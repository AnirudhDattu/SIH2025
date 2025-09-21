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
│
├── scraper/                    # Web scraping module
│   ├── scrape_upload_data.py  # Selenium-based image scraper
│   └── object_ids.txt         # Generated MongoDB IDs log
│
├── ocr_data_extractor/        # OCR and data processing
│   ├── image_parser.py        # Google Document AI integration
│   ├── image_processor.py     # Image download and processing
│   ├── gemini_postprocess.py  # AI-powered data extraction
│   └── update_mongodb.py      # Database update operations
│
├── rag/                       # Compliance checking system
│   ├── rag.py                 # RAG-based compliance validator
│   ├── pdfs/                  # Legal Metrology Act documents
│   │   └── FInal-Book-Legal-Metrology-with-amendments.pdf
│   └── rules_chroma_store/    # Vector database for legal rules
│
└── temp/                      # Temporary processing files
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
- Python 3.8+
- Google Cloud Project with Document AI API enabled
- MongoDB Atlas account
- Google Gemini API access
- Chrome/Chromium browser for Selenium

### 1. Clone Repository
```bash
git clone https://github.com/AnirudhDattu/SIH2025.git
cd SIH2025
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` file with your API keys and credentials:
```bash
# Copy from template and edit with your values
cp .env.example .env
```

Required environment variables:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=productdb
MONGODB_COLLECTION=products
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Optional configuration
SELENIUM_HEADLESS=1
SELENIUM_TIMEOUT=30
```

### 4. Create Configuration File
Copy and customize the configuration file:
```bash
# Copy from template and edit with your values
cp config.yaml.example config.yaml
```

Configuration options:
```yaml
# Product URL to scrape and analyze
url: "https://example-ecommerce-site.com/product/123"

# Google Cloud Document AI Configuration
project_id: "your-gcp-project-id"
location: "us"  # or your preferred region (us, eu, asia-northeast1)

# Document Parser Configuration
doc_processor_id: "your-document-processor-id"
doc_processor_version: "rc"  # or specific version

# Form Parser Configuration  
form_processor_id: "your-form-processor-id"
form_processor_version: "rc"  # or specific version

# AI Model Configuration
gemini_model: "gemini-2.5-pro"  # or "gemini-2.5-flash" for faster processing
gemini_api_key_env: "GEMINI_API_KEY"

# Optional: RAG System Configuration
rules_pdf: "rag/pdfs/Final-Book-Legal-Metrology-with-amendments.pdf"
rules_store: "rag/rules_chroma_store"

# Optional: Selenium Configuration (for headless mode)
selenium_headless: "1"  # Set to "1" for headless mode
```

### 5. Setup Google Cloud Credentials
- Create a Google Cloud service account
- Download the JSON key file
- Place it in your project directory
- Update the path in `.env` file

## 🚦 Usage

### Prerequisites Check
Before running the system, ensure you have:
```bash
# Check Python version (3.8+ required)
python --version

# Verify Chrome/Chromium is installed
google-chrome --version || chromium --version

# Test MongoDB connection
python -c "import pymongo; print('MongoDB driver ready')"

# Verify Google Cloud credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### Basic Usage
```bash
# Run the complete pipeline
python main.py

# For debugging, run with verbose output
python -v main.py 2>&1 | tee pipeline.log
```

### Step-by-Step Process
1. **Configure URL**: Update `config.yaml` with the target product URL
2. **Environment Setup**: Ensure all API keys and credentials are configured in `.env`
3. **Run Pipeline**: Execute `main.py` to start the complete workflow
4. **Monitor Progress**: Check console output for real-time progress updates
5. **View Results**: 
   - Temporary files: `temp/ocr_output.txt` (raw OCR) and `temp/product_output.json` (processed data)
   - Database: Final results automatically stored in MongoDB with compliance analysis
6. **Cleanup**: Temporary files are automatically cleaned up after 30 seconds

### Individual Module Usage

#### Run Only Image URL Extraction
```python
from scraper.scrape_upload_data import extract_image_urls
image_urls = extract_image_urls("https://example.com/product")
print(f"Found {len(image_urls)} product images")
```

#### Run Only OCR Processing
```python
from ocr_data_extractor.image_processor import process_images_to_ocr
from ocr_data_extractor.gemini_postprocess import process_ocr_to_json

# Process images to OCR text
process_images_to_ocr("config.yaml", image_urls, "temp/ocr_output.txt")

# Extract structured data using AI
product_data = process_ocr_to_json("temp/ocr_output.txt", "config.yaml", image_urls[0])
```

