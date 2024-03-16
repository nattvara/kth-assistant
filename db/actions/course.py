
def find_course_by_canvas_id(canvas_id: str):
    from db.models.course import Course
    return Course.select().filter(Course.canvas_id == canvas_id).first()
