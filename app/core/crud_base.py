from typing import ClassVar, Optional, Sequence

from sqlalchemy import Table, func

from app.core.database import database


class CrudBase[ID, DTO]:
    table: ClassVar[Table]

    async def get_by_id(self, id_: ID) -> Optional[DTO]:
        return await database.fetch_one(self.table.select().where(self.table.c.id == id_))

    async def create(self, obj: DTO) -> ID:
        query = self.table.insert().values(**obj)
        return await database.execute(query)

    async def create_and_get(self, obj: DTO) -> DTO:
        query = self.table.insert().values(**obj).returning(self.table)
        return await database.fetch_one(query)

    async def create_many(self, objs: Sequence[DTO]) -> list[ID]:
        objs = list(objs)
        if len(objs) == 0:
            return []
        query = self.table.insert().values(objs).returning(self.table.c.id)
        rows = await database.fetch_all(query)
        return [row[0] for row in rows]

    async def create_and_get_many(self, objs: Sequence[DTO]) -> Sequence[DTO]:
        objs = list(objs)
        if len(objs) == 0:
            return []
        query = self.table.insert().values(objs).returning(self.table)
        return await database.fetch_all(query)

    async def update(self, values: DTO) -> ID:
        id_ = values["id"]
        query = self.table.update().where(self.table.c.id == id_).values(values).returning(self.table.c.id)
        row = await database.fetch_one(query)
        return row[0]

    async def update_and_get(self, values: DTO) -> DTO:
        id_ = values["id"]
        query = self.table.update().where(self.table.c.id == id_).values(values).returning(self.table)
        return await database.fetch_one(query)

    async def update_many(self, objs: Sequence[DTO]) -> None:
        for obj in objs:
            await self.update(obj)

    async def get_many_by_ids(self, ids: Sequence[ID]) -> Sequence[DTO]:
        query = self.table.select().where(self.table.c.id.in_(ids))
        return await database.fetch_all(query)

    async def delete(self, id_: ID) -> None:
        query = self.table.delete().where(self.table.c.id == id_)
        await database.execute(query)

    async def delete_many(self, ids: Sequence[ID]) -> None:
        query = self.table.delete().where(self.table.c.id.in_(ids))
        await database.execute(query)

    async def count(self) -> int:
        query = func.count().select_from(self.table)
        return await database.fetch_val(query)

    async def get_all(self) -> Sequence[DTO]:
        query = self.table.select()
        return await database.fetch_all(query)
