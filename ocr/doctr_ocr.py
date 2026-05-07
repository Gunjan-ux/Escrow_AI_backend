from functools import lru_cache
from pathlib import Path

from doctr.io import DocumentFile
from doctr.models import ocr_predictor

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


@lru_cache(maxsize=1)
def _predictor():
    return ocr_predictor(pretrained=True)


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        doc = DocumentFile.from_pdf(str(path))
    elif suffix in IMAGE_EXTS:
        doc = DocumentFile.from_images(str(path))
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    result = _predictor()(doc)
    return result.render()
