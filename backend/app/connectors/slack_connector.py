
# slack_connector.py
# Example: list channel messages and return as documents to upsert into vector store.
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..config import SLACK_BOT_TOKEN
from ..vector_store import upsert_document

client = WebClient(token=SLACK_BOT_TOKEN)

def pull_channel(channel_id, limit=200):
    try:
        res = client.conversations_history(channel=channel_id, limit=limit)
        messages = res['messages']
        docs = []
        for m in messages:
            text = m.get('text', '')
            user = m.get('user')
            ts = m.get('ts')
            title = f"Slack:{channel_id}:{ts}"
            metadata = {'source':'slack', 'channel': channel_id, 'user': user, 'ts': ts}
            upsert_document(title, text, metadata)
            docs.append(title)
        return docs
    except SlackApiError as e:
        raise
