# Import all the models, so that Base has them before being
# imported by Alembic
from storage.db.base_class import Base  # noqa
from storage.db.models.token import *  # noqa
from storage.db.models.user import *  # noqa
