from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists
from db.models import Chat, ChatConfig, PromptHandle


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    rename_map = {
        # syntax is from: to
        'model_name': 'llm_model_name',
        'model_params': 'llm_model_params',
    }
    models = [Chat, ChatConfig, PromptHandle]

    for model in models:
        table_name = model._meta.table_name
        for old_column, new_column in rename_map.items():
            if column_exists(model, old_column):
                sql = f'ALTER TABLE "{table_name}" RENAME COLUMN "{old_column}" TO "{new_column}";'
                if not fake:
                    database.execute_sql(sql)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # Reverse the rename_map for rollback
    rename_map = {
        'llm_model_name': 'model_name',
        'llm_model_params': 'model_params',
    }
    models = [Chat, ChatConfig, PromptHandle]

    for model in models:
        table_name = model._meta.table_name
        for new_column, old_column in rename_map.items():
            if column_exists(model, new_column):
                sql = f'ALTER TABLE "{table_name}" RENAME COLUMN "{new_column}" TO "{old_column}";'
                if not fake:
                    database.execute_sql(sql)
