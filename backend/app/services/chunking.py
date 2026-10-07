from dataclasses import dataclass

@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str

def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk_text = normalized[start:end].strip()
        if chunk_text:
            chunks.append(TextChunk(index=index, text=chunk_text))
            index += 1
        if end >= len(normalized):
            break
        next_start = max(0, end - chunk_overlap)
        if next_start <= start:
            next_start = end
        start = next_start
    return chunks
