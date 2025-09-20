# main.py
import os, json
import yaml
import time
import shutil
import threading
from pathlib import Path
from dotenv import load_dotenv
from typing import List
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# Optional: silence gRPC ALTS info logs
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

load_dotenv()

# ---- scraper: we ONLY read image URLs (no DB writes here) ----
# If your module path is different, adjust the import accordingly.
from scraper.scrape_upload_data import extract_image_urls

# ---- OCR + postprocess ----
from ocr_data_extractor.image_processor import process_images_to_ocr
from ocr_data_extractor.gemini_postprocess import process_ocr_to_json

# ---- RAG (we will hot-patch 're' on the module to avoid editing rag.py) ----
import rag.rag as rag
import re as _re
setattr(rag, "re", _re)          # force the module's global 're' to the real regex module

CONFIG_FILE = "config.yaml"
TEMP_DIR = Path("temp"); TEMP_DIR.mkdir(parents=True, exist_ok=True)
OCR_OUTPUT_TXT = str(TEMP_DIR / "ocr_output.txt")
PRODUCT_OUTPUT_JSON = str(TEMP_DIR / "product_output.json")
RULES_STORE_DEFAULT = "rag/rules_chroma_store"
RULES_PDF_DEFAULT = "rag/pdfs/Final-Book-Legal-Metrology-with-amendments.pdf"

def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key, default)
    if v and len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
    return v

def read_config(path: str = CONFIG_FILE) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def _get_mongo_collection():
    uri = _env("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI is not set in .env")
    db_name = _env("MONGODB_DB", "productdb") or "productdb"
    coll_name = _env("MONGODB_COLLECTION", "products") or "products"
    client = MongoClient(uri, server_api=ServerApi("1"))
    return client[db_name][coll_name]

def _resolve_rules_pdf(rules_pdf_cfg: str) -> Path:
    # Try a few reasonable locations to find the PDF
    candidates = [
        Path(rules_pdf_cfg),
        Path.cwd() / rules_pdf_cfg,
        Path(__file__).parent / rules_pdf_cfg,
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    tried = "\n  - ".join(str(p) for p in candidates)
    raise SystemExit(
        "Rules PDF not found. Update config.yaml: rules_pdf to a valid path.\n"
        f"Tried:\n  - {tried}"
    )

def cleanup_temp_folder(temp_dir: Path, delay_seconds: int = 30):
    """
    Deletes the temp folder after a specified delay.
    Runs in a separate thread to avoid blocking the main process.
    """
    def _cleanup():
        try:
            print(f"[cleanup] Waiting {delay_seconds} seconds before cleaning up temp folder...")
            time.sleep(delay_seconds)
            
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"[cleanup] ✅ Successfully deleted temp folder: {temp_dir}")
            else:
                print(f"[cleanup] ⚠️  Temp folder already deleted: {temp_dir}")
                
        except Exception as e:
            print(f"[cleanup] ❌ Error deleting temp folder: {e}")
    
    # Start cleanup in background thread
    cleanup_thread = threading.Thread(target=_cleanup, daemon=True)
    cleanup_thread.start()
    print(f"[main] 🧹 Scheduled temp folder cleanup in {delay_seconds} seconds")

def main():
    print("="*60)
    print("SCRAPE ➜ OCR ➜ GEMINI ➜ RAG COMPLIANCE ➜ FINAL DB WRITE (single write)")
    print("="*60)

    cfg = read_config()
    url = cfg.get("url")
    if not url:
        raise SystemExit("config.yaml must contain key: url")

    rules_pdf_cfg = cfg.get("rules_pdf", RULES_PDF_DEFAULT)
    rules_store = cfg.get("rules_chroma_store", RULES_STORE_DEFAULT)

    # A) Scrape image URLs (NO DB writes here)
    print("[main] Scraping image URLs…")
    image_urls: List[str] = extract_image_urls(url)
    if not image_urls:
        raise SystemExit("No images found to OCR.")
    print(f"[main] {len(image_urls)} image URLs found")

    # B) OCR all images → temp/ocr_output.txt (and a JSON file we will delete)
    print("[main] Running OCR on all images…")
    local_paths, ocr_txt_path, ocr_json_path = process_images_to_ocr(CONFIG_FILE, image_urls, OCR_OUTPUT_TXT)
    print(f"[main] OCR written: {ocr_txt_path} / {ocr_json_path}")

    # Remove the per-image OCR JSON artifact (as requested)
    try:
        p = Path(ocr_json_path)
        if p.exists():
            p.unlink()
            print(f"[main] Removed unused OCR JSON: {p}")
    except Exception as e:
        print(f"[main] (non-fatal) Could not remove OCR JSON: {e}")

    # C) Gemini post-processing → temp/product_output.json (initial version)
    print("[main] Running Gemini post-processing…")
    with open(ocr_txt_path, "r", encoding="utf-8") as f:
        ocr_text = f.read()
    product_json = process_ocr_to_json(CONFIG_FILE, ocr_text, image_urls[0])

    # D) Load/build rules vector DB & run RAG compliance (no edits to rag.py)
    print("[main] Loading rules vector DB…")
    rules_store_path = Path(rules_store)
    if rules_store_path.exists():
        vector_db = rag.load_vector_db(str(rules_store_path))
    else:
        rules_store_path.mkdir(parents=True, exist_ok=True)
        rules_pdf_path = _resolve_rules_pdf(rules_pdf_cfg)
        vector_db = rag.build_vector_db(str(rules_pdf_path), str(rules_store_path))

    print("[main] Running RAG compliance check…")
    # Extract only the ocr_data for compliance checking
    ocr_data_for_compliance = product_json.get("ocr_data", {})
    compliance = rag.check_compliance(vector_db, ocr_data_for_compliance)
    
    # Update the product_json with compliance results
    from datetime import datetime, timezone
    product_json["compliance"] = {
        "score": compliance.get("compliance_score", None),
        "status": compliance.get("compliance_status", None), 
        "violations": compliance.get("violations", []),
        "reasoning": compliance.get("reasoning", None),
        "analysis_timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    }

    # Save the complete product_output.json with compliance data
    with open(PRODUCT_OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(product_json, f, ensure_ascii=False, indent=2)
    print(f"[main] product_output.json (with compliance) -> {Path(PRODUCT_OUTPUT_JSON).resolve()}")

    # E) Single final DB write
    print("[main] Writing final document to MongoDB (single write)…")
    coll = _get_mongo_collection()
    final_doc = {
        "product_title": product_json.get("product_title"),
        "image_urls": image_urls,
        "product_url": url,
        "status": "ocr_uploaded",
        "created_at": product_json.get("created_at"),
        "updated_at": product_json.get("updated_at"),
        "ocr_data": product_json.get("ocr_data", {}),
        "compliance": product_json.get("compliance", {})  # Now uses the updated compliance data
    }
    res = coll.insert_one(final_doc)
    print(f"[main] ✅ Inserted final document _id: {res.inserted_id}")

    print("\n" + "="*60)
    print("PIPELINE COMPLETED ✅")
    print("="*60)
    
    # Schedule temp folder cleanup after 30 seconds
    cleanup_temp_folder(TEMP_DIR, delay_seconds=30)

if __name__ == "__main__":
    main()