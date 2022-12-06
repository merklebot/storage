# Import all the models, so that Base has them before being
# imported by Alembic
from storage.db.base_class import Base  # noqa
from storage.db.models.content import *  # noqa
from storage.db.models.key import *  # noqa
from storage.db.models.permission import *  # noqa
from storage.db.models.token import *  # noqa
from storage.db.models.user import *  # noqa
