from datetime import date
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.db.models import CreationModificationDateBase, Base


class User(CreationModificationDateBase):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(sa.String(254), unique=True, index=True, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(sa.String(254), default="")
    middle_name: Mapped[Optional[str]] = mapped_column(sa.String(254), default="")
    last_name: Mapped[Optional[str]] = mapped_column(sa.String(254), default="")

    date_of_birth: Mapped[date] = mapped_column(sa.Date, nullable=False)
    date_of_join: Mapped[date] = mapped_column(sa.Date, nullable=False)
    date_of_left: Mapped[date] = mapped_column(sa.Date, nullable=False)

    business_email: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    personal_email: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)


class Group(CreationModificationDateBase):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(sa.String(254), unique=True, nullable=False, index=True)


class UserToGroup(Base):
    __tablename__ = "user_group"
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE', name='fx_user2group'))
    group_id: Mapped[int] = mapped_column(sa.ForeignKey('groups.id', ondelete='CASCADE', name='fx_group2user'))

    __table_args__ = (
        sa.UniqueConstraint('user_id', 'group_id', name='ux_user_id_group_id'),
    )
