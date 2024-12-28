import requests
import json
import os

def get_files(folder_path):
    "Get the path of a folder containing files and return a list of the file names."
    return os.listdir(folder_path)

def get_llama_question(section):
    _url = "http://127.0.0.1:11434/api/generate"
    _custom_prompt = f"Provide 2 questions that this section answers with high precision: {section}"
    _payload = {"model": "llama3-gradient", "prompt": _custom_prompt, "stream": False}
    
    _payload = json.dumps(_payload)
    
    response_data = None
    try:
        response = requests.post(_url, data=_payload)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.HTTPError as err:
        print("HTTP error", err)
    
    return response_data['response'] if response_data is not None else {'response': 'error in request or code.'}



## Get section of papers
previous_loc = ".."
current_loc = "."
root_folder = "paper_sections/"
files = get_files(os.path.join(previous_loc, root_folder))

all_questions = {}
for file in files:
    print(file)
    tmp_f = open(os.path.join(previous_loc, root_folder, file))
    tmp_json = json.load(tmp_f)
    tmp_json.pop()
    paper_questions = []
    for i in range(len(tmp_json)):
        tmp_section = tmp_json[i]['content']
        tmp_question = get_llama_question(tmp_section)
        print(tmp_json[i]['title'])
        paper_questions.append(tmp_question)

    tmp_paper_question = {file: paper_questions}
    tmp_paper_question = json.dumps(tmp_paper_question)
    #all_questions[file] = paper_questions

    with open(f"{previous_loc}/test_questions/{file}_questions.json", "w") as f:
        json.dump(tmp_paper_question, f, indent=4)

