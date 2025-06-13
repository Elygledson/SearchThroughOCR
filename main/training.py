from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import spacy
from tqdm import tqdm 

class ModelNLP:
    def __init__(self, model, TRAIN_DATA):
        self.model = model
        self.TRAIN_DATA = TRAIN_DATA

    def loadModel(self):
        model = self.model
        output_dir=Path("C:\\Users\\nithi\\Documents\\ner")
        n_iter=100

        if self.model is not None:
            nlp = spacy.load(self.model)  
            print("Loaded model '%s'" % self.model)
        else:
            nlp = spacy.blank('pt_core_news_sm')  
            print("Created blank 'pt_core_news_sm' model")

        trainModel(TRAIN_DATA)

    def trainModel(self):
        #Set up the pipeline
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner, last=True)
        else:
            ner = nlp.get_pipe('ner')

        for _, annotations in self.TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

        #Train the Recognizer
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        with nlp.disable_pipes(*other_pipes):  # only train NER
            optimizer = nlp.begin_training()
            for itn in range(n_iter):
                random.shuffle(TRAIN_DATA)
                losses = {}
                for text, annotations in tqdm(TRAIN_DATA):
                    nlp.update(
                        [text],  
                        [annotations],  
                        drop=0.5,  
                        sgd=optimizer,
                        losses=losses)
                print(losses)
        print('Finished')

    def TestModel(self):
        #Test the trained model
        for text, _ in self.TRAIN_DATA:
        doc = nlp('Oi, meu nome é João. Como vais?')
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    def saveModel():
    #Save the model
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir) 
            
    def testSavedModel():
        #Test the model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
            print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
