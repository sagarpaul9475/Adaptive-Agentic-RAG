from datetime import datetime
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    stored_filename: str
    file_type: str
    file_size_bytes: int = Field(ge=0)
    uploaded_at: datetime
    page_count: int | None = None
    character_count: int = Field(ge=0)
    chunk_count: int = Field(ge=0)

class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadata]
