import sqlalchemy as sa

from db import Base
from models.base import BaseMixin
from models.enums import State


class Complaint(BaseMixin, Base):
    __tablename__ = "complaints"

    title = sa.Column(sa.String(120), nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    photo_url = sa.Column(sa.String(200), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    state = sa.Column(sa.Enum(State), nullable=False, server_default=State.pending.name)
    complainer_id = sa.Column(sa.ForeignKey("users.id"), nullable=False)
