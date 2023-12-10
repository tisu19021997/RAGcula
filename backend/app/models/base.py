from sqlalchemy import Column, DateTime, UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id = Column(UUID, primary_key=True, index=True,
                default=func.uuid_generate_v4())
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __name__: str
