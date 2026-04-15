import os
import re
import sys
import subprocess
import threading
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)

CSV_PATH = "data/output/products.csv"

# ── Scraper state ──────────────────────────────────────────────────────────────
_state_lock = threading.Lock()
_scraper_state = {
    "status": "idle",          # idle | running | completed | error
    "last_run_time": None,     # ISO-8601 string
    "total_products": 0,
    "error_message": "",
}


def _get_state():
    with _state_lock:
        return dict(_scraper_state)


def _set_state(**kwargs):
    with _state_lock:
        _scraper_state.update(kwargs)


# ── Helpers ────────────────────────────────────────────────────────────────────
def clean_price(raw):
    if not isinstance(raw, str):
        return raw
    match = re.search(r"[\d.,]+\s*₺", raw)
    if match:
        return match.group(0).strip()
    return raw


def load_products():
    if not os.path.exists(CSV_PATH):
        return [], []
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8")
    except Exception:
        return [], []
    required = {"product_name", "price", "product_url", "image_url", "category_name"}
    if not required.issubset(df.columns):
        return [], []
    df = df.where(pd.notnull(df), None)
    df["price"] = df["price"].apply(clean_price)
    products = df.to_dict(orient="records")
    categories = sorted(df["category_name"].dropna().unique().tolist())
    return products, categories


def _count_products():
    products, _ = load_products()
    return len(products)


# ── Background scraper runner ──────────────────────────────────────────────────
def _run_scraper_bg():
    _set_state(status="running", error_message="")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "src.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = proc.communicate()
        if proc.returncode == 0:
            total = _count_products()
            _set_state(
                status="completed",
                last_run_time=datetime.now().isoformat(timespec="seconds"),
                total_products=total,
            )
        else:
            _set_state(
                status="error",
                last_run_time=datetime.now().isoformat(timespec="seconds"),
                error_message=stderr.decode("utf-8", errors="replace").strip(),
            )
    except Exception as exc:
        _set_state(
            status="error",
            last_run_time=datetime.now().isoformat(timespec="seconds"),
            error_message=str(exc),
        )


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    products, categories = load_products()
    state = _get_state()
    _set_state(total_products=len(products))
    return render_template(
        "index.html",
        products=products,
        categories=categories,
        total=len(products),
        scraper_status=state["status"],
    )


@app.route("/status")
def status():
    state = _get_state()
    return jsonify({
        "status": state["status"],
        "last_run_time": state["last_run_time"],
        "total_products": state["total_products"],
        "error_message": state["error_message"],
    })


@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    state = _get_state()
    if state["status"] == "running":
        return jsonify({"status": "running", "message": "Scraper zaten çalışıyor"}), 409
    t = threading.Thread(target=_run_scraper_bg, daemon=True)
    t.start()
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
