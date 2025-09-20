# ocr_data_extractor/image_processor.py
import requests, json
from pathlib import Path
from typing import List, Tuple
from ocr_data_extractor.image_parser import extract_ocr_text

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def _detect_mime(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".pdf": "application/pdf", ".tif": "image/tiff", ".tiff": "image/tiff",
    }.get(ext, "image/jpeg")

def download_images(image_urls: List[str]) -> List[str]:
    local_paths: List[str] = []
    for i, url in enumerate(image_urls, start=1):
        suffix = Path(url).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".pdf", ".tif", ".tiff"}:
            suffix = ".jpg"
        path = TEMP_DIR / f"img{i}{suffix}"
        print(f"[download] {url} -> {path}")
        r = requests.get(url, stream=True, timeout=40); r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        local_paths.append(str(path))
    return local_paths

def run_document_and_form_parsing(config_path: str, image_paths: List[str],
                                  output_txt_path: str = str(TEMP_DIR / "ocr_output.txt"),
                                  output_json_path: str = str(TEMP_DIR / "ocr_output.json")) -> Tuple[str, str]:
    all_lines = []
    records = []
    for idx, p in enumerate(image_paths, start=1):
        mime = _detect_mime(p)
        print(f"[parse] ({idx}/{len(image_paths)}) {p} (mime={mime})")
        part_path = TEMP_DIR / f"ocr_part_{idx}.txt"
        text = extract_ocr_text(config_path, p, mime, str(part_path))
        all_lines.append(f"===== IMAGE {idx}: {p} =====\n{text}\n")
        records.append({"index": idx, "path": p, "text": text})

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump({"images": records}, f, ensure_ascii=False, indent=2)

    print(f"[image_processor] ✅ OCR text:  {Path(output_txt_path).resolve()}")
    print(f"[image_processor] ✅ OCR JSON:  {Path(output_json_path).resolve()}")
    return output_txt_path, output_json_path

def process_images_to_ocr(config_path: str, image_urls: List[str],
                          output_txt_path: str = str(TEMP_DIR / "ocr_output.txt")) -> Tuple[List[str], str, str]:
    if not image_urls:
        raise ValueError("No image URLs provided to image_processor")
    local_paths = download_images(image_urls)
    txt_path, json_path = run_document_and_form_parsing(config_path, local_paths, output_txt_path)
    return local_paths, txt_path, json_path
