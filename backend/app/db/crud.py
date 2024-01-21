import uuid as uuid_pkg

from typing import List
from sqlalchemy import text
from sqlmodel import select, delete

from app.db.pg_vector import get_vector_store_singleton
from app.orm_models import Document
from app.db.session import SessionLocal


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
    user_id: str
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
    user_id: str
) -> List[Document] | None:
    with SessionLocal() as session:
        stmt = select(Document).where(Document.user_id == user_id)
        documents = session.execute(stmt).scalars().all()
        return documents


async def delete_document(
    document_id: uuid_pkg.UUID,
    user_id: str,
) -> None:
    with SessionLocal() as session:
        stmt = delete(Document).where(
            (Document.user_id == user_id)
            & (Document.id == document_id))
        session.execute(stmt)
        session.commit()

    vector_store = await get_vector_store_singleton()
    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"DELETE FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            f"(metadata_->>'doc_uuid')::text = '{document_id}' and"
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        await session.execute(stmt)
        await session.commit()
