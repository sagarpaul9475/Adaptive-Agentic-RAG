from app.services.chunking import split_text

def test_split_text_creates_overlapping_chunks():
    text = " ".join(f"word{i}" for i in range(300))
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert chunks[0].index == 0
    assert chunks[-1].text
    assert all(chunk.text for chunk in chunks)

def test_split_text_empty_input():
    assert split_text("   ", chunk_size=100, chunk_overlap=20) == []
