
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from . import vector_store, openai_client
from .connectors import slack_connector, gdrive_connector

app = FastAPI(title='AI Corporate Suite - Expanded')

class DocIn(BaseModel):
    title: str
    text: str
    metadata: dict = {}

@app.post('/ingest')
async def ingest(docs: List[DocIn]):
    out=[]
    try:
        for d in docs:
            id = vector_store.upsert_document(d.title, d.text, d.metadata)
            out.append({'id':id, 'title':d.title})
        return {'ok':True, 'ingested': out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QueryIn(BaseModel):
    question: str
    k: int = 5

@app.post('/query_corporate_memory')
async def query(q: QueryIn):
    try:
        results = vector_store.query(q.question, k=q.k)
        # prepare contexts
        contexts = []
        for r in results:
            contexts.append({'id': r.get('id'), 'title': r.get('metadata',{}).get('title', r.get('id')), 'text': r.get('metadata',{}).get('text', r.get('text','')) or r.get('text','')})
        answer = openai_client.ask_with_context(q.question, contexts)
        return {'answer': answer, 'matches': results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/slack/pull/{channel_id}')
async def pull_channel(channel_id: str):
    try:
        docs = slack_connector.pull_channel(channel_id)
        return {'pulled': docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/gdrive/ingest')
async def gdrive_ingest(folder_id: str = None):
    try:
        files = gdrive_connector.list_and_ingest(folder_id)
        return {'ingested': files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
