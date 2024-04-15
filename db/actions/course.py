
def find_course_by_canvas_id(canvas_id: str):
    from db.models.course import Course
    return Course.select().filter(Course.canvas_id == canvas_id).first()


def find_course_by_admin_token(admin_token: str):
    from db.models.course import Course
    return Course.select().filter(Course.admin_token == admin_token).first()
