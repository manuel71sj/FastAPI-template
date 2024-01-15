from __future__ import annotations

import math

from typing import TYPE_CHECKING, Generic, Sequence, TypeVar

from fastapi import Depends, Query
from fastapi_pagination import pagination_ctx
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination.links.bases import create_links
from pydantic import BaseModel

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')
DataT = TypeVar('DataT')
SchemaT = TypeVar('SchemaT')


class _Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description='Page number')
    size: int = Query(20, gt=0, le=100, description='Page size')

    def to_raw_params(self) -> RawParams:
        return RawParams(limit=self.size, offset=self.size * (self.page - 1))


class _Page(AbstractPage[T], Generic[T]):
    items: Sequence[T]  # 숫자
    total: int  # 총 데이터 수
    page: int  # 현재 페이지
    size: int  # 페이지당 개수
    total_pages: int  # 총 페이지 수
    links: dict[str, str | None]  # 점프 링크

    __params_type__ = _Params  # 사용자 지정 매개변수 사용

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: _Params) -> _Page[T]:
        page = params.page
        size = params.size
        total_pages = math.ceil(total / params.size)

        first = {'page': 1, 'size': f'{size}'}
        last = ({'page': f'{math.ceil(total / params.size)}', 'size': f'{size}'}) if total > 0 else None
        next_link = {'page': f'{page + 1}', 'size': f'{size}'} if (page + 1) <= total_pages else None
        prev_link = {'page': f'{page - 1}', 'size': f'{size}'} if (page - 1) >= 1 else None

        links = create_links(first=first, last=last, next=next_link, prev=prev_link).model_dump()  # type: ignore

        return cls(items=items, total=total, page=params.page, size=params.size, total_pages=total_pages, links=links)


class _PageData(BaseModel, Generic[DataT]):
    page_data: DataT | None = None


async def paging_data(db: AsyncSession, select: Select, page_data_schema: SchemaT) -> dict:  # type: ignore
    """
    SQLAlchemy를 기반으로 페이징 데이터 만들기

    :param db:
    :param select:
    :param page_data_schema:
    :return:
    """
    _paginate = await paginate(db, select)  # type: ignore
    page_data = _PageData[_Page[page_data_schema]](page_data=_paginate).model_dump()['page_data']  # type: ignore

    return page_data


# 페이징 종속성 주입
DependsPagination = Depends(pagination_ctx(_Page))
