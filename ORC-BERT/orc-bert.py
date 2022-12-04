from transformers import AutoTokenizer, AutoModelForMaskedLM
from difflib import SequenceMatcher
from spellchecker import SpellChecker
import torch
import requests
import base64
import json
import nltk
import re

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

#Predict words for mask using BERT; 
#refine prediction by matching with proposals from SpellChecker
def predict_word(text_original, text, suggestedwords):
    # Load, train and predict using pre-trained model
    tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
    tokenized_text = tokenizer.tokenize(text)
    # print(tokenized_text)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    # print(indexed_tokens)
    MASKIDS = [i for i, e in enumerate(tokenized_text) if e == '[MASK]']

    # Create the segments tensors
    segs = [i for i, e in enumerate(tokenized_text) if e == "."]
    segments_ids=[]
    prev=-1
    for k, s in enumerate(segs):
        segments_ids = segments_ids + [k] * (s-prev)
        prev=s
    segments_ids = segments_ids + [len(segs)] * (len(tokenized_text) - len(segments_ids))
    segments_tensors = torch.tensor([segments_ids])
    # prepare Torch inputs 
    tokens_tensor = torch.tensor([indexed_tokens])
    # Load pre-trained model
    model = AutoModelForMaskedLM.from_pretrained('neuralmind/bert-base-portuguese-cased')
    # Predict all tokens
    with torch.no_grad():
        predictions = model(tokens_tensor, segments_tensors)

    
    # Todo: investigar erro no acesso ao predictions  
    for i in range(len(MASKIDS)):
        preds = torch.topk(predictions[0][0][MASKIDS[i]], k=50) 
        indices = preds.indices.tolist()
        list1 = tokenizer.convert_ids_to_tokens(indices)
        list2 = suggestedwords[i]
        simmax=0
        predicted_token=''
        for word1 in list1:
            for word2 in list2:
                s = SequenceMatcher(None, word1, word2).ratio()
                if s is not None and s > simmax:
                    simmax = s
                    predicted_token = word1
        text_original = text_original.replace('[MASK]', predicted_token, 1)
    return text_original


def maskWord(personsList, text, text_original):
    ignorewords = personslist + ["!", ",", ".", "\"", "?", '(', ')', '*', "'"]
    # using enchant.checker.SpellChecker, identify incorrect words
    d = SpellChecker('pt')
    words = text.split()
    incorrectwords = [w for w in words if not w in d and w not in ignorewords]
    # using enchant.checker.SpellChecker, get suggested replacements
    suggestedwords = []
    for w in incorrectwords:
        candidatesWord = d.candidates(w)
        if candidatesWord:
            for s in candidatesWord:
                suggestedwords.append(s)
                break
        else:
            suggestedwords.append(w)
    # replace incorrect words with [MASK]
    print(suggestedwords)
    for w in incorrectwords:
        text = text.replace(w, '[MASK]')
        text_original = text_original.replace(w, '[MASK]')
        
    return text, text_original, suggestedwords
    
def get_personslist(text):
    personslist=[]
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent, language='portuguese'))):
            if isinstance(chunk, nltk.tree.Tree) and chunk.label() == 'PERSON' or  isinstance(chunk, nltk.tree.Tree) and chunk.label() == 'ORGANIZATION':
                personslist.insert(0, (chunk.leaves()[0][0]))         
    return list(set(personslist))

def cleanText(text):
        # cleanup text
    rep = { '\n': ' ', '\\': ' ', '\"': '"', '-': ' ', '"': ' " ', 
            '"': ' " ', '"': ' " ', ',':' , ', '.':' . ', '!':' ! ', 
            '?':' ? ', "n't": " not" , "'ll": " will", '*':' * ', 
            '(': ' ( ', ')': ' ) ', "s'": "s '"}
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text
    
def ocrGoogleVisionApi(image):
    with open(image, "rb") as img_file:
        my_base64 = base64.b64encode(img_file.read())
        

    url = "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyCY7LMQz4n_a54sjFl54nmzMLoXFJFybKY"
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

    texts = r.json()['responses'][0]['textAnnotations']
    results = []

    for t in texts:
        results.append(t['description'])
     
    text = ''    
    for word in results:
        text+= word + ' ' 
        
    return text 

if __name__ == "__main__":
    source = "example.jpg"
    text = ocrGoogleVisionApi(source)
    text_original = str(text)
    text = cleanText(text)
    personslist = get_personslist(text)
    text, text_original, suggestedwords = maskWord(personslist,text,text_original)

    output = predict_word(text_original, text, suggestedwords)
    print(output)
