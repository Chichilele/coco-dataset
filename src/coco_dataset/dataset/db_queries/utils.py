import os
from enum import Enum
from typing import List

import pymssql


def parse_list_to_sql(list_of_values: List[str]) -> str:
    """Prase a list as a SQL readable list

    Args:
        list_of_values (List): lsit of values to make SQL readable

    Returns:
        str: sql list
    """
    joined = "', '".join(list_of_values)
    sql_list = f"('{joined}')"
    return sql_list


def get_db_conn_from_env() -> pymssql.Connection:
    """Get a database connection from the environment variables

    Returns:
        pymssql.Connection: database connection
    """
    try:
        SERVER = os.environ["DBServer"]
        PORT = int(os.environ["DBPort"])
        DBNAME = os.environ["DBName"]
        DBUSER = os.environ["DBUser"]
        DBPASSWORD = os.environ["DBPassword"]
    except KeyError as e:
        raise KeyError(f"Environment variables not set: {e}")
    except ValueError:
        raise ValueError("DBPort must be an integer")
    conn = pymssql.connect(
        server=SERVER, port=PORT, database=DBNAME, user=DBUSER, password=DBPASSWORD
    )
    return conn
