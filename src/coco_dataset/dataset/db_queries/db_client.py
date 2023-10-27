from typing import Optional
import warnings

from loguru import logger
import pandas as pd
import pymssql
from dotenv import load_dotenv

from sclearn.utils import Timer
from .utils import get_db_conn_from_env
from .base_query_builder import BaseQuery


class DbClient:
    """Database client to run queries."""

    def __init__(self, db_conn: Optional[pymssql.Connection] = None) -> None:
        load_dotenv()
        self._db_conn = db_conn if db_conn else get_db_conn_from_env()

    def run(self, query: BaseQuery) -> pd.DataFrame:
        """Run the query and return the dataframe."""
        with Timer():
            logger.info("Running SQL query...")
            df: pd.DataFrame = self._run_sql_query(query.statement)
        logger.info(f"{df.head()=}")
        if df.empty:
            raise EmptyQueryError(query.statement)
        return df

    def _run_sql_query(self, query: str) -> pd.DataFrame:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
            df = pd.read_sql_query(sql=query, con=self._db_conn)
        return df


class EmptyQueryError(Exception):
    """Error raised when the query returns an empty dataframe."""

    def __init__(self, query: str) -> None:
        super().__init__(f"Query returned an empty dataframe:\n{query}")
