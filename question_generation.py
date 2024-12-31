from os.path import join
import requests
import re
import json
import os

def get_topics(content):
    """Extract main topics from the paper content using LLaMA."""
    _url = "http://127.0.0.1:11434/api/generate"
    print("Extracting topics...")
    
    _custom_prompt = (
        f"Based on this paper content, identify the main key words and topics or research areas it addresses. "
        f"Return ONLY a list of 3-7 specific research key words, topics or subfields emphasizing the techniques, etc... (like 'Natural Language Processing', "
        f"'Computer Vision', 'Reinforcement Learning', 'DPO', etc.). "
        f"Format the response as a Python list of strings. Example format: ['Topic1', 'Topic2', 'Topic3']. "
        f"Content: {content}"
    )
    
    _payload = {
        "model": "saish_15/tethysai_research",
        "prompt": _custom_prompt,
        "stream": False,
        "options": {"num_ctx": 6000},
        "keep_alive": -1
    }
    
    try:
        response = requests.post(_url, data=json.dumps(_payload))
        response.raise_for_status()
        response_data = response.json()
        
        # Clean the response to ensure it's a valid Python list
        topics_str = response_data['response'].strip()
        # Remove any markdown formatting if present
        topics_str = re.sub(r'```python|```', '', topics_str).strip()
        # Convert string representation of list to actual list
        topics = eval(topics_str)
        return topics
    except Exception as e:
        print(f"Error extracting topics: {str(e)}")
        return ["Topic extraction failed"]

def get_llama_question(section, theme):
    """Generate questions based on the section content and theme using LLaMA."""
    _url = "http://127.0.0.1:11434/api/generate"
    print(f"generate questions for {theme}...")
    
    if theme == 'research':
        _custom_prompt = (
            f"Read the sections carefully and summarize the main research question the authors are addressing. "
            f"Focus on identifying the problem they aim to solve, the motivations behind the study, and any "
            f"explicit or implicit questions they raise in the introduction or abstract or in this passage. YOU MUST ANSWER the main question 'WHY'"
            f"Simply take the results contribution and convert it into a Research Problem transparently."
            f"Provide the research question in clear and concise terms with high precision. "
            f"IMPORTANT: Do not generate questions like : What is the primary problem addressed by this research paper?, Or What motivates the development of this solution, and what are the costs associated with LLM serving systems? You need to generate full question by writitng exactly the name of the techniques and not refer it as 'this, the proposed solutions, exisiting or current solution, etc...'"
            f"The questions must follow this - Q1: ....? etc, Contribution:.... : {section}"
        )
    elif theme == 'method':
        _custom_prompt = (
            f"Analyze the methodology section of the paper and summarize the key methodological approach "
            f"used by the authors. Highlight the data, techniques, models, or tools employed to address "
            f"the research question. Identify any specific hypotheses tested, experimental setups, or "
            f"computational methods, and explain how these align with the research objectives.YOU MUST ANSWER the main question 'HOW' . "
            f"The answer must follow this - Methodology:.....: {section}"
        )
    else: 
        _custom_prompt = (
            f"Examine this results section of the paper and summarize (Do not be long, just mention the main results) "
            f"the key findings reported by the authors. Highlight the outcomes of experiments, the performance "
            f"of any models or methodologies, or the validation of hypotheses. Focus on quantitative metrics, "
            f"qualitative observations, or comparative analyses provided. Explain how these results contribute "
            f"to addressing the research question and advancing the field from the paper. "
            f"The answer must follow this - Results:.....: {section}"
        )

    _payload = {
        "model": "saish_15/tethysai_research",
        "prompt": _custom_prompt,
        "stream": False,
        "options": {"num_ctx": 6000},
        "keep_alive": -1
    }
    
    try:
        response = requests.post(_url, data=json.dumps(_payload))
        response.raise_for_status()
        response_data = response.json()
        return response_data['response']
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
        return "Error in request or code."

