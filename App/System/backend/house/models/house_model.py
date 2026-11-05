# ==================================================
# House
#
# Primary entity for the House domain.
#
# Examples:
#     Home
#     Lake Cabin
#     Rental House
#
# Parcel ID is optional because not all houses
# will have an available county lookup.
# ==================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean
)

from database import Base


class House(Base):

    __tablename__ = "houses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String
    )

    parcel_id = Column(
        String,
        nullable=True
    )

    address = Column(
        String
    )

    city = Column(
        String
    )

    county = Column(
        String
    )

    state = Column(
        String
    )

    zip_code = Column(
        String
    )

    date_acquired = Column(
        String,
        nullable=True
    )

    purchase_price_cents = Column(
        Integer,
        nullable=True
    )

    archived = Column(
        Boolean,
        default=False
    )