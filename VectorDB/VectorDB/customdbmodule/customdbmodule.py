import os
import csv
from openai import OpenAI

import numpy as np
from pprint import pprint
from models import *
from modulemanager import Module
from modulemanager import classregistry
from dotenv import load_dotenv

load_dotenv()

openAIclient = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@classregistry.register('customdb', )
class CustomdbModule2():
    def __init__(self, name):
        self.name = name
        self.faq_db = []

    def load(self, file):
        with open(file.path, 'r', encoding='utf-8') as fp:
            cr = csv.reader(fp)
            next(cr)

            for row in cr:
                # row: id,question,answer
                text = "Question: " + row[1] + "\nAnswer: " + row[2] + "\n"
                vector = self.get_embedding(text)
                doc = {'id': row[0], 'vector': vector,
                    'question': row[1], 'answer': row[2]}
                self.faq_db.append(doc)

        return "loading ok"

    def get_embedding(self, content, model='text-embedding-ada-002'):
        response = openAIclient.embeddings.create(input=content, model=model)
        vector = response.data[0].embedding
        return vector

    def similarity(self, v1, v2):  # return dot product of two vectors
        return np.dot(v1, v2)

    def query(self, query):
        results = []

        vector = self.get_embedding(query.query)

        for doc in self.faq_db:
            score = self.similarity(vector, doc['vector'])
            results.append(
                {'id': doc['id'], 'score': score, 'question': doc['question'], 'answer': doc['answer']})

        results = sorted(results, key=lambda e: e['score'], reverse=True)

        print(results[:query.top_k])
        return results[:query.top_k]

if __name__ == '__main__':
    db = CustomdbInterfece2("customdb")
    file = File(path='./File/prompt-faq.csv')

    faq_db = db.load(file)
    # print(faq_db)
    # print(faq_db)

    query = Query(query="ReAct가 뭔가요?", top_k = 2)
    print(query.query)
    #vector = db.get_embedding(query)
    # print(question, vector)

    result = db.query(query)
    pprint(result)