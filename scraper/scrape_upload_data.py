import os
from datetime import datetime
from typing import List

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OBJECT_IDS_FILE = "scraper/object_ids.txt"


def _env(key: str, default: str | None = None) -> str | None:
    """
    Read env var and strip wrapping single/double quotes if present.
    This makes values like "mongodb+srv://..." work even if quoted in .env.
    """
    v = os.getenv(key, default)
    if v and len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
    return v


# --------------------------- Mongo Helpers ---------------------------

def get_mongo_collection():
    uri = _env("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set in environment (from .env).")
    db_name = _env("MONGODB_DB", "productdb") or "productdb"
    coll_name = _env("MONGODB_COLLECTION", "products") or "products"

    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    return db[coll_name]


# ------------------------- Selenium Helpers --------------------------

def build_chrome_driver():
    headless = (_env("SELENIUM_HEADLESS", "") or "").strip() == "1"
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


# ------------------------ Scraping Logic -----------------------------

def extract_image_urls(product_url: str) -> List[str]:
    driver = build_chrome_driver()
    image_urls: List[str] = []
    try:
        driver.get(product_url)
        wait = WebDriverWait(driver, 10)

        ul_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ZqtVYK"))
        )
        print("✅ Found the <ul> container.")

        li_elements = ul_element.find_elements(By.CSS_SELECTOR, "li.YGoYIP")
        print(f"✅ Found {len(li_elements)} <li> elements inside.")

        for li in li_elements:
            try:
                img_element = li.find_element(By.TAG_NAME, "img")
                src = img_element.get_attribute("src")
                high_res_src = src.replace('/128/128/', '/832/832/')
                image_urls.append(high_res_src)
                print(f"🖼 Extracted URL: {high_res_src}")
            except Exception as e:
                print(f"⚠️ Could not find an image in one li: {e}")
    finally:
        driver.quit()
    return image_urls


# --------------------- Document + DB helpers -------------------------

def build_product_document(product_url: str, image_urls: List[str]) -> dict:
    now = datetime.now().isoformat()
    return {
        "product_title": None,
        "image_urls": image_urls,
        "product_url": product_url,
        "status": None,
        "created_at": now,
        "updated_at": now,
        "ocr_data": {
            "manufacturer": None,
            "manufacturer_address": None,
            "country_of_origin": None,
            "common_product_name": None,
            "net_quantity": None,
            "mrp": None,
            "unit_sale_price": None,
            "date_of_manufacture": None,
            "best_before": None,
            "raw_ocr_text": None,
        },
        "compliance": {
            "score": None,
            "status": None,
            "violations": [],
            "reasoning": None,
            "analysis_timestamp": None
        }
    }


def append_object_id(oid_str: str):
    with open(OBJECT_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(oid_str + "\n")


# --------------------------- Main API ---------------------------

def scrape_and_store_images(product_url: str):
    collection = get_mongo_collection()
    image_urls = extract_image_urls(product_url)

    if not image_urls:
        print("⚠️ No images found.")
        return None

    document = build_product_document(product_url, image_urls)
    result = collection.insert_one(document)
    inserted_id = str(result.inserted_id)
    print(f"✅ Inserted into MongoDB with ID: {inserted_id}")

    append_object_id(inserted_id)
    print(f"🧾 Appended ID to {OBJECT_IDS_FILE}")

    return inserted_id


def run_pipeline(url: str):
    return scrape_and_store_images(url)
