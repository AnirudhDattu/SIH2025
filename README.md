# Legal Metrology Compliance Checker - SIH 2025

An AI-powered system that automatically checks packaged food products for compliance with India's Legal Metrology Act (Packaged Commodities Rules, 2011). This solution was developed for Smart India Hackathon 2025.

## 🎯 Project Overview

This system automates the compliance checking process by:
1. **Web Scraping** product images from e-commerce URLs
2. **OCR Processing** using Google Document AI for text extraction
3. **AI Analysis** using Google Gemini for intelligent data extraction
4. **Compliance Validation** against Legal Metrology rules using RAG (Retrieval Augmented Generation)
5. **Database Management** with MongoDB for storing results

## 🏗️ System Architecture

```
Product URL → Web Scraper → MongoDB → OCR Processor → Gemini AI → Compliance Checker → Results
```

## 📂 Project Structure

```
SIH2025/
├── main.py                     # Main orchestration pipeline
├── requirements.txt            # Python dependencies
├── config.yaml                 # Configuration file (not tracked)
├── .env                        # Environment variables (not tracked)
├── __init__.py                 # Package initialization
│
├── scraper/                    # Web scraping module
│   ├── __init__.py            # Package initialization
│   ├── scrape_upload_data.py  # Selenium-based image scraper
│   └── object_ids.txt         # Generated MongoDB IDs log
│
├── ocr_data_extractor/        # OCR and data processing
│   ├── __init__.py            # Package initialization
│   ├── image_parser.py        # Google Document AI integration
│   ├── image_processor.py     # Image download and processing
│   ├── gemini_postprocess.py  # AI-powered data extraction
│   └── update_mongodb.py      # Database update operations
│
├── rag/                       # Compliance checking system
│   ├── rag.py                 # RAG-based compliance validator
│   ├── pdfs/                  # Legal Metrology Act documents
│   │   └── FInal-Book-Legal-Metrology-with-amendments .pdf
│   └── rules_chroma_store/    # Vector database for legal rules
│       ├── chroma.sqlite3     # ChromaDB database file
│       └── [collection_dirs]  # Vector collection directories
│
└── temp/                      # Temporary processing files (created at runtime)
    ├── ocr_output.txt         # Consolidated OCR results
    └── product_output.json    # Final processed data
```

## 🚀 Core Components

### 1. Web Scraper (`scraper/`)
- **Technology**: Selenium WebDriver with Chrome
- **Purpose**: Extracts product images from e-commerce websites
- **Features**: 
  - Headless browser automation
  - Dynamic content loading
  - Image URL extraction and validation
  - MongoDB integration for initial data storage

### 2. OCR Data Extractor (`ocr_data_extractor/`)
- **Technology**: Google Document AI (Document & Form Parser)
- **Purpose**: Converts product images to structured text data
- **Components**:
  - `image_parser.py`: Google Cloud Document AI integration
  - `image_processor.py`: Batch image processing pipeline
  - `gemini_postprocess.py`: AI-powered data extraction using Gemini
  - `update_mongodb.py`: Database operations for processed data

### 3. RAG Compliance Checker (`rag/`)
- **Technology**: LangChain + ChromaDB + BERT Reranker + Google Gemini
- **Purpose**: Validates products against Legal Metrology Act requirements
- **Features**:
  - Vector database of legal rules
  - Semantic search and retrieval
  - BERT-based document reranking
  - AI-powered compliance analysis

### 4. Main Pipeline (`main.py`)
- **Purpose**: Orchestrates the entire workflow
- **Process**:
  1. Reads product URL from config
  2. Scrapes images and stores in MongoDB
  3. Processes all images through OCR
  4. Extracts structured data using AI
  5. Updates database with processed information

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+ (tested with Python 3.9+)
- Google Cloud Project with Document AI API enabled
- MongoDB Atlas account (or local MongoDB instance)
- Google Gemini API access
- Chrome/Chromium browser for Selenium WebDriver
- Sufficient storage space for temporary image processing (~500MB recommended)

### 1. Clone Repository
```bash
git clone https://github.com/AnirudhDattu/SIH2025.git
cd SIH2025
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `selenium` - Web scraping automation
- `pymongo` - MongoDB database connectivity
- `google-cloud-documentai` - Google Document AI for OCR
- `google-generativeai` - Google Gemini API integration
- `langchain-community` - LangChain framework for RAG
- `langchain-huggingface` - Hugging Face embeddings
- `langchain-chroma` - ChromaDB vector database
- `transformers` - BERT models for document reranking
- `torch` - PyTorch for machine learning models
- `sentence-transformers` - Semantic embeddings
- `chromadb` - Vector database for legal rules storage

### 3. Environment Configuration
Create `.env` file with your API credentials and database configuration:
```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=productdb
MONGODB_COLLECTION=products

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Google Cloud Document AI
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Optional: Logging Level
LOG_LEVEL=INFO
```

**Security Note:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 4. Create Configuration File
Create `config.yaml` with your API and processing configurations:
```yaml
# Target URL for product scraping
url: "https://example-ecommerce-site.com/product/123"

