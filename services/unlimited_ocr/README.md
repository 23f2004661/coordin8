# Unlimited-OCR Microservice

This service isolates Baidu Unlimited-OCR and its GPU/CUDA inference dependencies from the main Coordin8 backend environment.

Conforms to Section 6 and Section 24 of `ProjectDetails.md`.

---

## Why Isolate?

Unlimited-OCR requires specific GPU dependencies:
- Python 3.12.3 (recommended by upstream repository)
- CUDA 12.9
- Transformers 4.57.1 or vLLM / SGLang serving engines

Isolating it in its own microservice prevents heavyweight ML libraries from contaminating the main API environment.

---

## Running Locally

```powershell
cd services/unlimited_ocr

# Create isolated venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run service
python server.py
```

The service will listen on `http://127.0.0.1:9001`.

---

## Endpoints

- `GET /health` — Service readiness
- `POST /parse_image` — Accepts image file, returns structured markdown + bounding regions
- `POST /parse_pdf` — Multi-page PDF renderer and parsing
