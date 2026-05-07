import hashlib
import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from config import ACTIVE_MODEL_ID, UPLOAD_DIR
from core.pipeline import analyze_deed
from db.database import get_deed_by_hash, get_deed_by_id, init_db, save_deed
from ocr.doctr_ocr import IMAGE_EXTS, extract_text
from schemas import Deed, ExtractResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ALLOWED_EXTS = {".pdf", *IMAGE_EXTS}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Escrow POC — Deed Intelligence Service", lifespan=lifespan)


def _save_upload(file: UploadFile) -> tuple[Path, str]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type {suffix!r}. Allowed: {sorted(ALLOWED_EXTS)}",
        )
    body = file.file.read()
    file_hash = hashlib.sha256(body).hexdigest()
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    dest.write_bytes(body)
    return dest, file_hash


def _to_response(deed: Deed, *, cached: bool) -> ExtractResponse:
    return ExtractResponse(
        deed_id=deed.id,
        file_hash=deed.file_hash,
        raw_text=deed.raw_text,
        extracted_fields=deed.extracted_fields,
        rules=deed.rules,
        cached=cached,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract(file: UploadFile = File(...)) -> ExtractResponse:
    path, file_hash = _save_upload(file)
    logger.info("[extract] Saved %s (hash=%s)", path, file_hash[:12])

    cached = get_deed_by_hash(file_hash)
    if cached:
        logger.info("[extract] Cache hit, returning deed_id=%s", cached.id)
        return _to_response(cached, cached=True)

    try:
        raw_text = extract_text(path)
    except Exception as exc:
        logger.exception("[extract] OCR failed")
        raise HTTPException(status_code=422, detail=f"OCR failed: {exc}") from exc

    try:
        fields, rules = analyze_deed(raw_text)
    except Exception as exc:
        logger.exception("[extract] Agent pipeline failed")
        raise HTTPException(status_code=502, detail=f"Agent pipeline failed: {exc}") from exc

    deed_id = save_deed(
        file_hash=file_hash,
        raw_text=raw_text,
        fields=fields,
        rules=rules,
        model_version=ACTIVE_MODEL_ID,
    )

    return ExtractResponse(
        deed_id=deed_id,
        file_hash=file_hash,
        raw_text=raw_text,
        extracted_fields=fields,
        rules=rules,
        cached=False,
    )


@app.get("/deeds/{deed_id}", response_model=ExtractResponse)
def get_deed(deed_id: int) -> ExtractResponse:
    deed = get_deed_by_id(deed_id)
    if not deed:
        raise HTTPException(status_code=404, detail=f"Deed {deed_id} not found")
    return _to_response(deed, cached=True)
