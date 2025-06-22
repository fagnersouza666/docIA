import importlib
from unittest.mock import patch
import pytest

from smart_indexer import SmartDocumentIndexer


@pytest.fixture
def app_client(tmp_path):
    # Prepare an indexer without external dependencies
    with patch.object(SmartDocumentIndexer, '_init_qa_model', lambda self: setattr(self, 'llm_type', 'internal')):
        smart_app = importlib.import_module('smart_app')
        my_indexer = SmartDocumentIndexer()
    my_indexer.index_file = str(tmp_path / 'index.json')
    my_indexer.vectorizer.max_df = 1.0
    doc = tmp_path / 'doc.txt'
    doc.write_text('conteudo para busca de testes')
    my_indexer.index_directory(tmp_path)
    smart_app.indexer = my_indexer
    with smart_app.app.test_client() as client:
        yield client, my_indexer


def test_stats_endpoint(app_client):
    client, idx = app_client
    resp = client.get('/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['total_documents'] == 1


def test_search_endpoint(app_client):
    client, idx = app_client
    with patch.object(idx, 'search', return_value=[{'ai_answer': 'ok', 'confidence': 1.0}]):
        resp = client.post('/search', json={'query': 'teste'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['results'][0]['ai_answer'] == 'ok'


def test_index_endpoint(app_client):
    client, idx = app_client
    with patch.object(idx, 'index_directory') as mock_index:
        resp = client.post('/index')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    mock_index.assert_called()
