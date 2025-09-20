# rag/rag.py
# -- coding: utf-8 --
import os, torch
import json 
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------
# 1) Build / load vector DB from rules PDF
# -------------------------------
def build_vector_db(pdf_path, persist_dir="./rules_chroma_store"):
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma.vectorstores import Chroma

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name="legal-metrology-col"
    )
    return vector_db

def load_vector_db(persist_dir="./rules_chroma_store"):
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma.vectorstores import Chroma
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(
        persist_directory=persist_dir,
        collection_name="legal-metrology-col",
        embedding_function=embeddings
    )

# -------------------------------
# 2) BERT reranker
# -------------------------------
_reranker_model = "amberoad/bert-multilingual-passage-reranking-msmarco"
_reranker_tokenizer = AutoTokenizer.from_pretrained(_reranker_model)
_reranker = AutoModelForSequenceClassification.from_pretrained(_reranker_model)

def _score(query, passage):
    inputs = _reranker_tokenizer(query, passage, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = _reranker(**inputs)
    return outputs.logits[0, 1].item()

def rerank_documents(query, docs, top_k=6):
    scored = [(_score(query, d.page_content), d) for d in docs]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored[:top_k]]

# -------------------------------
# 3) Compliance check (returns JSON; no DB writes)
# -------------------------------
def check_compliance(vector_db, product: dict) -> dict:
    violations = []

    # Quick pre-check on MRP containing units instead of currency
    mrp = (product.get("mrp") or "")
    if isinstance(mrp, str) and re.search(r"\b(kg|g|ml|l|litre|meter|cm)\b", mrp.lower()):
        violations.append({
            "field": "mrp",
            "issue": "MRP value contains a unit (e.g., kg/g/ml) instead of currency.",
            "rule_reference": "Rule on Maximum Retail Price display",
            "reason": "MRP should represent a monetary amount (e.g., Rs. 50.00); found measurement units."
        })

    # Vector search + rerank
    query = json.dumps(product, ensure_ascii=False, indent=2)
    retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 20, "fetch_k": 30, "lambda_mult": 0.6})
    docs = retriever.invoke(query)
    if not docs:
        return {
            "compliance_status": "error",
            "violations": violations,
            "reasoning": "No matching rules retrieved for validation."
        }

    reranked = rerank_documents(query, docs, top_k=6)
    context_text = "\n\n".join(d.page_content for d in reranked)

    prompt = f"""
You are a meticulous compliance officer for the Legal Metrology Act (Packaged Commodities Rules, 2011).
Validate the PRODUCT DATA against the CONTEXT (rules) and return ONLY valid JSON.

CONTEXT:
{context_text}

PRODUCT DATA:
{query}

INSTRUCTIONS:
1. Output ONLY valid JSON (no commentary, no code blocks).
2. If all fields are compliant:
    - "compliance_status": "compliant"
    - "violations": []
    - "reasoning": "The product information fully complies with the rules in the given context."
3. If there are violations:
    - Include them in "violations" with:
      "field", "issue", "rule_reference", and "reason".
4. Do not invent violations not present in PRODUCT DATA.
5. General Rule: Any field with an empty string ("") is a violation.

SPECIAL RULES:
- country_of_origin: If "India"/"INDIA", importer details are NOT required.
- imported_by: Mandatory ONLY if country_of_origin is not India.
- date_of_manufacture: allow "MM/YYYY", "YYYY-MM-DD", "YYYY/M/D".
- net_quantity:
    - number + valid unit (g, kg, ml, l, litre, meter, cm, pcs, pack, tablet, capsule).
    - If missing → violation.
    - If contains currency units (Rs, INR, ₹, $) → wrong type.
- mrp:
    - must be monetary (Rs/INR/₹/$).
    - If missing → violation.
    - If measurement units present → wrong type.

OUTPUT FORMAT (strict JSON):
{{
  "compliance_status": "compliant" | "non-compliant" | "error",
  "compliance_score": "percentage or short summary",
  "violations": [
    {{
      "field": "string",
      "issue": "string",
      "rule_reference": "Rule section",
      "reason": "string"
    }}
  ],
  "reasoning": "string"
}}
"""
    resp = gemini_model.generate_content(prompt)
    raw = resp.text
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    s = m.group(0) if m else raw.strip()
    try:
        out = json.loads(s)
    except json.JSONDecodeError:
        return {
            "compliance_status": "error",
            "violations": violations,
            "reasoning": "Gemini response malformed; could not parse JSON."
        }

    if violations:
        out.setdefault("violations", []).extend(violations)
        if out.get("compliance_status") == "compliant":
            out["compliance_status"] = "non-compliant"
    if "reasoning" not in out:
        out["reasoning"] = "Auto-generated reasoning based on rule context and product data."
    return out
