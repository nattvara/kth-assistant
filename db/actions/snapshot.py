
def find_latest_snapshot_for_course(course: object):
    from db.models.snapshot import Snapshot
    return Snapshot.select().filter(
        Snapshot.course == course
    ).order_by(
        Snapshot.created_at.desc()
    ).first()


def all_snapshots_of_course_in_most_recent_order(course: object):
    from db.models.snapshot import Snapshot
    return Snapshot.select().filter(
        Snapshot.course == course
    ).order_by(
        Snapshot.created_at.desc()
    )
