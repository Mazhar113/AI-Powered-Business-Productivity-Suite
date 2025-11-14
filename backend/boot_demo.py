
# bootsrap demo docs into the backend (call after starting backend)
import requests, time
docs = [
    {"title":"Pricing Decision 2022","text":"We changed pricing due to churn among SMEs and rising CAC. Tiered pricing approved.","metadata":{"source":"email","date":"2022-07-01"}},
    {"title":"Customer Research Q2 2022","text":"SME customers sensitive to annual pricing; recommend trial periods.","metadata":{"source":"doc","date":"2022-06-15"}},
    {"title":"Board Minutes July 2022","text":"Decision: Move to tiered pricing and adjust discounts for enterprise accounts.","metadata":{"source":"meeting","date":"2022-07-02"}}
]
resp = requests.post('http://localhost:8000/ingest', json=docs)
print(resp.json())
