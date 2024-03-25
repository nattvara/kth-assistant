
def find_content_with_sha(sha: str):
    from db.models.content import Content
    return Content.select().filter(
        Content.sha == sha
    ).first()
