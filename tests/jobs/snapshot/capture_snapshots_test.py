import pytest
import arrow

from jobs.snapshot.capture_snapshots import job
from db.models import Course, Snapshot


@pytest.mark.asyncio
async def test_capture_snapshot_creates_new_snapshots_for_courses_where_snapshots_does_not_exists():
    course_1 = Course(canvas_id='47414')
    course_1.save()

    assert not Snapshot.select().filter(Snapshot.course == course_1).exists()

    await job()

    assert Snapshot.select().filter(Snapshot.course == course_1).exists()


@pytest.mark.asyncio
async def test_capture_snapshot_creates_new_snapshot_if_most_recent_snapshot_is_expired(mocker):
    mocked_time = arrow.get('2024-03-24T00:00:00Z')

    with mocker.patch('arrow.now', return_value=mocked_time):
        course_1 = Course(canvas_id='47414', snapshot_lifetime_in_mins=60)
        course_1.save()

        snapshot_1 = Snapshot(course=course_1)
        snapshot_2 = Snapshot(course=course_1)
        snapshot_1.save()
        snapshot_2.save()

        snapshot_1.created_at = arrow.now().shift(hours=-2)
        snapshot_2.created_at = arrow.now().shift(minutes=-59)
        snapshot_1.save()
        snapshot_2.save()

        assert len(Snapshot.select().filter(Snapshot.course == course_1)) == 2

        await job()

        assert len(Snapshot.select().filter(Snapshot.course == course_1)) == 2

        snapshot_2.created_at = arrow.now().shift(minutes=-60)
        snapshot_2.save()

        await job()

        assert len(Snapshot.select().filter(Snapshot.course == course_1)) == 3

        # running the job again shouldn't produce any new snapshots, since
        # a new one was just created
        await job()
        assert len(Snapshot.select().filter(Snapshot.course == course_1)) == 3


@pytest.mark.asyncio
async def test_job_enqueues_itself_the_next_minute(mocker):
    mock_start_job_again_in = mocker.patch("jobs.snapshot.capture_snapshots.start_job_again_in")

    await job()

    mock_start_job_again_in.assert_called_once_with(60)
