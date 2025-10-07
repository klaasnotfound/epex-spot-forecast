import os
from unittest.mock import patch

import duckdb

from src.util.db import get_db_connection

data_dir = os.path.normpath(f"{__file__}/../../../data")


def test_get_db_connection():
    with patch.object(duckdb, "connect", return_value="dummy_conn") as mock_connect:
        # Inits new connection
        conn1 = get_db_connection()
        assert conn1 == "dummy_conn"
        mock_connect.assert_called_once_with(f"{data_dir}/db/local.db")
        # Re-uses existing connection
        conn2 = get_db_connection()
        assert conn2 == conn1
        mock_connect.assert_called_once_with(f"{data_dir}/db/local.db")
