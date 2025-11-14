
import os
import openai
from .config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

EMBED_MODEL = 'text-embedding-3-small'
CHAT_MODEL = 'gpt-4o-mini'

def embed_text(text):
    resp = openai.Embedding.create(model=EMBED_MODEL, input=text)
    return resp['data'][0]['embedding']

def ask_with_context(question, contexts, max_tokens=500):
    prompt = "You are a helpful corporate assistant. Use the sources below and answer concisely with citations.\n\n"
    for c in contexts:
        prompt += f"[doc_{c.get('id')}] {c.get('title')}:\n{c.get('text')[:2000]}\n---\n"
    prompt += f"\nQuestion: {question}\nAnswer:" 
    resp = openai.ChatCompletion.create(model=CHAT_MODEL, messages=[{'role':'user','content':prompt}], max_tokens=max_tokens)
    return resp['choices'][0]['message']['content']
