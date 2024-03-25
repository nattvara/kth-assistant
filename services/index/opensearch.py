from opensearchpy import OpenSearch
import config.settings as settings


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
