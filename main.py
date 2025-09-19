# main.py
import os
import yaml
from dotenv import load_dotenv
from typing import List
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from pathlib import Path

os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

# Load env first
load_dotenv()

# 1) scraper step: import your function from the path you’re using
#    If your package is named "complaince_checker" (typo) keep that import.
from scraper.scrape_upload_data import run_pipeline as run_scraper_pipeline

# 2) OCR + postprocess modules (from ocr_data_extractor/)
from ocr_data_extractor.image_processor import process_images_to_ocr
from ocr_data_extractor.gemini_postprocess import process_ocr_to_json
from ocr_data_extractor.update_mongodb import update_existing_product

CONFIG_FILE = "config.yaml"

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

OCR_OUTPUT_TXT = str(TEMP_DIR / "ocr_output.txt")
PRODUCT_OUTPUT_JSON = str(TEMP_DIR / "product_output.json")

def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key, default)
    if v and len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
    return v

def read_url_from_config(cfg_path: str = "config.yaml") -> str:
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    url = cfg.get("url")
    if not url or not isinstance(url, str):
        raise SystemExit("config.yaml must contain a string key 'url'.")
    return url

def get_mongo_doc(object_id: str) -> dict:
    """Fetch the existing MongoDB document to get image_urls."""
    uri = _env("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is not set in env (.env).")

    db_name = _env("MONGODB_DB", "productdb") or "productdb"
    coll_name = _env("MONGODB_COLLECTION", "products") or "products"

    client = MongoClient(uri, server_api=ServerApi("1"))
    doc = client[db_name][coll_name].find_one({"_id": ObjectId(object_id)})
    if not doc:
        raise SystemExit(f"No document found for _id={object_id}")
    return doc

def main():
    print("=" * 60)
    print("SCRAPE ➜ OCR (all images) ➜ GEMINI ➜ UPDATE Mongo")
    print("=" * 60)

    # A) Read URL from config.yaml only
    url = read_url_from_config(CONFIG_FILE)
    print(f"[main] Using URL: {url}")

    # B) Run the scraper (inserts initial product doc with image_urls into mongoDB)
    print("[main] Running scraper to create initial Mongo doc...")
    object_id = run_scraper_pipeline(url)
    object_id = str(object_id)  # ensure string
    print(f"[main] Mongo _id: {object_id}")

    # C) Pull the doc back to get image_urls
    print("[main] Fetching document to get image_urls...")
    doc = get_mongo_doc(object_id)
    image_urls: List[str] = doc.get("image_urls") or []
    if not image_urls:
        raise SystemExit("No image_urls found in Mongo document; nothing to OCR.")
    print(f"[main] Found {len(image_urls)} images")

    # D) Download all images + run Document & Form parsing on each
    print("[main] Running image processor (downloads + Document/Form Parser)...")
    _, ocr_txt_path = process_images_to_ocr(CONFIG_FILE, image_urls, OCR_OUTPUT_TXT)
    print(f"[main] OCR text consolidated at: {ocr_txt_path}")

    # E) Read OCR content & run Gemini post-processing to JSON
    print("[main] Running Gemini post-processing...")
    with open(ocr_txt_path, "r", encoding="utf-8") as f:
        ocr_text = f.read()
    # pass the first image URL to populate the JSON's image_url field
    first_image_url = image_urls[0]
    result_json = process_ocr_to_json(CONFIG_FILE, ocr_text, first_image_url)

    # F) Save product_output.json locally
    print("[main] Saving product_output.json...")
    import json
    with open(PRODUCT_OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    print(f"[main] Saved JSON at: {os.path.abspath(PRODUCT_OUTPUT_JSON)}")

    # G) Update the same MongoDB object with this JSON and set status=ocr_uploaded
    print("[main] Updating MongoDB existing document...")
    update_res = update_existing_product(PRODUCT_OUTPUT_JSON, object_id)
    print(f"[main] Update result: {update_res}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED ✅")
    print("=" * 60)

if __name__ == "__main__":
    main()
