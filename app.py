import os
import re
import sys
import shutil
import subprocess
import threading
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

SITE_CSV = {
    "kazimalic": "data/output/kazimalic_products.csv",
    "istockina":  "data/output/istockina_products.csv",
}
SITE_PREV_CSV = {
    "kazimalic": "data/output/kazimalic_prev.csv",
    "istockina":  "data/output/istockina_prev.csv",
}
VALID_SITES = {"kazimalic", "istockina"}

# ── Scraper state ──────────────────────────────────────────────────────────────
_state_lock = threading.Lock()
_scraper_state = {
    "kazimalic": {
        "status": "idle",
        "last_run_time": None,
        "total_products": 0,
        "error_message": "",
        "new_urls": [],
        "price_changed": {},
    },
    "istockina": {
        "status": "idle",
        "last_run_time": None,
        "total_products": 0,
        "error_message": "",
        "new_urls": [],
        "price_changed": {},
    },
}


def _get_state(site):
    with _state_lock:
        return dict(_scraper_state[site])


def _set_state(site, **kwargs):
    with _state_lock:
        _scraper_state[site].update(kwargs)


# ── Price helpers ──────────────────────────────────────────────────────────────
def clean_price(raw):
    if not isinstance(raw, str):
        return raw
    match = re.search(r"[\d.,]+\s*₺", raw)
    return match.group(0).strip() if match else raw


# ── CSV helpers ────────────────────────────────────────────────────────────────
def _snapshot_csv(site):
    csv_path = SITE_CSV[site]
    prev_path = SITE_PREV_CSV[site]
    if os.path.exists(csv_path):
        shutil.copy2(csv_path, prev_path)


def _compare_snapshots(site):
    csv_path = SITE_CSV[site]
    prev_path = SITE_PREV_CSV[site]
    if not os.path.exists(prev_path) or not os.path.exists(csv_path):
        return set(), {}
    try:
        old_df = pd.read_csv(prev_path, encoding="utf-8")
        new_df = pd.read_csv(csv_path,  encoding="utf-8")
    except Exception:
        return set(), {}

    required = {"product_url", "price"}
    if not required.issubset(old_df.columns) or not required.issubset(new_df.columns):
        return set(), {}

    old_df["price"] = old_df["price"].apply(clean_price)
    new_df["price"] = new_df["price"].apply(clean_price)

    old_map = dict(zip(old_df["product_url"], old_df["price"]))
    new_map = dict(zip(new_df["product_url"], new_df["price"]))

    new_urls = set(new_map.keys()) - set(old_map.keys())
    price_changed = {
        url: old_map[url]
        for url in new_map
        if url in old_map and old_map[url] != new_map[url]
    }

    return new_urls, price_changed


def load_products(site):
    csv_path = SITE_CSV[site]
    if not os.path.exists(csv_path):
        return [], []
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except Exception:
        return [], []

    required = {"product_name", "price", "product_url", "image_url", "category_name"}
    if not required.issubset(df.columns):
        return [], []

    df = df.where(pd.notnull(df), None)
    df["price"] = df["price"].apply(clean_price)

    state         = _get_state(site)
    new_urls_set  = set(state.get("new_urls", []))
    price_changed = state.get("price_changed", {})

    products = df.to_dict(orient="records")
    for p in products:
        url = p.get("product_url") or ""
        if url in new_urls_set:
            p["_tag"]       = "new"
            p["_old_price"] = None
        elif url in price_changed:
            p["_tag"]       = "price_changed"
            p["_old_price"] = price_changed[url]
        else:
            p["_tag"]       = ""
            p["_old_price"] = None

    categories = sorted(df["category_name"].dropna().unique().tolist())
    return products, categories


# ── Background scraper runner ──────────────────────────────────────────────────
def _run_scraper_bg(site):
    _set_state(site, status="running", error_message="")
    _snapshot_csv(site)
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "src.main", f"--site={site}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = proc.communicate()

        if proc.returncode == 0:
            new_urls, price_changed = _compare_snapshots(site)
            products, _ = load_products(site)
            _set_state(
                site,
                status="completed",
                last_run_time=datetime.now().isoformat(timespec="seconds"),
                total_products=len(products),
                new_urls=list(new_urls),
                price_changed=price_changed,
            )
        else:
            _set_state(
                site,
                status="error",
                last_run_time=datetime.now().isoformat(timespec="seconds"),
                error_message=stderr.decode("utf-8", errors="replace").strip(),
            )
    except Exception as exc:
        _set_state(
            site,
            status="error",
            last_run_time=datetime.now().isoformat(timespec="seconds"),
            error_message=str(exc),
        )


# ── Routes ─────────────────────────────────────────────────────────────────────
def _resolve_site():
    site = request.args.get("site", "kazimalic")
    return site if site in VALID_SITES else "kazimalic"


@app.route("/")
def index():
    site = _resolve_site()
    products, categories = load_products(site)
    state = _get_state(site)
    _set_state(site, total_products=len(products))
    return render_template(
        "index.html",
        products=products,
        categories=categories,
        total=len(products),
        scraper_status=state["status"],
        new_count=len(state.get("new_urls", [])),
        price_changed_count=len(state.get("price_changed", {})),
        current_site=site,
    )


@app.route("/status")
def status():
    site = _resolve_site()
    state = _get_state(site)
    return jsonify({
        "status":              state["status"],
        "last_run_time":       state["last_run_time"],
        "total_products":      state["total_products"],
        "error_message":       state["error_message"],
        "new_count":           len(state.get("new_urls", [])),
        "price_changed_count": len(state.get("price_changed", {})),
    })


@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    site = _resolve_site()
    state = _get_state(site)
    if state["status"] == "running":
        return jsonify({"status": "running", "message": "Scraper zaten çalışıyor"}), 409
    t = threading.Thread(target=_run_scraper_bg, args=(site,), daemon=True)
    t.start()
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
