import warnings

import peewee

from . import BaseModel, Message, FeedbackQuestion

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)

QUESTION_UNANSWERED = 'UNANSWERED'


class Feedback(BaseModel):
    class Meta:
        db_table = 'feedback'
        table_name = 'feedback'

    id = peewee.AutoField()
    language = peewee.CharField(null=False, index=True, max_length=4)
    answer = peewee.CharField(null=False, index=True, max_length=512, default=QUESTION_UNANSWERED)
    feedback_question = peewee.ForeignKeyField(FeedbackQuestion, null=True, backref='feedbacks', on_delete='CASCADE')
    message = peewee.ForeignKeyField(Message, null=True, backref='feedbacks', on_delete='CASCADE')
