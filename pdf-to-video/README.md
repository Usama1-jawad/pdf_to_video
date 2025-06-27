# PDF to Video API

A Flask-based API that converts PDF documents to videos using AI-generated images and text-to-speech.

## Features

- PDF text extraction using pdfplumber
- Text-to-speech conversion using gTTS
- AI image generation using Stable Diffusion
- Video creation using MoviePy
- RESTful API endpoints

## API Endpoints

- `GET /` - Health check and welcome message
- `GET /health` - API health status
- `POST /upload` - Upload PDF and convert to video

## Usage

### Upload PDF
```bash
curl -X POST -F "file=@document.pdf" https://your-api-url/upload
```

The API will return the converted video file as a download.

## Deployment

This API is configured for deployment on Render.com with the following setup:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Environment**: Python 3.11

## Dependencies

- Flask - Web framework
- pdfplumber - PDF text extraction
- gTTS - Text-to-speech
- diffusers - AI image generation
- transformers - Hugging Face models
- torch - PyTorch for AI models
- moviepy - Video editing
- Pillow - Image processing
- gunicorn - WSGI server

## Notes

- The API processes only the first 3 paragraphs for performance
- Generated videos include AI-generated images synchronized with audio narration
- Temporary files are automatically cleaned up after processing 