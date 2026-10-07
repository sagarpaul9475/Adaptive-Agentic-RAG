import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings
from app.models.document import DocumentMetadata
from app.services.chunking import split_text
from app.services.document_parser import parse_document

_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")

def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    name = _FILENAME_PATTERN.sub("_", name).strip("._")
    return name or "document"

def _manifest_path(document_id: str) -> Path:
    return settings.DATA_DIR / f"{document_id}.json"

def _document_dir(document_id: str) -> Path:
    return settings.DATA_DIR / "documents" / document_id

def _load_metadata(path: Path) -> DocumentMetadata:
    return DocumentMetadata.model_validate_json(path.read_text(encoding="utf-8"))

def list_documents() -> list[DocumentMetadata]:
    documents = []
    for manifest in settings.DATA_DIR.glob("*.json"):
        try:
            documents.append(_load_metadata(manifest))
        except Exception:
            continue
    return sorted(documents, key=lambda item: item.uploaded_at, reverse=True)

async def ingest_upload(upload: UploadFile) -> DocumentMetadata:
    original_name = _safe_filename(upload.filename or "document")
    extension = Path(original_name).suffix.lower().lstrip(".")
    if extension not in settings.allowed_extension_set:
        allowed = ", ".join(sorted(settings.allowed_extension_set))
        raise ValueError(f"Unsupported file type. Allowed types: {allowed}")

    document_id = str(uuid4())
    stored_filename = f"{document_id}_{original_name}"
    destination = settings.UPLOAD_DIR / stored_filename
    document_dir = _document_dir(document_id)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    total_bytes = 0

    try:
        with destination.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise ValueError(f"File exceeds the {settings.max_upload_size_mb} MB upload limit")
                output.write(chunk)

        parsed = parse_document(destination, extension)
        if not parsed.text.strip():
            raise ValueError("No extractable text was found in the uploaded document")

        chunks = split_text(parsed.text, settings.chunk_size, settings.chunk_overlap)
        document_dir.mkdir(parents=True, exist_ok=True)
        chunks_path = document_dir / "chunks.jsonl"
        with chunks_path.open("w", encoding="utf-8") as output:
            for chunk in chunks:
                record = {"document_id": document_id, "chunk_index": chunk.index, "text": chunk.text, "source": original_name}
                output.write(json.dumps(record, ensure_ascii=False) + "\n")

        metadata = DocumentMetadata(
            document_id=document_id,
            filename=original_name,
            stored_filename=stored_filename,
            file_type=extension,
            file_size_bytes=total_bytes,
            uploaded_at=datetime.now(timezone.utc),
            page_count=parsed.page_count,
            character_count=len(parsed.text),
            chunk_count=len(chunks),
        )
        _manifest_path(document_id).write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
        return metadata
    except Exception:
        destination.unlink(missing_ok=True)
        if document_dir.exists():
            for child in document_dir.iterdir():
                child.unlink(missing_ok=True)
            document_dir.rmdir()
        _manifest_path(document_id).unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

def delete_document(document_id: str) -> bool:
    metadata_path = _manifest_path(document_id)
    if not metadata_path.exists():
        return False
    try:
        metadata = _load_metadata(metadata_path)
        (settings.UPLOAD_DIR / metadata.stored_filename).unlink(missing_ok=True)
    except Exception:
        pass
    document_dir = _document_dir(document_id)
    if document_dir.exists():
        for child in document_dir.iterdir():
            child.unlink(missing_ok=True)
        document_dir.rmdir()
    metadata_path.unlink(missing_ok=True)
    return True
