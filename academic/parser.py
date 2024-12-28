import re
import os

def extract_sections(content):
    """
    Extract specific sections from academic paper content.
    Returns a dictionary with section names as keys and their content as values.
    """
    sections = {
        'Abstract': None,
        'Introduction': None,
        'Method': None,
        'Conclusion': None
    }
    
    # Pattern for finding sections
    # Look for section headers that might be numbered (e.g., "1. Introduction" or just "Introduction")
    section_patterns = {
        'Abstract': r'(?:^|\n)(?:Abstract|ABSTRACT\n*)(.*?)(?=\n(?:\d+\.?\s*)?(?:Introduction|INTRODUCTION|Related Work|\d|$))',
        'Introduction': r'(?:^|\n)(?:\d+\.?\s*)?Introduction|INTRODUCTION\n*(.*?)(?=\n(?:\d+\.?\s*)?(?:Related Work|Background|Method|Proposed|System|Approach|Framework|\d|$))',
        'Method': r'(?:^|\n)(?:\d+\.?\s*)?(?:Method(?:ology)?|METHODOLOGY|Proposed Method|Approach|System Description|Model(?:\s+Architecture)?|Framework)\n*(.*?)(?=\n(?:\d+\.?\s*)?(?:Experimental|Results|Evaluation|Discussion|Analysis|\d|$))',
        'Conclusion': r'(?:^|\n)(?:\d+\.?\s*)?Conclusion[s]?|CONCLUSION\n*(.*?)(?=\n(?:References|Bibliography|\d|$))'
    }
    
    # Extract each section using regex patterns
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            # Clean up the extracted text
            section_text = match.group(1).strip()
            # Remove any references like [1], [2,3], etc.
            section_text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', section_text)
            # Clean up multiple newlines
            section_text = re.sub(r'\n\s*\n', '\n\n', section_text)
            sections[section_name] = section_text

    return sections

def save_sections_to_md(sections, output_filename):
    """
    Save extracted sections to a markdown file.
    """
    with open(output_filename, 'w', encoding='utf-8') as f:
        for section_name, content in sections.items():
            if content:
                f.write(f'# {section_name}\n\n')
                f.write(f'{content}\n\n')

def process_paper(input_filename, output_filename):
    """
    Process a paper file and extract relevant sections.
    """
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract sections
        sections = extract_sections(content)
        
        # Save to markdown file
        save_sections_to_md(sections, output_filename)
        
        # Print status message
        print(f"Successfully processed {input_filename}")
        print("Extracted sections:")
        for section_name, content in sections.items():
            if content:
                print(f"- {section_name}")
            else:
                print(f"- {section_name} (not found)")
                
    except Exception as e:
        print(f"Error processing {input_filename}: {str(e)}")

def main():
    # Example usage
    input_file = "paper0.md"
    output_file = "extracted_sections.md"
    
    if os.path.exists(input_file):
        process_paper(input_file, output_file)
    else:
        print(f"Input file {input_file} not found.")

if __name__ == "__main__":
    main()
