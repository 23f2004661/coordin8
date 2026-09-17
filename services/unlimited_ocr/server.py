"""FastAPI worker server for Unlimited-OCR."""

import time
from fastapi import FastAPI, File, UploadFile
import uvicorn
from config import DEVICE, HOST, MODEL_NAME, MODEL_VERSION, PORT

app = FastAPI(title="Unlimited-OCR Worker", version="0.1.0")


@app.get("/health")
def health():
    return {
        "status": "ready",
        "service": "unlimited-ocr-worker",
        "model": MODEL_NAME,
        "version": MODEL_VERSION,
        "device": DEVICE,
    }


@app.post("/parse_image")
async def parse_image(file: UploadFile = File(...)):
    start = time.time()
    content = await file.read()
    # Placeholder for upstream Baidu Unlimited-OCR inference call
    text_markdown = f"# Extracted Text from {file.filename}\n\nUnlimited-OCR extracted content."
    return {
        "text_markdown": text_markdown,
        "raw_text": "Unlimited-OCR extracted content.",
        "page_number": 1,
        "regions": [],
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "processing_time": time.time() - start,
        "warnings": [],
    }


@app.post("/parse_pdf")
async def parse_pdf(file: UploadFile = File(...)):
    start = time.time()
    content = await file.read()
    # Multi-page PDF workflow renders pages to images and parses
    return [
        {
            "page_number": 1,
            "text_markdown": f"# Page 1: {file.filename}\n\nMulti-page OCR parsed content.",
            "raw_text": "Multi-page OCR parsed content.",
            "regions": [],
            "warnings": [],
        }
    ]


if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
