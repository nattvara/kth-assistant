from peewee_migrate import Migrator
import peewee as pw

from db.custom_fields import IndexTypeField, ModelNameField
from services.index.supported_indices import IndexType
from db.migrations import column_exists, is_sqlite
from services.llm.supported_models import LLMModel
from db.models import Session


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Session, 'default_index_type'):
        default_index_type_field_no_default = IndexTypeField(null=False, index=True)
        default_index_type_field_with_default = IndexTypeField(
            null=False,
            index=True,
            default=IndexType.VECTOR_SEARCH_OPENAI_TEXT_EMBEDDING_3_LARGE
        )
        migrator.add_fields(Session, default_index_type=default_index_type_field_with_default)
        migrator.change_fields(Session, default_index_type=default_index_type_field_no_default)

    if not column_exists(Session, 'default_llm_model_name'):
        default_llm_model_name_no_default = ModelNameField(null=False, index=True)
        default_llm_model_name_with_default = ModelNameField(null=False, index=True, default=LLMModel.OPENAI_GPT4)
        migrator.add_fields(Session, default_llm_model_name=default_llm_model_name_with_default)
        migrator.change_fields(Session, default_llm_model_name=default_llm_model_name_no_default)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Session, 'default_index_type', cascade=True)
        migrator.remove_fields(Session, 'default_llm_model_name', cascade=True)