# Google Cloud Document AI Configuration
project_id: "your-gcp-project-id"
location: "us"  # or your preferred region (us, eu, asia-northeast1, etc.)

# Document Parser Configuration (for text extraction)
doc_processor_id: "your-document-processor-id"
doc_processor_version: "your-processor-version"  # or "rc" for latest

# Form Parser Configuration (for structured data extraction)
form_processor_id: "your-form-processor-id"
form_processor_version: "your-processor-version"  # or "rc" for latest

# Gemini AI Configuration
gemini:
  model: "gemini-2.0-flash-exp"  # or gemini-1.5-pro for more complex tasks
  api_key_env: "GEMINI_API_KEY"
  max_tokens: 8192
  temperature: 0.1  # Lower for more consistent outputs

# RAG Configuration (Optional - defaults provided)
rag:
  chunk_size: 1000
  chunk_overlap: 200
  similarity_threshold: 0.7
  max_retrieved_docs: 10
```

**Configuration Notes:**
- Replace placeholder values with your actual Google Cloud and API credentials
- The `url` field should point to an e-commerce product page with clear product images
- Use `gemini-2.0-flash-exp` for faster processing or `gemini-1.5-pro` for more accurate analysis

### 5. Setup Google Cloud Credentials
- Create a Google Cloud service account
- Download the JSON key file
- Place it in your project directory (outside of version control)
- Update the path in `.env` file

### 6. Initialize Vector Database (First Run)
The RAG system requires a vector database of legal rules. This is automatically created on first run:

```bash
# The system will:
# 1. Parse the Legal Metrology PDF document
# 2. Create embeddings for all rules and sections
# 3. Store them in rag/rules_chroma_store/
# 4. This process takes a few minutes initially but speeds up subsequent runs
```

**Note:** The `rules_chroma_store` directory contains the pre-built vector database and should not be deleted.

## 🚦 Usage

### Basic Usage
```bash
python main.py
```

### Step-by-Step Process
1. **Configure URL**: Update `config.yaml` with the product URL
2. **Run Pipeline**: Execute `main.py`
3. **Monitor Progress**: Check console output for each stage
4. **View Results**: Check `temp/product_output.json` for extracted data
5. **Database**: Processed data is automatically stored in MongoDB

### Individual Module Usage

#### Run Only Scraper
```python
from scraper.scrape_upload_data import run_pipeline
object_id = run_pipeline("https://example.com/product")
```

#### Run Only OCR Processing
```python
from ocr_data_extractor.image_processor import process_images_to_ocr
process_images_to_ocr("config.yaml", image_urls, "output.txt")
```

#### Run Only Compliance Check
```python
from rag.rag import main as run_compliance_check
run_compliance_check()
```

## 📊 Data Flow

### MongoDB Document Structure
```json
{
  "_id": "ObjectId",
  "product_title": "Product Name",
  "image_urls": ["url1", "url2"],
  "product_url": "source_url",
  "status": "ocr_uploaded",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "ocr_data": {
    "manufacturer": "Company Name",
    "manufacturer_address": "Address",
    "country_of_origin": "India",
    "common_product_name": "Biscuits",
    "net_quantity": "100g",
    "mrp": "Rs. 50",
    "unit_sale_price": "Rs. 45",
    "date_of_manufacture": "01/2024",
    "best_before": "12/2024",
    "raw_ocr_text": "Full OCR content..."
  },
  "compliance": {
    "score": "85%",
    "status": "non-compliant",
    "violations": [
      {
        "field": "manufacturer_address",
        "issue": "Address incomplete",
        "rule_reference": "Rule 6(1)",
        "reason": "Missing pin code"
      }
    ],
    "reasoning": "Detailed analysis...",
    "analysis_timestamp": "2024-01-01T00:00:00"
  }
}
```

## 🎯 Legal Metrology Compliance Checks

The system validates against these key requirements:

### Mandatory Information
- ✅ **Manufacturer Name and Address**
- ✅ **Common/Generic Name of Commodity**
- ✅ **Net Quantity** (weight, measure, or number)
- ✅ **Maximum Retail Price (MRP)**
- ✅ **Date of Manufacture/Packing**
- ✅ **Best Before/Use By Date**
- ✅ **Country of Origin** (for imported goods)

## 🔧 Technical Features

### AI-Powered OCR
- **Google Document AI**: Industry-leading OCR accuracy
- **Form Parser**: Extracts key-value pairs from product labels
- **Table Parser**: Handles nutritional information tables

### Intelligent Data Extraction
- **Google Gemini**: Advanced language model for data interpretation
- **Structured Output**: Consistent JSON format generation
- **Error Handling**: Robust retry mechanisms and fallbacks

### Compliance Validation
- **Vector Database**: ChromaDB for efficient rule retrieval
- **Semantic Search**: Finds relevant legal provisions
- **BERT Reranking**: Improves search result relevance
- **AI Analysis**: Gemini-powered compliance assessment

### Web Scraping
- **Selenium Automation**: Handles dynamic content loading
- **Multi-image Support**: Extracts all product images
- **Error Recovery**: Handles common web scraping issues

## 🔒 Security & Privacy

- Environment variables for sensitive configuration
- Secure MongoDB connections with authentication
- Google Cloud IAM for API access control
- No sensitive data stored in repository
- Temporary file cleanup after processing

## 📈 Performance Optimization

- **Batch Processing**: Multiple images processed together
- **Vector Caching**: Legal rules stored in a persistent vector database
- **Connection Pooling**: Efficient database connections
- **Memory Management**: Temporary files cleaned automatically

## 🤝 Contributing

This repository welcomes contributions from developers interested in improving legal metrology compliance checking. We follow standard Git workflow practices for clean, collaborative development.

### Quick Start for Contributors
1. **Fork & Clone**: Fork this repository and clone your fork
2. **Setup Environment**: Install dependencies and configure your environment (see setup instructions above)
3. **Create Branch**: Always work on feature branches (`feature/description`, `fix/description`, etc.)
4. **Develop & Test**: Make your changes and test the complete pipeline
5. **Submit PR**: Create a detailed pull request for review

### Development Workflow
- **Fork the repository** to your GitHub account
- **Clone your fork** and add the original as upstream
- **Create feature branches** for all changes
- **Follow conventional commits** (`feat:`, `fix:`, `docs:`, etc.)
- **Test thoroughly** before submitting PRs
- **Write clear PR descriptions** with testing instructions

### Branch Naming Convention
- `feature/description` - New features (e.g., `feature/add-batch-processing`)
- `fix/description` - Bug fixes (e.g., `fix/gemini-api-timeout`)
- `docs/description` - Documentation updates (e.g., `docs/update-setup-guide`)
- `refactor/description` - Code improvements (e.g., `refactor/modularize-rag-system`)
- `test/description` - Adding or updating tests

### Code Standards
- **Python PEP 8**: Follow standard Python style guidelines
- **Type Hints**: Include type annotations for functions
- **Docstrings**: Document all functions and classes
- **Error Handling**: Include appropriate try-catch blocks
- **Configuration**: Use environment variables for sensitive data

### Testing Your Changes
Before submitting a PR, ensure your changes work correctly:

```bash
# Test the complete pipeline
python main.py

