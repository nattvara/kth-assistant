from services.index.chunks import split_text_with_overlap
import services.index.opensearch as search
from db.models import Url


class IndexService:

    def __init__(self):
        self.client = search.get_client()

    def index_url(self, url: Url):
        if not search.index_exists(self.client, url.snapshot.id):
            search.create_index(self.client, url.snapshot.id)

        chunks = split_text_with_overlap(url.content.text)
        for idx, chunk in enumerate(chunks):
            search.index_document(self.client, url.snapshot, f"{url.id}-{idx}", {
                'name': url.content.name,
                'text': chunk,
                'url': url.href,
            })

        url.refresh()
        url.state = Url.States.INDEXED
        url.save()
