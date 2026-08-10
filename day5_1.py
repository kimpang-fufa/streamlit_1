#import ollama
import streamlit as st
from groq import Groq

#when loading the file locally
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("groq_API_KEY")

#when loading the api key from streamlit secrets
API_KEY = st.secrets["groq_API_KEY"]


client = Groq(api_key=API_KEY)
#MODEL = "qwen2.5:3b"
MODEL = "llama-3.1-8b-instant"
question = input("Question: ")
msg = [{"role":"user", "content" : question}]
# response = ollama.chat(model=MODEL, messsages=msg)
response = client.chat.completions.create(model=MODEL, messages=msg)
# print("Answer:", response["message"]["content"])
print("Answer: ", response.choices[0].message.content)