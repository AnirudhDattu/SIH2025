# ocr_data_extractor/update_mongodb.py
import os
import json
from datetime import datetime, timezone
from typing import Any, Dict

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

load_dotenv()

def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key, default)
    if v and len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
    return v

def _get_client() -> MongoClient:
    uri = _env("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI not set in environment (.env).")
    return MongoClient(uri, server_api=ServerApi("1"))

def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_existing_product(json_path: str, object_id: str) -> dict:
    """
    Reads JSON from disk and $sets it into the existing document with the given _id.
    Also sets status='ocr_uploaded' and updated_at to now.
    """
    db_name = _env("MONGODB_DB", "productdb") or "productdb"
    collection_name = _env("MONGODB_COLLECTION", "products") or "products"

    client = _get_client()
    db = client[db_name]
    collection = db[collection_name]

    try:
        oid = ObjectId(object_id)
    except Exception as e:
        raise ValueError(f"Invalid ObjectId: {object_id}") from e

    payload = _read_json(json_path)

    # Ensure top-level timestamps & status
    payload.setdefault("created_at", _utc_now())
    payload["updated_at"] = _utc_now()
    # We'll set status explicitly below as 'ocr_uploaded'

    # Merge: $set the payload fields at top level
    # (If you want to only set specific subfields, narrow this dict)
    update_doc = {
        "$set": payload | {"status": "OCR UPLOADED", "updated_at": _utc_now()}
    }

    res = collection.update_one({"_id": oid}, update_doc)
    if res.matched_count == 0:
        return {"status": "error", "reason": "object_not_found", "object_id": object_id}

    return {
        "status": "ok",
        "action": "updated",
        "object_id": object_id,
        "db": db_name,
        "collection": collection_name,
        "final_status": "ocr_uploaded",
        "modified_count": res.modified_count,
        "matched_count": res.matched_count,
    }
