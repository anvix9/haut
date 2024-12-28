import os
from markitdown import MarkItDown
from pathlib import Path

def convert_pdfs_to_markdown(input_dir, output_dir):
    """
    Convert all PDFs in input directory to markdown files in output directory.
    
    Args:
        input_dir (str): Path to directory containing PDF files
        output_dir (str): Path to directory where markdown files will be saved
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize converter
    md = MarkItDown()
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            # Construct full input path
            input_path = os.path.join(input_dir, pdf_file)
            
            # Create output filename (replace .pdf with .md)
            output_filename = os.path.splitext(pdf_file)[0] + '.md'
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"Converting {pdf_file}...")
            
            # Convert PDF to markdown
            result = md.convert(input_path)
            
            # Save markdown content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            print(f"Successfully converted {pdf_file} to {output_filename}")
            
        except Exception as e:
            print(f"Error converting {pdf_file}: {str(e)}")
            continue

def main():
    # Define directories
    current_dir = os.getcwd()
    input_dir = os.path.join(current_dir, 'papers')
    output_dir = os.path.join(current_dir, 'papers_converted')
    
    print("Starting PDF to Markdown conversion...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Convert all PDFs
    convert_pdfs_to_markdown(input_dir, output_dir)
    
    print("\nConversion process completed!")
    
    # Print summary of converted files
    if os.path.exists(output_dir):
        converted_files = [f for f in os.listdir(output_dir) if f.endswith('.md')]
        print(f"\nTotal files converted: {len(converted_files)}")
        print("Converted files:")
        for file in converted_files:
            print(f"- {file}")

main()
