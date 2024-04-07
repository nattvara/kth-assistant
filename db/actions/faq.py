
def find_faq_by_public_id(faq_id: str):
    from db.models.faq import Faq
    return Faq.select().filter(
        Faq.faq_id == faq_id
    ).first()
