import sqlalchemy as sa

from db import Base
from models.base import BaseMixin
from models.enums import RoleType


class User(BaseMixin, Base):
    __tablename__ = "users"

    email = sa.Column(sa.String(120), unique=True)
    password = sa.Column(sa.String(255))
    first_name = sa.Column(sa.String(200))
    last_name = sa.Column(sa.String(200))
    phone = sa.Column(sa.String(20))
    role = sa.Column(
        sa.Enum(RoleType), nullable=False, server_default=RoleType.complainer.name
    )
    iban = sa.Column(sa.String(200))
