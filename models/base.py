import sqlalchemy as sa


class BaseMixin:
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, nullable=False, server_default=sa.func.now())
    last_modified_at = sa.Column(
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