def extract_markdown_sections(file_path, section_titles):
    """Extract specific sections from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return {}, ""
    
    # Separate "Abstract" from other titles
    abstract_pattern = r'##\s*Abstract'
    other_titles = [title for title in section_titles if title.lower() != 'abstract']
    
    # Create pattern for numbered sections
    numbered_pattern = r'##\s*(?:\d+\.?\s*)*({titles})'
    other_titles_pattern = '|'.join(map(re.escape, other_titles))
    
    # Combine patterns for both Abstract and numbered sections
    if 'Abstract' in section_titles:
        full_pattern = f'(?:{abstract_pattern}|{numbered_pattern.format(titles=other_titles_pattern)})(.*?)(?=##|\Z)'
    else:
        full_pattern = f'{numbered_pattern.format(titles=other_titles_pattern)}(.*?)(?=##|\Z)'
    
    # Find all matches with case-insensitive flag
    matches = re.finditer(full_pattern, content, re.DOTALL | re.IGNORECASE)
    
    # Store matches in a dictionary with section title as key
    extracted_sections = {}
    for match in matches:
        section_content = match.group(2).strip()
        header = match.group(0).split('\n')[0]
        clean_header = re.sub(r'^##\s*(?:\d+\.?\s*)*', '', header).strip()
        extracted_sections[clean_header] = section_content
    
    return extracted_sections, content

def process_markdown_files(input_folder, output_folder):
    """Process all markdown files in the input folder and generate analysis JSON files."""
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Define section categories
    research_question_sections = [
        "Abstract", "Introduction", "Conclusion", "goals", "Motivation", "Motivations", 
        "overview", "problem statement", "research problem", "objectives", "aims", "objective",
        "main"
    ]
    method_questions = [
        "Method", "Methods", "architecture", "Abstract", "study", "studies", 
        "methodologies", "approach", "approaches", "preliminary", "preliminaries",
        "Technical specifications", "Specifications","Problem-setup", "Pre-training",
        "experimental setup","approximate methods","procedure", "ablations", "ablation study", "Model", "Dataset",
        "details", "evaluation tasks", "data construction", "inference","field architecture", "implementation study", "setup"
        "experiment settings", "design recipes","method and data collection", "Materials", "discussions"
    ]

    results_question_sections = [
        "conclusion", "discussion", "study", "studies", "future work", 
        "Summary", "Abstract", "future directions","Limitation", "limitations", "limitation",
         "analysis",  "evaluations", "Broader impacts", "impact", "impacts", 
        "objectives",  "main results", "evaluations", "training principles", "summary statistics", "conclusions, limitations, and discussion",
        "limitations and future works", "limitation and future work", "conclusion and discussion"
    ]
    themes = ['research', 'method', 'results']
    
    # Get all markdown files in the input folder
    markdown_files = [f for f in os.listdir(input_folder) if f.endswith('.md')]
    iter_ = 0 
    for md_file in markdown_files:
        iter_ +=1
        print(f"Processing {md_file}... | {iter_}/{len(markdown_files)}")
        file_path = os.path.join(input_folder, md_file)
        
        complete = {}
        research_content = ""  # Store research sections for topic extraction
        
        # First process research sections to get topics
        sections, _ = extract_markdown_sections(file_path, research_question_sections)
        if sections:
            research_content = "\n\n".join(sections.values())
            # Extract topics from research content
            topics = get_topics(research_content)
            complete["topics"] = topics
        
        # Then process all themes
        for theme in themes:
            if theme == "research":
                # Reuse already extracted research sections
                tmp_contents = research_content
            elif theme == "method":
                sections, _ = extract_markdown_sections(file_path, method_questions)
                tmp_contents = "\n\n".join(sections.values()) if sections else ""
            elif theme == "results":
                sections, _ = extract_markdown_sections(file_path, results_question_sections)
                tmp_contents = "\n\n".join(sections.values()) if sections else ""

            if tmp_contents:  # Only process if sections were found
                res = get_llama_question(tmp_contents, theme)
                complete[theme] = res
            else:
                complete[theme] = "No relevant sections found"
        
        # Create output filename
        output_filename = os.path.splitext(md_file)[0] + '_analysis.json'
        output_path = os.path.join(output_folder, output_filename)
        
        # Save results to JSON file
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(complete, outfile, indent=4)
        
        print(f"Saved analysis for {md_file} to {output_filename}")

# Example usage
if __name__ == "__main__":
    input_folder = "./converted_markdown_trends"  # Folder containing markdown files
    output_folder = "./paper_analysis"  # Folder where JSON files will be saved
    
    process_markdown_files(input_folder, output_folder)
    print("Processing complete!")
