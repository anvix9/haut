import logging
import time
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)

    # Input and Output Directories
    input_dir = Path("./academic/papers/")
    output_dir = Path("./converted_markdown_trends/")

    if not input_dir.exists():
        _log.error(f"Input directory {input_dir} does not exist. Exiting.")
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

    # Process each PDF in the input directory
    for pdf_file in input_dir.glob("*.pdf"):
        _log.info(f"Processing file: {pdf_file}")
        start_time = time.time()
        try:
            # Convert PDF
            conv_result = doc_converter.convert(pdf_file)
            if not hasattr(conv_result, "document") or not conv_result.document:
                _log.error(f"Conversion result is empty for file {pdf_file}. Skipping.")
                continue

            # Export to Markdown
            markdown_content = conv_result.document.export_to_markdown()
            output_file = output_dir / f"{pdf_file.stem}.md"
            with output_file.open("w", encoding="utf-8") as fp:
                fp.write(markdown_content)

            _log.info(f"Markdown exported successfully to {output_file}.")
        except Exception as e:
            _log.error(f"Error processing file {pdf_file}: {e}")
        finally:
            elapsed_time = time.time() - start_time
            _log.info(f"Finished processing {pdf_file} in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()

