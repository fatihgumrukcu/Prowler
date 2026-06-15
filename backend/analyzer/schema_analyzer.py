import json
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models import Check

# Required fields per @type. Values are (field_path, human label) tuples.
# field_path supports dot-notation for nested keys, e.g. "offers.price"
_REQUIRED_FIELDS: Dict[str, List[tuple]] = {
    "WebSite":        [("name", "name"), ("url", "url")],
    "WebPage":        [("name", "name"), ("url", "url")],
    "Article":        [("headline", "headline"), ("author", "author"), ("datePublished", "datePublished"), ("image", "image")],
    "BlogPosting":    [("headline", "headline"), ("author", "author"), ("datePublished", "datePublished"), ("image", "image")],
    "NewsArticle":    [("headline", "headline"), ("author", "author"), ("datePublished", "datePublished"), ("image", "image")],
    "Product":        [("name", "name"), ("offers", "offers")],
    "BreadcrumbList": [("itemListElement", "itemListElement")],
    "FAQPage":        [("mainEntity", "mainEntity")],
    "HowTo":          [("name", "name"), ("step", "step")],
    "Recipe":         [("name", "name"), ("recipeIngredient", "recipeIngredient"), ("recipeInstructions", "recipeInstructions")],
    "Organization":   [("name", "name"), ("url", "url")],
    "LocalBusiness":  [("name", "name"), ("address", "address"), ("url", "url")],
    "Person":         [("name", "name")],
    "Event":          [("name", "name"), ("startDate", "startDate"), ("location", "location")],
    "JobPosting":     [("title", "title"), ("hiringOrganization", "hiringOrganization"), ("jobLocation", "jobLocation"), ("datePosted", "datePosted")],
    "Review":         [("itemReviewed", "itemReviewed"), ("reviewRating", "reviewRating"), ("author", "author")],
    "VideoObject":    [("name", "name"), ("description", "description"), ("thumbnailUrl", "thumbnailUrl"), ("uploadDate", "uploadDate")],
    "SoftwareApplication": [("name", "name"), ("operatingSystem", "operatingSystem"), ("applicationCategory", "applicationCategory")],
}


def _extract_types(data: Any) -> List[str]:
    types = []
    if isinstance(data, list):
        for item in data:
            types.extend(_extract_types(item))
    elif isinstance(data, dict):
        if "@type" in data:
            t = data["@type"]
            types.extend(t if isinstance(t, list) else [t])
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                types.extend(_extract_types(item))
    return types


def _get_nested(obj: dict, path: str) -> Any:
    """Resolve a dot-notation path in a dict. Returns None if missing."""
    parts = path.split(".")
    cur = obj
    for part in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _check_entity(entity: dict) -> List[Check]:
    """Validate a single schema entity against known required-field rules."""
    checks = []
    raw_type = entity.get("@type")
    if not raw_type:
        return checks

    types = raw_type if isinstance(raw_type, list) else [raw_type]

    for schema_type in types:
        required = _REQUIRED_FIELDS.get(schema_type)
        if not required:
            continue

        missing = []
        for field_path, label in required:
            value = _get_nested(entity, field_path)
            # Treat empty string, empty list, empty dict as missing
            if value is None or value == "" or value == [] or value == {}:
                missing.append(label)

        if missing:
            checks.append(Check(
                id=f"schema_{schema_type.lower()}_fields",
                category="Schema",
                label=f"{schema_type}: Zorunlu Alanlar",
                status="warning",
                message=f"{schema_type} schema'sında eksik alanlar: {', '.join(missing)}",
                value=schema_type,
                recommendation=f"Şu alanları ekleyin: {', '.join(missing)}",
            ))
        else:
            checks.append(Check(
                id=f"schema_{schema_type.lower()}_fields",
                category="Schema",
                label=f"{schema_type}: Zorunlu Alanlar",
                status="passed",
                message=f"{schema_type} zorunlu alanların tümü mevcut",
                value=schema_type,
            ))

    return checks


def _walk_entities(data: Any) -> List[dict]:
    """Recursively collect all schema entities from parsed JSON-LD."""
    entities = []
    if isinstance(data, list):
        for item in data:
            entities.extend(_walk_entities(item))
    elif isinstance(data, dict):
        if "@type" in data:
            entities.append(data)
        if "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                entities.extend(_walk_entities(item))
    return entities


def analyze_schema(soup: BeautifulSoup) -> List[Check]:
    checks = []
    script_tags = soup.find_all("script", type="application/ld+json")

    if not script_tags:
        checks.append(Check(
            id="schema_json_ld",
            category="Schema",
            label="JSON-LD Yapılandırılmış Veri",
            status="warning",
            message="Sayfada JSON-LD yapılandırılmış verisi bulunamadı",
            recommendation="İçeriğinizi arama motorlarına tanıtmak için JSON-LD schema ekleyin",
        ))
        return checks

    all_entities: List[dict] = []
    all_types: List[str] = []
    parse_errors = 0

    for tag in script_tags:
        try:
            data = json.loads(tag.string or "")
            all_entities.extend(_walk_entities(data))
            all_types.extend(_extract_types(data))
        except (json.JSONDecodeError, TypeError):
            parse_errors += 1

    # 1. JSON-LD varlığı + parse durumu
    if parse_errors > 0 and not all_types:
        checks.append(Check(
            id="schema_json_ld",
            category="Schema",
            label="JSON-LD Yapılandırılmış Veri",
            status="warning",
            message=f"JSON-LD bulundu ancak parse edilemedi ({parse_errors} hata)",
            recommendation="JSON-LD sözdizimi hatalarını düzeltin",
        ))
        return checks
    elif parse_errors > 0:
        checks.append(Check(
            id="schema_json_ld",
            category="Schema",
            label="JSON-LD Yapılandırılmış Veri",
            status="warning",
            message=f"JSON-LD kısmen parse edildi; {parse_errors} blokta hata var",
            value=", ".join(all_types),
            recommendation="JSON-LD sözdizimi hatalarını düzeltin",
        ))
    else:
        checks.append(Check(
            id="schema_json_ld",
            category="Schema",
            label="JSON-LD Yapılandırılmış Veri",
            status="passed",
            message=f"{len(script_tags)} JSON-LD bloğu bulundu",
            value=", ".join(dict.fromkeys(all_types)) if all_types else "mevcut (@type yok)",
        ))

    # 2. Her entity için zorunlu alan kontrolü
    seen_types: set = set()
    for entity in all_entities:
        raw_type = entity.get("@type")
        types = raw_type if isinstance(raw_type, list) else [raw_type]
        for t in types:
            if t in seen_types:
                continue
            seen_types.add(t)
        entity_checks = _check_entity(entity)
        checks.extend(entity_checks)

    return checks


def get_schema_metadata(soup: BeautifulSoup) -> Dict:
    script_tags = soup.find_all("script", type="application/ld+json")
    types: List[str] = []
    for tag in script_tags:
        try:
            data = json.loads(tag.string or "")
            types.extend(_extract_types(data))
        except (json.JSONDecodeError, TypeError):
            pass
    return {"schema_types": types}
