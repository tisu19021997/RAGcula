from app.db.pg_vector import get_vector_store_singleton
from sqlalchemy import text


async def is_user_existed(
    user_id: str,
):
    vector_store = await get_vector_store_singleton()

    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"SELECT * FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        result = await session.execute(stmt)
    return result.first() is not None


async def is_document_existed(
    document_name: str,
    user_id: str,
):
    vector_store = await get_vector_store_singleton()

    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"SELECT * FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            f"(metadata_->>'file_name')::text = '{document_name}' and"
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        result = await session.execute(stmt)
    return result.first() is not None


async def delete_all_documents_from_user(
    user_id: str
):
    vector_store = await get_vector_store_singleton()

    async with vector_store._async_session() as session, session.begin():
        stmt = text(
            f"DELETE FROM {vector_store.schema_name}.data_{vector_store.table_name} where "
            # f"(metadata_->>'file_name')::text = '{document_name}' and"
            f"(metadata_->>'user_id')::text = '{user_id}'"
        )
        await session.execute(stmt)
        await session.commit()
