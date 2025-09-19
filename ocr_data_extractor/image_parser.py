# image_parser.py
import os
from typing import Optional, List
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import yaml

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg

def set_credentials(creds_path: str) -> None:
    creds_abs = os.path.abspath(creds_path)
    if not os.path.exists(creds_abs):
        raise FileNotFoundError(f"credentials file not found: {creds_abs}")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_abs

def text_from_anchor(document: documentai.Document, text_anchor) -> str:
    if not text_anchor or not getattr(text_anchor, "text_segments", None):
        return ""
    parts: List[str] = []
    for seg in text_anchor.text_segments:
        start = int(seg.start_index) if seg.start_index is not None else 0
        end = int(seg.end_index) if seg.end_index is not None else 0
        parts.append(document.text[start:end])
    return "".join(parts).strip()

def run_processor(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    processor_version_id: Optional[str] = None,
) -> documentai.Document:
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    
    if processor_version_id:
        name = client.processor_version_path(project_id, location, processor_id, processor_version_id)
    else:
        name = client.processor_path(project_id, location, processor_id)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"input file not found: {os.path.abspath(file_path)}")
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    return result.document

def extract_ocr_text(config_path: str, image_path: str, mime_type: str, output_file: str ) -> str:
    """Main function to extract OCR text from image"""
    # Load config and set credentials
    cfg = load_config(config_path)
    set_credentials(cfg["gcp"]["credentials_path"])
    
    project_id = cfg["gcp"]["project_id"]
    location = cfg["gcp"]["location"]
    doc_parser_id = cfg["processors"]["document_parser_id"]
    form_parser_id = cfg["processors"]["form_parser_id"]
    doc_parser_ver = cfg["processors"].get("document_parser_version_id") or None
    form_parser_ver = cfg["processors"].get("form_parser_version_id") or None
    
    # Collect all OCR output
    output_lines = []
    
    # Run Document Parser
    print("Running Document Parser...")
    doc_doc = run_processor(project_id, location, doc_parser_id, image_path, mime_type, doc_parser_ver)
    
    output_lines.append("================ DOCUMENT PARSER OUTPUT ================")
    text = doc_doc.text or ""
    output_lines.append(text if text else "(No text)")
    output_lines.append(f"\n[Extracted {len(text)} characters total]")
    
    # Run Form Parser
    print("Running Form Parser...")
    form_doc = run_processor(project_id, location, form_parser_id, image_path, mime_type, form_parser_ver)
    
    output_lines.append("\n================ FORM PARSER OUTPUT (Key–Value Pairs) ================")
    kv_count = 0
    for page in form_doc.pages:
        for f in page.form_fields:
            key = text_from_anchor(form_doc, f.field_name.text_anchor) if f.field_name else ""
            val = text_from_anchor(form_doc, f.field_value.text_anchor) if f.field_value else ""
            output_lines.append(f"[Page {page.page_number}] {key} -> {val}")
            kv_count += 1
    
    if kv_count == 0:
        output_lines.append("(No form fields found)")
    
    output_lines.append("\n================ FORM PARSER OUTPUT (Tables) ================")
    tbl_count = 0
    for page in form_doc.pages:
        for t_idx, tbl in enumerate(page.tables, start=1):
            tbl_count += 1
            output_lines.append(f"\n-- Table {t_idx} on Page {page.page_number} --")
            if tbl.header_rows:
                output_lines.append("Header:")
                for row in tbl.header_rows:
                    output_lines.append(" | ".join([text_from_anchor(form_doc, cell.layout.text_anchor) for cell in row.cells]))
            if tbl.body_rows:
                output_lines.append("Body:")
                for row in tbl.body_rows:
                    output_lines.append(" | ".join([text_from_anchor(form_doc, cell.layout.text_anchor) for cell in row.cells]))
    
    if tbl_count == 0:
        output_lines.append("(No tables found)")
    
    # Combine
    final_text = "\n".join(output_lines)

    # Save into ocr_output.txt
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)
    print(f"\n✅ OCR output saved to {os.path.abspath(output_file)}")
    
    return final_text