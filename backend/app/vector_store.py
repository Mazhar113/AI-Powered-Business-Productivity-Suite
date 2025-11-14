
# vector_store.py
# Provides a simple interface: upsert_document(title, text, metadata) and query(text, k)
import os
import json
import numpy as np
from typing import List, Dict
from . import config

USE_PINECONE = bool(config.PINECONE_API_KEY)

if USE_PINECONE:
    import pinecone
    pinecone.init(api_key=config.PINECONE_API_KEY, environment=config.PINECONE_ENV)
    INDEX_NAME = config.PINECONE_INDEX
    if INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(INDEX_NAME, dimension=1536)
    index = pinecone.Index(INDEX_NAME)

from . import openai_client

# Simple SQLite fallback
import sqlite3
DB_PATH = 'ai_corp_full.db'
def init_sqlite():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, title TEXT, text TEXT, metadata TEXT, embedding TEXT)')
    conn.commit()
    conn.close()

if not USE_PINECONE:
    init_sqlite()

def upsert_document(title: str, text: str, metadata: Dict):
    emb = openai_client.embed_text(text)
    meta = metadata or {}
    if USE_PINECONE:
        id = meta.get('id') or str(np.random.randint(1_000_000, 9_999_999))
        index.upsert([(id, emb, {"title": title, "text": text, **meta})])
        return id
    else:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO documents (title,text,metadata,embedding) VALUES (?,?,?,?)', (title, text, json.dumps(meta), json.dumps(emb)))
        doc_id = c.lastrowid
        conn.commit()
        conn.close()
        return str(doc_id)

def _sqlite_all():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, text, metadata, embedding FROM documents')
    rows = c.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({"id": str(r[0]), "title": r[1], "text": r[2], "metadata": json.loads(r[3] or "{}"), "embedding": json.loads(r[4])})
    return out

def query(query_text: str, k: int = 5):
    q_emb = openai_client.embed_text(query_text)
    if USE_PINECONE:
        res = index.query(q_emb, top_k=k, include_metadata=True)
        items = []
        for m in res['matches']:
            items.append({"id": m['id'], "score": m['score'], "metadata": m.get('metadata')})
        return items
    else:
        rows = _sqlite_all()
        def cosine(a,b):
            a=np.array(a); b=np.array(b)
            return float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
        scored = []
        for r in rows:
            sc = cosine(q_emb, r['embedding'])
            scored.append((sc, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for sc, r in scored[:k]:
            out.append({"id": r['id'], "score": sc, "metadata": r['metadata'], "title": r['title'], "text": r['text']})
        return out
