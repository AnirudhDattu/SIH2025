# -- coding: utf-8 --
import os, json, re, torch
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# -------------------------------
# Load environment variables & configure Gemini
# -------------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------
# 1. Load PDF, Chunk & Embed
# -------------------------------
def build_vector_db(pdf_path, persist_dir="./rules_chroma_store"):
    """
    Builds or loads a vector database from a PDF file.
    """
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma.vectorstores import Chroma

    print("Building or loading vector database...")

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
    print("Vector database ready.")
    return vector_db


# -------------------------------
# 2. Load & Prepare BERT Reranker
# -------------------------------
reranker_model_name = "amberoad/bert-multilingual-passage-reranking-msmarco"
reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)

def rerank_score(query, passage):
    """
    Scores the relevance of a passage to a query using a pre-trained model.
    """
    inputs = reranker_tokenizer(query, passage, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = reranker_model(**inputs)
    return outputs.logits[0, 1].item()

def rerank_documents(query, docs, top_k=6):
    """
    Reranks documents based on their relevance to the query.
    """
    scored = [(rerank_score(query, d.page_content), d) for d in docs]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [doc for score, doc in scored[:top_k]]


# -------------------------------
# 3. Compliance Checking (Gemini version)
# -------------------------------
def check_compliance(vector_db, product):
    """
    Checks a product's compliance against rules using a vector DB and Gemini.
    """
    violations = []

    # Quick Pre-checks
    if "mrp" in product and product["mrp"]:
        if re.search(r"\b(kg|g|ml|l|litre|meter|cm)\b", product["mrp"].lower()):
            violations.append({
                "field": "mrp",
                "issue": "MRP value contains a unit (e.g., kg/g/ml) instead of currency.",
                "rule_reference": "Rule on Maximum Retail Price display",
                "reason": "The MRP should represent a monetary amount (e.g., Rs. 50.00), but units like weight/volume were found."
            })

    # Vector Search + Reranking
    query = json.dumps(product, indent=2)
    retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 20, "fetch_k": 30, "lambda_mult": 0.6})
    docs = retriever.invoke(query)
    if not docs:
        return {
            "compliance_status": "error",
            "violations": violations,
            "reasoning": "The system could not retrieve any matching rules for validation."
        }

    reranked_docs = rerank_documents(query, docs, top_k=6)
    context_text = "\n\n".join(d.page_content for d in reranked_docs)

    # LLM Validation (Gemini API)
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
    - "reason" must clearly explain why the violation occurred.
4. Do not invent violations not present in PRODUCT DATA.
5. General Rule: Any field with an empty string ("") as its value is a violation.

SPECIAL RULES:
- country_of_origin: If value is "India" or "INDIA", importer details are NOT required.
- imported_by: Mandatory ONLY if country_of_origin is not India.
- date_of_manufacture: "MM/YYYY", "YYYY-MM-DD", or "YYYY/M/D" formats are valid.
- net_quantity:
    - Must be a number followed by a valid unit (g, kg, ml, l, litre, meter, cm, pcs, pack, tablet, capsule).
    - If missing → flag as violation.
    - If it contains a currency unit (Rs, INR, $, rs, etc.), flag as wrong type.
- mrp:
    - Must be a monetary amount (Rs, INR, ₹, $).
    - If missing → flag as violation.
    - If it contains measurement units (g, kg, ml, litre, meter, cm, etc.), flag as wrong type.


OUTPUT FORMAT (strictly JSON):
{{
  "compliance_status": "compliant" | "non-compliant",
  "compliance_score" : "give in % out of total check and how many are missing",
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
    response = gemini_model.generate_content(prompt)
    raw_output = response.text
    
    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    json_str_fixed = json_match.group(0) if json_match else raw_output.strip()

    try:
        parsed = json.loads(json_str_fixed)
        
        if violations:
            parsed.setdefault("violations", []).extend(violations)
            parsed["compliance_status"] = "non-compliant"

        if "reasoning" not in parsed:
            if parsed.get("compliance_status") == "compliant":
                parsed["reasoning"] = "The product complies with all required rules."
            else:
                parsed["reasoning"] = "The product has one or more violations that make it non-compliant."

        return parsed
    except json.JSONDecodeError:
        return {
            "compliance_status": "error",
            "violations": violations,
            "reasoning": "The response from Gemini was malformed and could not be converted into structured JSON."
        }
    
# ------------------------------------------------
# 4. Update the MongoDB document with compliance data
# ------------------------------------------------
def update_compliance_in_db(document_id, compliance_data):
    """
    Updates the 'compliance' field of a MongoDB document.
    """
    MONGO_URI = "mongodb+srv://anirudhdatt3:anirudh2004@productdata.vfuvb8w.mongodb.net/?retryWrites=true&w=majority"
    MONGO_DB = "productdb"
    MONGO_COLLECTION = "products"
    
    client = None
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Add a timestamp to the compliance data before updating
        compliance_data["analysis_timestamp"] = datetime.utcnow().isoformat() + 'Z'
        
        # Update the document with the new compliance data
        result = collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"compliance": compliance_data}}
        )
        
        if result.modified_count > 0:
            print(f"Successfully updated document with ID {document_id}.")
        else:
            print(f"No document updated. Document with ID {document_id} not found.")

    except Exception as e:
        print(f"An error occurred while updating MongoDB: {e}")
    finally:
        if client:
            client.close()

# -------------------------------
# 5. Main
# -------------------------------
def main():
    """
    Main function to run the compliance check and update the database.
    """
    pdf_path = "pdfs/FInal-Book-Legal-Metrology-with-amendments.pdf"
    document_id = "68cde016ff7418eb09a1afac"

    if not os.path.exists("./rules_chroma_store"):
        vector_db = build_vector_db(pdf_path)
    else:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma.vectorstores import Chroma
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db = Chroma(
            persist_directory="./rules_chroma_store",
            collection_name="legal-metrology-col",
            embedding_function=embeddings
        )

    # Fetch OCR data from MongoDB
    client = None
    product_data = None
    try:
        client = MongoClient("mongodb+srv://anirudhdatt3:anirudh2004@productdata.vfuvb8w.mongodb.net/?retryWrites=true&w=majority")
        db = client["productdb"]
        collection = db["products"]
        
        document = collection.find_one({"_id": ObjectId(document_id)})
        
        if document and "ocr_data" in document:
            raw_ocr_data = document["ocr_data"]
            # Filter the data to get only the required fields
            fields_to_retrieve = {
                "manufacturer": "manufacturer",
                "address_manufacturer": "manufacturer_address",
                "country_of_origin": "country_of_origin",
                "common_product_name": "common_product_name",
                "net_quantity": "net_quantity",
                "mrp": "mrp",
                "unit_sale_price": "unit_sale_price",
                "date_of_manufacture": "date_of_manufacture",
                "best_before": "best_before",
            }
            product_data = {
                key: raw_ocr_data.get(value, None) for key, value in fields_to_retrieve.items()
            }
        else:
            print(f"Error: Document with ID {document_id} not found or 'ocr_data' is missing.")
            return

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return
    finally:
        if client:
            client.close()
    
    # Run compliance check
    if product_data:
        print("Successfully fetched product data. Running compliance check...")
        result = check_compliance(vector_db, product_data)
        print("\nFINAL COMPLIANCE CHECK RESULT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Update MongoDB with the result
        update_compliance_in_db(document_id, result)


if __name__ == "__main__":
    main()
