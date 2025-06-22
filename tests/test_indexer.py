import os
from pathlib import Path
from unittest.mock import patch
import pytest

from smart_indexer import SmartDocumentIndexer


@pytest.fixture
def indexer(tmp_path):
    # Avoid network calls during initialization
    with patch.object(SmartDocumentIndexer, '_init_qa_model', lambda self: setattr(self, 'llm_type', 'internal')):
        idx = SmartDocumentIndexer()
    idx.index_file = str(tmp_path / 'index.json')
    # Avoid max_df/min_df issues with single document
    idx.vectorizer.max_df = 1.0
    return idx


def test_chunk_text(indexer):
    text = 'a' * 4500
    chunks = indexer._chunk_text(text, chunk_size=2000, overlap=400)
    assert len(chunks) == 3
    assert chunks[0] == text[:2000]
    # Second chunk should overlap with first
    assert chunks[1].startswith(text[1600:1610])


def test_index_and_search(indexer, tmp_path):
    doc = tmp_path / 'doc.txt'
    doc.write_text('Este documento possui informacao relevante sobre testes.')
    indexer.index_directory(tmp_path)
    assert len(indexer.documents) == 1
    assert indexer.document_vectors is not None

    with patch.object(indexer, '_answer_question', return_value={'answer': 'resp', 'confidence': 0.9}):
        results = indexer.search('informacao')
    assert results
    assert results[0]['ai_answer'] == 'resp'


def test_generate_natural_answer(indexer):
    context = 'A reuniao ocorreu em 12/01/2024. Participou Joao Silva.'
    answer = indexer._generate_natural_answer('Quando foi a reuniao?', context)
    assert '12/01/2024' in answer['answer']
    assert answer['confidence'] > 0.5


def test_get_stats(indexer, tmp_path):
    doc = tmp_path / 'doc.txt'
    doc.write_text('teste basico')
    indexer.index_directory(tmp_path)
    stats = indexer.get_stats()
    assert stats['total_documents'] == 1
    assert 'model_status' in stats
