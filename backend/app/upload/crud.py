import uuid as uuid_pkg
from fastapi import Depends
from typing import List, Optional
from sqlalchemy import text
from sqlmodel import select, delete

from app.database import get_vector_store_singleton, SessionLocal
from .models import Document


async def is_user_existed(
    user_id: str,
) -> bool:
    vector_store = await get_vector_store_singleton()
    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"SELECT id FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        result = await session.execute(stmt)
    return result.first() is not None


async def is_document_existed(
    document_id: uuid_pkg.UUID,
    user_id: str,
) -> bool:
    vector_store = await get_vector_store_singleton()
    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"SELECT id FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            f"(metadata_->>'document_id')::text = '{document_id}' and"
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        result = await session.execute(stmt)
    return result.first() is not None


async def delete_all_documents_from_user(
    user_id: str,
) -> None:
    vector_store = await get_vector_store_singleton()
    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"DELETE FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            # f"(metadata_->>'file_name')::text = '{document_name}' and"
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        await session.execute(stmt)
        await session.commit()


def create_documents(
    documents: List[Document],
) -> List[Document]:
    with SessionLocal() as session:
        for document in documents:
            session.add(document)
            session.commit()
            session.refresh(document)
    return documents


def get_documents(
) -> List[Document] | None:
    with SessionLocal() as session:
        stmt = select(Document)
        documents = session.execute(stmt).scalars().all()
        return documents


def get_document_by_id(
    document_id: str,
) -> Optional[Document]:
    with SessionLocal() as session:
        stmt = select(Document).where(Document.id == document_id)
        document = session.execute(stmt).scalars().first()
        return document


async def delete_document_by_id(
    document_id: uuid_pkg.UUID,
) -> None:
    # vector_store = await get_vector_store_singleton()

    # Document objects.
    with SessionLocal() as session:
        stmt = delete(Document).where(Document.id == document_id)
        session.execute(stmt)
        session.commit()

    # Vectors in vector database.
    # async with vector_store._async_session() as session, session.begin():
    #     stmt = text(
    #         f"DELETE FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
    #         f"(metadata_->>'doc_uuid')::text = '{document_id}'"
    #     )
    #     await session.execute(stmt)
    #     await session.commit()
