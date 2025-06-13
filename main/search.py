from api_secrets import API_KEY_OPENAI, API_KEY_GOOGLE
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from time import sleep
from tqdm import tqdm
from io import BytesIO
import requests
import openai
import base64
import json
import csv
import sys
import os


def spreadSheet(spreadSheetTitle, data):
    if os.path.exists(f'spreadsheet\{spreadSheetTitle}.csv') == False:
        with open(f'spreadsheet\{spreadSheetTitle}.csv', 'w', encoding='utf-8', newline='') as f:
            header = csv.writer(f,delimiter=';')
            header.writerow(['Nº TÍTULO','NOME', 'CPF','RG', 'DOCUMENTO', 'MUNICÍPIO', 'ÁREA (ha)'])
            header.writerow(data)
    else:
        with open(f'spreadsheet\{spreadSheetTitle}.csv', 'a', encoding='utf-8', newline='') as f:
            line = csv.writer(f,delimiter=';')
            line.writerow(data)

    """
    @desc: this function extracts main information from text
    
    @params:
        - file: the command to execute this process
    
    @returns:
        - the requested textual content
    """

def chatGPT(prompt):
    tokens = len(prompt) + 100
    if tokens <= 4097:
        openai.api_key = API_KEY_OPENAI
        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
        return response['choices'][0]['text'].strip().split('\n')
    else:
        return ['Nome: ;','CPF: ;','RG: ;','Documento: ;','Área em hectares: ']
        
    

def get_max_str_index(lst):
    return max(enumerate(lst), key=lambda x: len(x[1]))

def ocrGoogleVisionApi(my_base64):
    url = f'https://vision.googleapis.com/v1/images:annotate?key={API_KEY_GOOGLE}'
    data = {
        'requests': [
            {
                'image': {
                    'content': my_base64.decode('utf-8')
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION'
                    }
                ]
            }
        ]
    }
    r = requests.post(url=url, data=json.dumps(data))
    text = r.json()['responses'][0]['fullTextAnnotation']['text']
    result = get_max_str_index(text.split('.\n'))
    return result[1].replace('\n','')

def convert_pdf_to_img(pdf_file):
    pages = convert_from_path(pdf_file)
    buffered = BytesIO()
    if len(pages) > 1:
        pages[1].save(buffered, format="JPEG")
    else:
        pages[0].save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str

def extractTextFromPdf(filename):
    reader = PdfReader(filename)
    page = reader.pages[1]
    return page.extract_text()

def openDirectory(path,method):
    try:       
        documentTitle = path.split('/')[-1]
        dir_list = tqdm(os.listdir(path))
        for numberTitle in dir_list:
                image = convert_pdf_to_img(path + '/' + numberTitle)
                text = method(image)
                output = chatGPT('Extraia apenas nome, cpf, rg, documento e área em hectares do texto\n' + text)
                sleep(0.1)
                spreadSheet(documentTitle, [numberTitle] + output)
                dir_list.set_description(f"{numberTitle}")
    except NameError:
        print(NameError)

def main(command):
    if command[1] == '-i':
      openDirectory(command[2], ocrGoogleVisionApi)
    elif command[1] == '-f':
      openDirectory(command[2], extractTextFromPdf)

if __name__ == "__main__":
    main(sys.argv)