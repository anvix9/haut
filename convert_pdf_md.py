"""This script is a temporary script for converting many Pdfs to 
markdown using Marker sequentially."""

import os
import subprocess
import sys

def get_files(folder_path):
    """Get the path of a folder containing PDFs and return a list of the file names."""
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return []
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

def main():
    current_loc = "."
    root_folder = "academic/papers/"
    marker_folder = "markerx/"
    output_folder = f"{current_loc}/{root_folder}"
    
    # Get list of PDFs
    pdfs = get_files(output_folder)
    if not pdfs:
        print("No PDF files found in the folder.")
        return
    
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Convert PDFs into Markdown
    for pdf in pdfs:
        tmp_name = os.path.splitext(pdf)[0]  # Get file name without extension
        input_path = os.path.join(root_folder, pdf)
        output_path = os.path.join(root_folder, f"{tmp_name}.md")
        
        command = (
            f"cd {marker_folder} && poetry run {sys.executable} ./convert_single.py "
            f"../{input_path} ../{output_path} --parallel_factor 2"
        )
        
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully converted: {pdf}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while processing {pdf}: {e}")

if __name__ == "__main__":
    main()

