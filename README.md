# Unified Document Assistant API

A FastAPI-based document processing and question-answering system that leverages NVIDIA's LLaMA model to provide intelligent responses based on document context.

## 🚀 Features

- **Multi-format Document Support**: Process PDF, DOCX, EML, and TXT files
- **AI-Powered Q&A**: Uses NVIDIA's LLaMA-3.3-Nemotron model for intelligent responses
- **RESTful API**: Simple HTTP endpoint for document analysis
- **Context-Aware Responses**: Answers questions based on the loaded document content
- **URL-based Document Loading**: Fetch documents directly from URLs

## 📋 Prerequisites

- Python 3.8+
- NVIDIA API Key (for LLaMA model access)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd unified-doc-assistant
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up your API key**
   - Replace `"API KEY HERE"` in `utils.py` with your actual NVIDIA API key
   - Or use environment variables (recommended):
```bash
export NVIDIA_API_KEY="your-api-key-here"
```

## 📦 Dependencies

Create a `requirements.txt` file:
```txt
fastapi==0.104.1
uvicorn==0.24.0
PyPDF2==3.0.1
python-docx==1.1.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
openai==1.3.0
requests==2.31.0
pydantic==2.5.0
python-multipart==0.0.6
```

## 🏃‍♂️ Running the Application

1. **Start the FastAPI server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📡 API Usage

### Endpoint: `/api/v1/hackrx/run`

**Method:** POST

**Request Body:**
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the main topic of this document?",
    "Can you summarize the key points?"
  ]
}
```

**Response:**
```json
{
  "document": "document.pdf",
  "status": "PDF loaded successfully.",
  "answers": [
    {
      "question": "What is the main topic of this document?",
      "answer": "The main topic is..."
    },
    {
      "question": "Can you summarize the key points?",
      "answer": "The key points are..."
    }
  ]
}
```

### Example cURL Request
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
     -H "Content-Type: application/json" \
     -d '{
       "documents": "https://example.com/sample.pdf",
       "questions": ["What is this document about?"]
     }'
```

## 🏗️ Project Structure

```
unified-doc-assistant/
├── main.py           # FastAPI application and routes
├── utils.py          # Document processing and AI logic
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file:
```env
NVIDIA_API_KEY=your-api-key-here
API_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=nvidia/llama-3.3-nemotron-super-49b-v1.5
```

### Supported File Types
- **PDF** (.pdf)
- **Word Documents** (.docx, .docs, .word, .docm, .document)
- **Email** (.eml)
- **Text** (.txt)

## 🚨 Error Handling

The API provides detailed error messages:
- `400`: Failed to download document
- `422`: Document parsed but no text extracted
- `500`: Internal server error

## 🔐 Security Considerations

1. **API Key Security**: Never commit your API key to version control
2. **Input Validation**: The system validates file extensions and URLs
3. **CORS**: Configure CORS settings based on your deployment needs

## 🐛 Troubleshooting

### Common Issues

1. **"No document loaded to provide context"**
   - Ensure the document URL is accessible
   - Check if the file format is supported

2. **"Failed to download document"**
   - Verify the document URL is correct
   - Check network connectivity

3. **API Key errors**
   - Ensure your NVIDIA API key is valid
   - Check if the key has proper permissions

## 📈 Performance Tips

1. **Document Size**: Large documents may take longer to process
2. **Question Complexity**: Simple, specific questions yield better results
3. **Caching**: Consider implementing caching for frequently accessed documents

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- NVIDIA for providing the LLaMA-3.3-Nemotron model
- FastAPI for the excellent web framework
- All contributors to the dependent libraries
