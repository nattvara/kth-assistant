from typing import List

from opensearchpy import OpenSearch
import config.settings as settings
from config.logger import log


class Document:

    def __init__(self, name: str, url: str, text: str):
        self.name = name
        self.url = url
        self.text = text


def get_client():
    client = OpenSearch(
        hosts=[{'host': settings.get_settings().OPENSEARCH_HOST, 'port': settings.get_settings().OPENSEARCH_PORT}],
        http_compress=True,
        http_auth=(settings.get_settings().OPENSEARCH_USERNAME, settings.get_settings().OPENSEARCH_PASSWORD),
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    return client


def health_check(client: OpenSearch):
    info = client.info()
    return info['cluster_name']


def index_exists(client: OpenSearch, index_name: str) -> bool:
    return client.indices.exists(index=index_name)


def create_index(client: OpenSearch, index_name: str):
    log().info(f"creating index: {index_name}")
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 1,
                'number_of_replicas': 0,
            },
        },
        'mappings': {
            'properties': {
            }
        }
    }
    client.indices.create(
        index=index_name,
        body=index_body,
        ignore=[400, 404],
    )


def index_document(client: OpenSearch, index_name: str, doc_id: str, body: dict) -> str:
    log().info(f"add document with id '{doc_id}' to index '{index_name}'")
    client.index(
        index=index_name,
        id=doc_id,
        body=body,
        refresh=True,
    )


def search_index(client: OpenSearch, index_name: str, query_string: str, max_docs: int = 4) -> List[Document]:
    log().info(f"searching index '{index_name}'")

    query = {
        'query': {
            'multi_match': {
                'query': query_string,
                'fields': [
                    'text',
                    'name'
                ]
            }
        },
        'size': max_docs,
        '_source': False,
        'fields': ['text', 'name', 'url']
    }

    res = client.search(index=index_name, body=query)

    out = []
    for doc in res['hits']['hits']:
        out.append(Document(
            doc['fields']['name'][0],
            doc['fields']['url'][0],
            doc['fields']['text'][0],
        ))

    return out
