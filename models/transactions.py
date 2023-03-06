import sqlalchemy as sa

from db import Base
from models.base import BaseMixin


class Transaction(BaseMixin, Base):
    __tablename__ = "transactions"

    quote_id = sa.Column(sa.String(120), nullable=False)
    transfer_id = sa.Column(sa.Integer, nullable=False)
    target_account_id = sa.Column(sa.String(100), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    complaint_id = sa.Column(sa.ForeignKey("complaints.id"))
