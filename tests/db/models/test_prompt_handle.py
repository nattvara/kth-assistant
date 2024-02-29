import arrow

from db.models.prompt_handle import PromptHandle


def test_prompt_handle_defaults_to_pending_state():
    handle = PromptHandle()

    assert handle.state == PromptHandle.States.PENDING


def test_timestamps_are_set_on_creation():
    handle = PromptHandle()

    assert handle.created_at is not None
    assert handle.modified_at is not None
    assert handle.created_at <= arrow.utcnow()
    assert handle.modified_at <= arrow.utcnow()


def test_modified_at_changes_on_save(mocker):
    first_mock_time = arrow.get('2024-02-29T11:50:47.810300+01:00')
    second_mock_time = first_mock_time.shift(hours=1)

    mock_utcnow = mocker.patch('db.models.base_model.arrow.utcnow', return_value=first_mock_time)

    handle = PromptHandle()

    mock_utcnow.return_value = second_mock_time

    handle.state = PromptHandle.States.FINISHED
    handle.save()

    assert handle.modified_at == second_mock_time
