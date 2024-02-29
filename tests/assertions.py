from db.connection import db


def assert_table_count(expected_count):
    tables = db.get_tables()
    actual_count = len(tables)

    assert actual_count == expected_count, f"Expected {expected_count} tables, found {actual_count}"
