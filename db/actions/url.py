
def get_most_recent_url():
    from db.models.url import Url
    return Url.select().filter(
        Url.state == Url.States.UNVISITED
    ).order_by(
        Url.created_at.asc()
    ).first()


def exists_any_unvisited_urls_in_snapshot(snapshot):
    from db.models.url import Url
    return Url.select().filter(
        Url.state == Url.States.UNVISITED
    ).filter(
        Url.snapshot == snapshot
    ).order_by(
        Url.created_at.asc()
    ).exists()


def exists_any_urls_waiting_to_be_indexed_in_snapshot(snapshot):
    from db.models.url import Url
    return Url.select().filter(
        Url.state == Url.States.WAITING_TO_INDEX
    ).filter(
        Url.snapshot == snapshot
    ).order_by(
        Url.created_at.asc()
    ).exists()


def find_url_with_href_sha_in_snapshot(href_sha: str, snapshot):
    from db.models.url import Url
    return Url.select().filter(
        Url.href_sha == href_sha
    ).filter(
        Url.snapshot == snapshot
    ).first()


def find_url_referencing_content_in_snapshot(snapshot, content):
    from db.models.url import Url
    return Url.select().filter(
        Url.content == content
    ).filter(
        Url.snapshot == snapshot
    ).first()
