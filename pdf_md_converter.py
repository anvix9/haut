import logging
import time
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
from docling.document_converter import DocumentConverter, PdfFormatOption

log = logging.getLogger(__name__)

def is_folder_empty(folder_path: Path) -> bool:
    """
    Check if a folder is empty or contains no PDF files.
    
    Args:
        folder_path: Path to the folder to check
        
    Returns:
        bool: True if the folder is empty or has no PDFs, False otherwise
    """
    return not any(folder_path.glob("*.pdf"))

def process_pdf_folders(input_dir: Path, output_dir: Path, doc_converter: DocumentConverter) -> None:
    """
    Process PDF files from multiple folders, excluding 'archived_papers' and empty folders.
    
    Args:
        input_dir: Base input directory containing folders with PDFs
        output_dir: Output directory for markdown files
        doc_converter: Configured DocumentConverter instance
    """
    # Get all subdirectories except 'archived_papers'
    folders = [f for f in input_dir.iterdir() 
              if f.is_dir() and f.name != 'archived_papers']
    
    if not folders:
        log.warning(f"No valid folders found in {input_dir}")
        return
        
    for folder in folders:
        # Skip empty folders
        if is_folder_empty(folder):
            log.info(f"Skipping empty folder: {folder.name}")
            continue
            
        log.info(f"Processing folder: {folder.name}")
        
        # Process each PDF in the current folder
        for pdf_file in folder.glob("*.pdf"):
            log.info(f"Processing file: {pdf_file}")
            start_time = time.time()
            
            try:
                # Convert PDF
                conv_result = doc_converter.convert(pdf_file)
                if not hasattr(conv_result, "document") or not conv_result.document:
                    log.error(f"Conversion result is empty for file {pdf_file}. Skipping.")
                    continue
                
                # Create output filename with folder name prefix
                output_filename = f"{folder.name}_{pdf_file.stem}.md"
                output_file = output_dir / output_filename
                
                # Export to Markdown
                markdown_content = conv_result.document.export_to_markdown()
                with output_file.open("w", encoding="utf-8") as fp:
                    fp.write(markdown_content)
                    
                log.info(f"Markdown exported successfully to {output_file}.")
                
            except Exception as e:
                log.error(f"Error processing file {pdf_file}: {e}")
            finally:
                elapsed_time = time.time() - start_time
                log.info(f"Finished processing {pdf_file} in {elapsed_time:.2f} seconds.")

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Input and Output Directories
    input_dir = Path("./data/")
    output_dir = Path("./converted_markdowns/")
    
    if not input_dir.exists():
        log.error(f"Input directory {input_dir} does not exist. Exiting.")
        return
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Docling Parse with EasyOCR
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["en"]
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )
    
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    # Process all folders
    process_pdf_folders(input_dir, output_dir, doc_converter)

if __name__ == "__main__":
    main()
