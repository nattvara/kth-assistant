
def test_user_courses_user_can_administrate_are_returned_in_list_of_courses(
    api_client,
    valid_course,
    authenticated_session,
):
    authenticated_session.session.admin_courses.append(valid_course.canvas_id)
    authenticated_session.session.save()

    response = api_client.get('/admin/courses', headers=authenticated_session.headers)
    assert response.status_code == 200
    assert response.json()['courses'][0]['canvas_id'] == valid_course.canvas_id
