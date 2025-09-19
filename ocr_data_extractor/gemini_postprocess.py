# ocr_data_extractor/gemini_postprocess.py
# (UNCHANGED — pasted here for completeness)
import os
import json
import time
from datetime import datetime, timezone, timedelta
import google.generativeai as genai
import yaml
from dotenv import load_dotenv

DEFAULT_MODEL = "gemini-2.5-pro"
MAX_RETRIES = 5

def load_config(path: str) -> dict:
    """Load config.yaml for model settings only"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg

def load_env_vars():
    """Load environment variables from .env file"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return api_key

def now_iso_ist() -> str:
    """Get current IST timestamp in ISO format"""
    ist_timezone = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist_timezone).replace(microsecond=0).isoformat()

def coerce_output(data: dict, image_url: str) -> dict:
    def pick(d, k, default=None):
        return d[k] if isinstance(d, dict) and k in d and d[k] not in ("", []) else default

    out = {}
    out["product_title"] = pick(data, "product_title", None)
    out["image_url"] = image_url
    out["status"] = None
    out["created_at"] = now_iso_ist()
    out["updated_at"] = now_iso_ist()

    ocr_in = data.get("ocr_data", {}) if isinstance(data.get("ocr_data"), dict) else {}

    manufacturer = (
        ocr_in.get("manufacturer")
        or ocr_in.get("name_of_the_manufacturer")
        or ocr_in.get("packer")
        or None
    )
    manufacturer_address = (
        ocr_in.get("manufacturer_address")
        or ocr_in.get("address_of_manufacturer")
        or None
    )

    ocr_out = {
        "manufacturer": manufacturer,
        "manufacturer_address": manufacturer_address,
        "country_of_origin": ocr_in.get("country_of_origin"),
        "common_product_name": ocr_in.get("common_product_name"),
        "net_quantity": ocr_in.get("net_quantity"),
        "mrp": ocr_in.get("mrp"),
        "unit_sale_price": ocr_in.get("unit_sale_price"),
        "date_of_manufacture": ocr_in.get("date_of_manufacture"),
        "best_before": ocr_in.get("best_before"),
        "raw_ocr_text": ocr_in.get("raw_ocr_text"),
    }
    out["ocr_data"] = ocr_out

    compliance_in = data.get("compliance", {}) if isinstance(data.get("compliance"), dict) else {}
    out["compliance"] = {
        "score": pick(compliance_in, "score", None),
        "status": pick(compliance_in, "status", None),
        "violations": pick(compliance_in, "violations", []),
        "reasoning": pick(compliance_in, "reasoning", None),
        "analysis_timestamp": pick(compliance_in, "analysis_timestamp", now_iso_ist()),
    }
    return out

def build_prompt(raw_text: str, image_url: str) -> str:
    return f"""
You are a strict JSON extractor. Return ONLY valid JSON (no markdown, no prose).
We provide OCR text from Google Document AI for one packaged food product.
Extract fields exactly as shown. If a field is missing in the source, set it to null. Do not hallucinate.
The violations array can be empty if no violations are found or can be multiple too. 
Do not upload any complaince details or analysis timestamp. they all should be none they will be updated after. 

Required JSON shape (keys and nesting must match EXACTLY):
{{
  "product_title": "example product title",
  "image_url": "{image_url}",
  "status": null,
  "created_at": "date and time in ist",
  "updated_at": "sate and time in ist",
  
  "ocr_data": {{
    "manufacturer": null,
    "manufacturer_address": null,
    "country_of_origin": null,
    "common_product_name": null,
    "net_quantity": null,
    "mrp": null,
    "unit_sale_price": null,
    "date_of_manufacture": null,
    "best_before": null,
    "raw_ocr_text": null
  }},
  
  "compliance": {{
    "score": null,
    "status": null,
    "violations": [{{
      "field": "string",
      "issue": "string",
      "rule_reference": "Rule section",
      "reason": "string"
    }}
    ],
    "reasoning": "string",
    "analysis_timestamp": "string(null for now)"
  }}
}}

IMPORTANT FIELD MAPPING:
- manufacturer: Use "name_of_the_manufacturer", "packer", or "manufacturer" from OCR
- manufacturer_address: Use "address_of_manufacturer" from OCR
- raw_ocr_text: Include the full original OCR text

SOURCE OCR (verbatim):
{raw_text}
"""

def validate_json_structure(data: dict) -> bool:
    required_top_keys = ["product_title", "image_url", "status", "created_at", "updated_at", "ocr_data", "compliance"]
    required_ocr_keys = ["manufacturer", "manufacturer_address", "country_of_origin", "common_product_name", 
                         "net_quantity", "mrp", "unit_sale_price", "date_of_manufacture", "best_before", "raw_ocr_text"]
    required_compliance_keys = ["score", "status", "violations", "reasoning", "analysis_timestamp"]
    if not all(k in data for k in required_top_keys): return False
    if not isinstance(data.get("ocr_data"), dict): return False
    if not all(k in data["ocr_data"] for k in required_ocr_keys): return False
    if not isinstance(data.get("compliance"), dict): return False
    if not all(k in data["compliance"] for k in required_compliance_keys): return False
    return True

def call_gemini_with_retry(api_key: str, model_name: str, prompt: str, max_retries: int = 5) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=(
            "You are a JSON-only extractor. Always return only JSON. "
            "No explanations, no markdown, no backticks. "
            "Follow the exact JSON structure provided in the prompt."
        ),
        generation_config={"temperature": 0.0, "response_mime_type": "application/json"},
    )
    for attempt in range(max_retries):
        try:
            print(f"Gemini API call attempt {attempt + 1}/{max_retries}")
            resp = model.generate_content(prompt)
            text = resp.candidates[0].content.parts[0].text
            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                first, last = text.find("{"), text.rfind("}")
                if first != -1 and last != -1 and last > first:
                    result = json.loads(text[first:last+1])
                else:
                    raise
            if validate_json_structure(result):
                print(f"Valid JSON structure received on attempt {attempt + 1}")
                return result
            print(f"Invalid JSON structure on attempt {attempt + 1}, retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            time.sleep(2)
    raise RuntimeError(f"Failed to get valid JSON structure after {max_retries} attempts")

def process_ocr_to_json(config_path: str, ocr_text: str, image_url: str) -> dict:
    api_key = load_env_vars()
    cfg = load_config(config_path)
    model_name = cfg.get("gemini", {}).get("model", "gemini-2.5-pro")
    print(f"Using Gemini model: {model_name}")
    prompt = build_prompt(ocr_text, image_url)
    gemini_obj = call_gemini_with_retry(api_key, model_name, prompt)
    return coerce_output(gemini_obj, image_url)