# Test individual components
python -m ocr_data_extractor.image_processor
python -m rag.rag

# Verify dependencies
pip install -r requirements.txt
```

### What We're Looking For
- **Performance Improvements**: Optimize OCR processing or RAG queries
- **New Features**: Additional compliance checks or data extraction capabilities
- **Bug Fixes**: Address issues with existing functionality
- **Documentation**: Improve setup guides, API documentation, or code comments
- **Testing**: Add unit tests or integration tests
- **Error Handling**: Better error messages and recovery mechanisms

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License & Legal

This project is developed for Smart India Hackathon 2025. The Legal Metrology compliance rules are based on the official Government of India regulations.

## 🆘 Support

### Troubleshooting

#### Common Setup Issues

**Python Import Errors:**
```bash
# If you encounter module import errors, ensure virtual environment is activated
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Google Cloud Authentication:**
```bash
# Set the service account key path
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
# Verify authentication
gcloud auth application-default login
```

**MongoDB Connection Issues:**
- Verify your MongoDB URI in `.env` file
- Ensure MongoDB Atlas cluster is running and accessible
- Check network connectivity and firewall settings

**ChromeDriver Issues:**
```bash
# Install ChromeDriver automatically
pip install webdriver-manager
# Or download manually from https://chromedriver.chromium.org/
```

#### Performance Optimization Tips
- **Batch Processing**: Process multiple images in a single run for better efficiency
- **Vector Database**: The RAG system builds its vector database on first run - subsequent runs are faster
- **Temporary Files**: The system automatically cleans up `temp/` files after processing
- **Memory Management**: For large image sets, consider processing in smaller batches

#### Getting Help
For technical issues or questions:
1. Check the troubleshooting section above
2. Review error logs in console output
3. Verify all configuration files are properly set up
4. Search existing [GitHub Issues](https://github.com/AnirudhDattu/SIH2025/issues)
5. Create a new issue with detailed error information and steps to reproduce

#### Contributing Help
- Check the [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines
- Look for issues labeled `good first issue` or `help wanted`
- Join discussions in existing pull requests
- Ask questions in issue comments before starting work

---

**Note**: This system is designed for educational and demonstration purposes as part of SIH 2025. For production use in regulatory compliance, additional validation and legal review may be required.
