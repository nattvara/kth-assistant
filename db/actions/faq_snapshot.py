
def find_latest_faq_snapshot_for_course(course: object):
    from db.models.faq_snapshot import FaqSnapshot
    return FaqSnapshot.select().filter(
        FaqSnapshot.course == course
    ).order_by(
        FaqSnapshot.created_at.desc()
    ).first()
