import warnings
import uuid

import peewee

from db.custom_fields import FeedbackQuestionExtraDataField
from . import BaseModel

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)

FAQ_TRIGGER = 'from_faq'


def _generate_id() -> str:
    uuid4 = uuid.uuid4()
    return str(uuid4)


class FeedbackQuestion(BaseModel):
    class Meta:
        db_table = 'feedback_questions'
        table_name = 'feedback_questions'

    id = peewee.AutoField()
    feedback_question_id = peewee.CharField(null=False, index=True, unique=True, default=_generate_id)
    trigger = peewee.CharField(null=False, index=True)
    is_active = peewee.BooleanField(default=True)
    question_en = peewee.TextField(null=False)
    question_sv = peewee.TextField(null=False)
    extra_data_en = FeedbackQuestionExtraDataField(null=False)
    extra_data_sv = FeedbackQuestionExtraDataField(null=False)

    def to_dict_in_language(self, language: str) -> dict:
        if language == 'en':
            return {
                'feedback_question_id': self.feedback_question_id,
                'question': self.question_en,
                'extra_data': self.extra_data_en,
            }
        elif language == 'sv':
            return {
                'feedback_question_id': self.feedback_question_id,
                'question': self.question_sv,
                'extra_data': self.extra_data_sv,
            }
        else:
            raise ValueError(f"Unsupported language {language}")

    @staticmethod
    def make_chat_message_trigger(chat_number: int, message_number: int) -> str:
        return f'chat:{chat_number}:message:{message_number}'
