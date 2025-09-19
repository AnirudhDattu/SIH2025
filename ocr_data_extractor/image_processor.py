# ocr_data_extractor/image_processor.py
import os
import io
import time
import requests
from pathlib import Path
from typing import List, Tuple

from .image_parser import extract_ocr_text  # same module you already have

# Where temp images & OCR output live relative to current working dir
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def _detect_mime(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".pdf": "application/pdf",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }.get(ext, "image/jpeg")

def download_images(image_urls: List[str]) -> List[str]:
    """
    Downloads each image URL to temp/img{n}.<ext> and returns the local file paths in order.
    Names: img1, img2, ...
    """
    local_paths: List[str] = []
    for i, url in enumerate(image_urls, start=1):
        # infer extension from URL path; default .jpg if unknown
        filename = f"img{i}"
        suffix = Path(url).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".pdf", ".tif", ".tiff"}:
            suffix = ".jpg"
        local_path = TEMP_DIR / f"{filename}{suffix}"

        print(f"[download] {url} -> {local_path}")
        resp = requests.get(url, stream=True, timeout=40)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        local_paths.append(str(local_path))
    return local_paths

def run_document_and_form_parsing(
    config_path: str,
    image_paths: List[str],
    output_txt_path: str = str(TEMP_DIR / "ocr_output.txt")
) -> str:
    """
    Runs Document Parser + Form Parser for each image and writes a single combined ocr_output.txt.
    Returns the final output path (absolute).
    """
    out_lines: List[str] = []
    for idx, p in enumerate(image_paths, start=1):
        mime = _detect_mime(p)
        print(f"[parse] ({idx}/{len(image_paths)}) {p} (mime={mime})")
        # We call your existing extract_ocr_text which:
        # - sets GCP credentials from config
        # - runs both Document Parser and Form Parser
        # - writes the combined output to the path we pass
        # To keep one file, we collect text in memory and write once at end.
        temp_out = TEMP_DIR / f"ocr_part_{idx}.txt"
        text = extract_ocr_text(config_path, p, mime, str(temp_out))
        out_lines.append(f"===== IMAGE {idx}: {p} =====\n{text}\n")

    final_text = "\n".join(out_lines)
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    abs_path = str(Path(output_txt_path).resolve())
    print(f"[image_processor] ✅ Combined OCR written to {abs_path}")
    return abs_path

def process_images_to_ocr(
    config_path: str,
    image_urls: List[str],
    output_txt_path: str = "ocr_output.txt"
) -> Tuple[List[str], str]:
    """
    1) Downloads all images to ./temp/img1..imgN
    2) Runs document+form parsing for all
    3) Returns (local_image_paths, final_ocr_txt_path)
    """
    if not image_urls:
        raise ValueError("No image URLs provided to image_processor")

    local_paths = download_images(image_urls)
    final_txt_path = run_document_and_form_parsing(config_path, local_paths, output_txt_path)
    return local_paths, final_txt_path
