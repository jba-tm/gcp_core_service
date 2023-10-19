from typing import Optional
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.db.models import CreationModificationDateBase, Base


class School(CreationModificationDateBase):
    __tablename__ = 'schools'
    name: Mapped[str] = mapped_column(sa.String(254), unique=True, index=True, nullable=False)
    address_line_1: Mapped[Optional[str]] = mapped_column(sa.String(254), default="", nullable=True)
    address_line_2: Mapped[Optional[str]] = mapped_column(sa.String(254), default="", nullable=True)
    pin_code: Mapped[Optional[int]] = mapped_column(sa.Integer(), nullable=True)
    web_site: Mapped[Optional[str]] = mapped_column(sa.String(100), default="", nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        sa.DECIMAL(precision=18, scale=18, asdecimal=True),
        nullable=True
    )
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        sa.DECIMAL(precision=18, scale=18, asdecimal=True),
        nullable=True
    )


class UserToSchool(Base):
    __tablename__ = "user_school"
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE', name='fx_user2school'))
    school_id: Mapped[int] = mapped_column(sa.ForeignKey('schools.id', ondelete='CASCADE', name='fx_school2user'))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    __table_args__ = (
        sa.UniqueConstraint('user_id', 'school_id', name='ux_user_id_school_id'),
    )
