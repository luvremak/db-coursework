from typing import Sequence, Type

import asyncpg

from app.core.crud_base import CrudBase
from app.core.exceptions import UniqueViolationError
from app.core.models import Entity
from app.core.serializer import Serializer
from app.core.types import DTO


class RepoBase[ID, E: Entity]:
    not_found_exception_cls: Type[Exception]
    unique_violation_exception_cls: Type[UniqueViolationError]

    def __init__(self, crud: CrudBase[ID, DTO], serializer: Serializer[E, DTO], entity_cls: Type[E]):
        self.crud = crud
        self.serializer = serializer
        self.entity_cls = entity_cls

    async def get_by_id(self, id_: ID) -> E:
        dto = await self.crud.get_by_id(id_)
        if dto is None:
            raise self.not_found_exception_cls()
        return self.serializer.deserialize(dto)

    async def create(self, model: E) -> ID:
        dto = self.serializer.serialize(model)
        try:
            return await self.crud.create(dto)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def create_and_get(self, model: E) -> E:
        dto = self.serializer.serialize(model)
        try:
            dto = await self.crud.create_and_get(dto)
            return self.serializer.deserialize(dto)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def create_many(self, models: Sequence[E]) -> list[ID]:
        dtos = self.serializer.flat.serialize(models)
        try:
            return await self.crud.create_many(dtos)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def create_and_get_many(self, models: Sequence[E]) -> Sequence[E]:
        dtos = self.serializer.flat.serialize(models)
        try:
            dtos = await self.crud.create_and_get_many(dtos)
            return self.serializer.flat.deserialize(dtos)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def update(self, values: E) -> None:
        dto = self.serializer.serialize(values)
        try:
            await self.crud.update(dto)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def update_and_get(self, values: E) -> E:
        dto = self.serializer.serialize(values)
        try:
            dto = await self.crud.update_and_get(dto)
            return self.serializer.deserialize(dto)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def update_many(self, models: Sequence[E]) -> None:
        dtos = self.serializer.flat.serialize(models)
        try:
            await self.crud.update_many(dtos)
        except asyncpg.UniqueViolationError as e:
            raise self.unique_violation_exception_cls(e.constraint_name) from e

    async def get_many_by_ids(self, ids: Sequence[ID]) -> Sequence[E]:
        dtos = await self.crud.get_many_by_ids(ids)
        return self.serializer.flat.deserialize(dtos)

    async def delete(self, id_: ID) -> None:
        await self.crud.delete(id_)

    async def delete_many(self, ids: Sequence[ID]) -> None:
        await self.crud.delete_many(ids)

    async def count(self) -> int:
        return await self.crud.count()

    async def get_all(self) -> Sequence[E]:
        dto = await self.crud.get_all()
        return self.serializer.flat.deserialize(dto)
