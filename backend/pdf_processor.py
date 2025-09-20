# In backend/pdf_processor.py

import fitz  # PyMuPDF

def extract_structured_text(pdf_path: str):
    """
    Extracts structured text from a PDF file, classifying blocks as headings or paragraphs.
    """
    doc = fitz.open(pdf_path)
    structured_text = []
    
    # Analyze font sizes to find a baseline for paragraph text.
    font_counts = {}
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0: # Block of text
                for l in b["lines"]:
                    for s in l["spans"]:
                        size = round(s['size'])
                        font_counts[size] = font_counts.get(size, 0) + len(s['text'].strip())

    if not font_counts:
        # Handle empty or image-only PDFs
        return []

    # The most frequent font size is likely the main paragraph text.
    base_size = max(font_counts, key=font_counts.get)
    
    # Extract and classify text blocks
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            # The block is a tuple: (x0, y0, x1, y1, "text", block_no, block_type)
            block_text = b[4].strip()
            if not block_text:
                continue

            # Heuristic logic to classify based on font size
            try:
                # To get font size, we need to check the first line's first span of the block
                page_dict = page.get_text("dict")
                text_block = page_dict['blocks'][b[5]] # Find block by block_no
                first_line = text_block['lines'][0]
                first_span = first_line['spans'][0]
                font_size = round(first_span['size'])
                
                block_type = "para" # Default to paragraph
                if font_size > base_size + 1: # If font is slightly larger, it could be a heading
                    block_type = "heading"

                structured_text.append({
                    "type": block_type,
                    "text": block_text.replace('\n', ' '), # Clean up newlines
                    "page": page_num + 1
                })
            except (IndexError, KeyError):
                # Fallback for blocks without clear span info
                structured_text.append({
                    "type": "para",
                    "text": block_text.replace('\n', ' '),
                    "page": page_num + 1
                })

    return structured_text