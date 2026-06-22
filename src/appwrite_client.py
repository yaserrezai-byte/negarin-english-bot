from appwrite.client import Client
from appwrite.services.databases import Databases

_client = None
_databases = None

def get_client():
    global _client
    if _client is None:
        import config
        _client = Client()
        _client.set_endpoint(config.APPWRITE_ENDPOINT)
        _client.set_project(config.APPWRITE_PROJECT_ID)
        _client.set_key(config.APPWRITE_API_KEY)
    return _client

def get_databases():
    global _databases
    if _databases is None:
        _databases = Databases(get_client())
    return _databases
