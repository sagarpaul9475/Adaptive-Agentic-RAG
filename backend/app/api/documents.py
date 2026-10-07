from fastapi import APIRouter, File, HTTPException, UploadFile
from app.models.document import DocumentListResponse, DocumentMetadata
from app.services.document_store import delete_document, ingest_upload, list_documents

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)) -> DocumentMetadata:
    try:
        return await ingest_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document ingestion failed") from exc

@router.get("", response_model=DocumentListResponse)
def get_documents() -> DocumentListResponse:
    return DocumentListResponse(documents=list_documents())

@router.delete("/{document_id}")
def remove_document(document_id: str) -> dict[str, str]:
    if not delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}
