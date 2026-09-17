import os

HOST = os.getenv("OCR_HOST", "127.0.0.1")
PORT = int(os.getenv("OCR_PORT", "9001"))
MODEL_NAME = os.getenv("OCR_MODEL_NAME", "Unlimited-OCR")
MODEL_VERSION = os.getenv("OCR_MODEL_VERSION", "2026-07")
DEVICE = os.getenv("OCR_DEVICE", "cuda")
