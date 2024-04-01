
def find_cookie_by_identifier(identifier: str):
    from db.models import Cookie
    return Cookie.select().filter(Cookie.identifier == identifier).first()
