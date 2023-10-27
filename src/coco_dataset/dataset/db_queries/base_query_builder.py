from typing import List, Optional
from abc import ABC, abstractmethod

from pydantic import BaseModel

from sclearn.dataset.db_queries import BOOTH_NAMES


class BaseQuery:
    """SQL Query."""

    statement: str

    def __init__(self, value: str) -> None:
        self.statement = value

    def __str__(self) -> str:
        return self.statement

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, BaseQuery) and self.statement == __value.statement


class BaseQueryBuilder(BaseModel, ABC):
    """SQL query builder to get labelled data."""

    booth_name: BOOTH_NAMES
    classes: Optional[List[str]]
    n_samples_per_class: int
    start_date: str
    end_date: str

    class Config:
        underscore_attrs_are_private = True
        use_enum_values = True

    _query: Optional[BaseQuery] = None

    @abstractmethod
    def get_query(self) -> BaseQuery:
        """Abstract method to be implemented by subclasses."""
