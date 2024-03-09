from llms.config import Params
from db.connection import db


def assert_table_count(expected_count):
    tables = db.get_tables()
    actual_count = len(tables)

    assert actual_count == expected_count, f"Expected {expected_count} tables, found {actual_count}"


def assert_model_params_equal(expected: Params, actual: Params):
    equal = (
            actual.temperature == expected.temperature and
            actual.max_new_tokens == expected.max_new_tokens and
            actual.context_length == expected.context_length and
            actual.enable_top_k_filter == expected.enable_top_k_filter and
            actual.top_k_limit == expected.top_k_limit and
            actual.enable_top_p_filter == expected.enable_top_p_filter and
            actual.top_p_threshold == expected.top_p_threshold and
            actual.stop_strings == expected.stop_strings
    )

    assert equal, "Model params instances are not equal"
