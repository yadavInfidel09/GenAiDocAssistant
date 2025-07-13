def chunk_document(parsed, chunk_size=500, overlap=100):
    chunks = []
    buffer = ''
    buffer_paragraphs = []
    buffer_pages = []
    for item in parsed:
        para = item['text']
        page = item['page']
        paragraph = item['paragraph']
        if buffer:
            buffer += ' '
        buffer += para
        buffer_paragraphs.append(paragraph)
        buffer_pages.append(page)
        if len(buffer) >= chunk_size:
            chunks.append({
                'text': buffer,
                'pages': list(set(buffer_pages)),
                'paragraphs': list(buffer_paragraphs)
            })
            # Overlap
            buffer = buffer[-overlap:]
            buffer_paragraphs = buffer_paragraphs[-2:]  # keep last 2
            buffer_pages = buffer_pages[-2:]
    # Add any remaining buffer
    if buffer:
        chunks.append({
            'text': buffer,
            'pages': list(set(buffer_pages)),
            'paragraphs': list(buffer_paragraphs)
        })
    return chunks
