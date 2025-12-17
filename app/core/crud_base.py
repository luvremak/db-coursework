import logging
from copy import deepcopy
from typing import ClassVar, Optional, Sequence

from sqlalchemy import Table, and_, asc, desc, func, select
from sqlalchemy.dialects import postgresql

from app.core.database import database
from app.core.types import PageData, PaginationParameters

logger = logging.getLogger(__name__)


class CrudBase[ID, DTO]:
    table: ClassVar[Table]

    @staticmethod
    def log_query(query):
        try:
            compiled = query.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
            logger.info(str(compiled))
        except Exception:
            logger.info(str(query))
        logger.info('-' * 50)

    async def get_by_id(self, id_: ID) -> Optional[DTO]:
        query = self.table.select().where(self.table.c.id == id_)
        self.log_query(query)
        return await database.fetch_one(query)

    async def create(self, obj: DTO) -> ID:
        query = self.table.insert().values(**obj)
        self.log_query(query)
        return await database.execute(query)

    async def create_and_get(self, obj: DTO) -> DTO:
        query = self.table.insert().values(**obj).returning(self.table)
        self.log_query(query)
        return await database.fetch_one(query)

    async def create_many(self, objs: Sequence[DTO]) -> list[ID]:
        objs = list(objs)
        if not objs:
            return []
        query = self.table.insert().values(objs).returning(self.table.c.id)
        self.log_query(query)
        rows = await database.fetch_all(query)
        return [row[0] for row in rows]

    async def create_and_get_many(self, objs: Sequence[DTO]) -> Sequence[DTO]:
        objs = list(objs)
        if not objs:
            return []
        query = self.table.insert().values(objs).returning(self.table)
        self.log_query(query)
        return await database.fetch_all(query)

    async def update(self, values: DTO) -> ID:
        id_ = values["id"]
        query = (
            self.table.update()
            .where(self.table.c.id == id_)
            .values(values)
            .returning(self.table.c.id)
        )
        self.log_query(query)
        row = await database.fetch_one(query)
        return row[0]

    async def update_and_get(self, values: DTO) -> DTO:
        id_ = values["id"]
        query = (
            self.table.update()
            .where(self.table.c.id == id_)
            .values(values)
            .returning(self.table)
        )
        self.log_query(query)
        return await database.fetch_one(query)

    async def update_many(self, objs: Sequence[DTO]) -> None:
        for obj in objs:
            await self.update(obj)

    async def get_many_by_ids(self, ids: Sequence[ID]) -> Sequence[DTO]:
        query = self.table.select().where(self.table.c.id.in_(ids))
        self.log_query(query)
        return await database.fetch_all(query)

    async def delete(self, id_: ID) -> None:
        query = self.table.delete().where(self.table.c.id == id_)
        self.log_query(query)
        await database.execute(query)

    async def delete_many(self, ids: Sequence[ID]) -> None:
        query = self.table.delete().where(self.table.c.id.in_(ids))
        self.log_query(query)
        await database.execute(query)

    async def count(self) -> int:
        query = func.count().select_from(self.table)
        self.log_query(query)
        return await database.fetch_val(query)

    async def get_all(self) -> Sequence[DTO]:
        query = self.table.select()
        self.log_query(query)
        return await database.fetch_all(query)

    def _get_column_by_name(self, column_name: str):
        return self.table.c.get(column_name)

    def apply_filters(self, query, filters: dict | None = None):
        if not filters:
            return query
        sqla_filters = []
        for column_name, value in filters.items():
            column = self._get_column_by_name(column_name)
            if column is None:
                continue
            sqla_filters.append(column == value)
        if sqla_filters:
            query = query.where(and_(*sqla_filters))
        return query

    def apply_pagination(self, query, pagination: PaginationParameters | None = None):
        if pagination is None:
            return query
        if pagination.page_size > 0 and pagination.page > 0:
            limit = pagination.page_size
            offset = (pagination.page - 1) * pagination.page_size
            query = query.limit(limit).offset(offset)
        order_column = self._get_column_by_name(pagination.order_by)
        order = asc if pagination.ascending else desc
        if order_column is not None:
            query = query.order_by(order(order_column))
        return query

    async def count_filtered(self, filters: dict | None = None) -> int:
        query = select(func.count()).select_from(self.table)
        query = self.apply_filters(query, filters)
        self.log_query(query)
        return await database.fetch_val(query)

    async def list(
        self,
        filters: dict | None = None,
        pagination: PaginationParameters | None = None,
    ) -> Sequence[DTO]:
        query = select(self.table)
        query = self.apply_filters(query, filters)
        query = self.apply_pagination(query, pagination)
        self.log_query(query)
        return await database.fetch_all(query)

    async def get_page(
        self,
        filters: dict | None = None,
        pagination: PaginationParameters | None = None,
    ) -> PageData[DTO]:
        return PageData(
            data=list(await self.list(deepcopy(filters), pagination=pagination)),
            total=await self.count_filtered(deepcopy(filters)),
        )