#### Run Only Compliance Check
```python
from rag.rag import load_vector_db, check_compliance

# Load legal rules database
vector_db = load_vector_db("rag/rules_chroma_store")

# Check compliance for product data
ocr_data = {"manufacturer": "ABC Corp", "net_quantity": "100g", ...}
compliance_result = check_compliance(vector_db, ocr_data)
print(f"Compliance Status: {compliance_result['compliance_status']}")
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
- **Google Document AI**: Industry-leading OCR accuracy with specialized processors
  - Document Parser: Handles general text extraction from product labels
  - Form Parser: Extracts key-value pairs and structured data
- **Multi-format Support**: JPEG, PNG, PDF, TIFF image formats
- **Batch Processing**: Processes multiple product images simultaneously

### Intelligent Data Extraction
- **Google Gemini**: Advanced language model for data interpretation
  - Model Options: `gemini-2.5-pro` (high accuracy) or `gemini-2.5-flash` (faster processing)
  - Structured JSON Output: Consistent data format with validation
  - Error Handling: Robust retry mechanisms with exponential backoff
  - IST Timestamp Support: Indian Standard Time for created/updated timestamps

### Compliance Validation
- **Vector Database**: ChromaDB for efficient legal rule storage and retrieval
  - Persistent storage with automatic rebuilding when needed
  - Semantic Search: Finds relevant legal provisions using embeddings
  - HuggingFace Embeddings: sentence-transformers/all-MiniLM-L6-v2 model
- **BERT Reranking**: Improves search result relevance with transformer-based scoring
- **AI Analysis**: Gemini-powered compliance assessment with detailed violation reporting

### Web Scraping
- **Selenium Automation**: Handles dynamic content loading and JavaScript-rendered pages
- **Chrome WebDriver**: Configurable headless/headed mode operation
- **Multi-image Support**: Extracts all available product images from e-commerce pages
- **Error Recovery**: Handles common web scraping issues with timeout and retry logic

### Database Integration
- **MongoDB Atlas**: Cloud-based document storage with full-text search
- **Connection Pooling**: Efficient database connections with automatic reconnection
- **Document Validation**: Schema validation for consistent data structure
- **Atomic Operations**: Ensures data integrity during multi-step processing

## 🔒 Security & Privacy

- Environment variables for sensitive configuration
- Secure MongoDB connections with authentication
- Google Cloud IAM for API access control
- No sensitive data stored in repository
- Temporary file cleanup after processing

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Configuration Issues
```bash
# Error: config.yaml not found
# Solution: Create config.yaml in the project root directory
cp config.yaml.example config.yaml  # If example exists
# Or create manually using the template in setup instructions

# Error: MONGODB_URI not set
# Solution: Check your .env file contains the correct MongoDB connection string
echo "MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/" >> .env
```

#### Google Cloud API Issues
```bash
# Error: Google Cloud credentials not found
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Error: Document AI API not enabled
# Solution: Enable Document AI API in Google Cloud Console
gcloud services enable documentai.googleapis.com --project=your-project-id
```

#### Selenium WebDriver Issues
```bash
# Error: Chrome driver not found
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y google-chrome-stable

# macOS:
brew install --cask google-chrome

# For headless environments:
export SELENIUM_HEADLESS=1
```

#### Memory and Performance Issues
```bash
# Large images causing memory issues
# Solution: Reduce image size or use batch processing
# Monitor memory usage during processing
python -c "import psutil; print(f'Available memory: {psutil.virtual_memory().available // (1024**3)} GB')"
```

#### Network and API Rate Limits
```bash
# Gemini API rate limit exceeded
# Solution: Add delays between API calls or reduce batch size
# Check API quotas in Google Cloud Console
```

## 📈 Performance Optimization

### Recommended System Requirements
- **CPU**: 4+ cores for parallel processing
- **RAM**: 8GB+ (16GB recommended for large datasets)
- **Storage**: 2GB+ free space for temporary files and vector database
- **Network**: Stable internet connection for API calls and web scraping

### Performance Tuning Options
- **Batch Processing**: Process multiple images simultaneously (configure in main.py)
- **Vector Caching**: Legal rules stored in persistent ChromaDB for faster subsequent runs
- **Connection Pooling**: MongoDB connections are reused efficiently
- **Memory Management**: Automatic cleanup of temporary files prevents disk space issues
- **Parallel Processing**: OCR operations can be parallelized for multiple images

### Monitoring and Logging
```bash
# Enable detailed logging
export GRPC_VERBOSITY=DEBUG  # For Google Cloud API debugging
export GEMINI_LOG_LEVEL=INFO  # For Gemini API logging

# Monitor system resources during processing
htop  # or top on systems without htop
nvidia-smi  # If using GPU acceleration
```

## 🤝 Contributing

We welcome contributions to improve the Legal Metrology Compliance Checker! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors
```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/SIH2025.git
cd SIH2025

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Install dependencies and set up environment
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys

# 4. Make your changes and test
python main.py  # Test the complete pipeline
# Or test individual modules

# 5. Submit pull request
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### Areas for Contribution
- **Web Scraping**: Add support for new e-commerce platforms
- **OCR Processing**: Improve accuracy for different product label formats
- **Compliance Rules**: Enhance legal metrology rule validation
- **UI/UX**: Develop web interface or CLI improvements
- **Documentation**: Improve setup guides and API documentation
- **Testing**: Add unit tests and integration tests
- **Performance**: Optimize processing speed and memory usage

### Development Workflow
1. **Issue Discussion**: Create or comment on issues before starting work
2. **Branch Naming**: Use `feature/`, `fix/`, `docs/`, or `refactor/` prefixes
3. **Code Style**: Follow PEP 8 guidelines and use meaningful variable names
4. **Testing**: Ensure your changes don't break existing functionality
5. **Documentation**: Update relevant documentation for new features
6. **Pull Request**: Provide clear description of changes and rationale

## 📄 License & Legal

This project is developed for Smart India Hackathon 2025. The Legal Metrology compliance rules are based on the official Government of India regulations.

## 🆘 Support

For technical issues or questions:
1. Check the troubleshooting section above
2. Review error logs in console output
3. Verify all configuration files are properly set up
4. Create an issue in the repository with detailed error information

---

**Note**: This system is designed for educational and demonstration purposes as part of SIH 2025. For production use in regulatory compliance, additional validation and legal review may be required.
