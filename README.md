# Escrow POC — AI Service

OCR + Agno extraction + deterministic rule generation for commercial sale deeds.
Returns `{raw_text, fields, rules}` for the future backend to persist.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set ANTHROPIC_API_KEY
```

System deps:

```bash
sudo apt install poppler-utils libreoffice
```

Convert the sample `.docx` deeds to PDF (one-time):

```bash
libreoffice --headless --convert-to pdf --outdir data/samples/ \
  Dubai_Commercial_Sale_Deed.docx India_Commercial_Sale_Deed.docx
```

## Run

```bash
uvicorn main:app --port 8001 --reload
```

## Try it

```bash
curl -F "file=@data/samples/Dubai_Commercial_Sale_Deed.pdf" \
     http://localhost:8001/extract | jq
```

Optional query params: `sla_days` (default 30), `penalty_pct` (default 2.0).

## Tests

```bash
pytest tests/
```

## Layout

| Path | Purpose |
|---|---|
| `main.py` | FastAPI app, `/extract` route |
| `ocr/doctr_ocr.py` | doctr wrapper, PDF/image → text |
| `agents/extractor.py` | Agno agent, text → structured fields |
| `rules/generator.py` | Deterministic field → rules generator |
| `prompts/extractor_system.txt` | System prompt for the extractor agent |
| `schemas.py` | Pydantic response models |
| `config.py` | Env loading |
