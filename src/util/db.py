import os
from typing import Union

import duckdb
from duckdb import DuckDBPyConnection

data_dir = os.path.normpath(f"{__file__}/../../../data")
db_filepath = f"{data_dir}/db/local.db"

DB_CONN: Union[DuckDBPyConnection, None] = None


def get_db_connection() -> DuckDBPyConnection:
    global DB_CONN
    if not DB_CONN:
        DB_CONN = duckdb.connect(db_filepath)
    return DB_CONN
