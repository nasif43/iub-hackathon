import re

def segment_contract(raw_text: str) -> list[tuple[str, str]]:
    """
    Splits contract text into (heading, body) tuples.
    Regex on numbered headings e.g. '2.1 Payment' or '10.1 Liability'
    Stops at the line containing 'Dataset Note:'
    """
    lines = raw_text.splitlines()
    blocks = []
    
    # Locate dataset note line and truncate
    clean_lines = []
    for line in lines:
        if "Dataset Note:" in line:
            break
        clean_lines.append(line)
        
    text_to_segment = "\n".join(clean_lines).strip()
    
    # Pattern: a newline or start of string, followed by digits, dot, digits, spaces, and the heading text on the same line
    heading_pattern = re.compile(r'(?:^|\n)(\d+\.\d+(?:\.\d+)*\s+[^\n]+)')

    
    matches = list(heading_pattern.finditer(text_to_segment))
    
    if not matches:
        return []
        
    for i in range(len(matches)):
        start_pos = matches[i].start()
        # Clean heading (strip the leading newline if any)
        heading_text = matches[i].group(1).strip()
        
        # End of the block is either the start of the next match, or the end of the text
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(text_to_segment)
        
        # Extract body (excluding the heading text itself)
        heading_full_match_text = matches[i].group(0)
        # body starts after the heading match
        heading_in_segment_start = start_pos + len(heading_full_match_text)
        body = text_to_segment[heading_in_segment_start:end_pos].strip()
        
        blocks.append((heading_text, body))
        
    return blocks
