from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
openAIclient = OpenAI(api_key=api_key)

def gpt_4_submit(instruction):
    
    messages = [
            {"role": "user", "content": f"{instruction}"},
        ]
    print("creating code........")    
    response = openAIclient.chat.completions.create(    
        model="gpt-4-turbo",
        temperature=0,
        messages=messages
    )

    return response.choices[0].message.content