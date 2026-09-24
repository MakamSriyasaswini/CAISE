from gateway.services.metadata_service import get_db_connection


def test_database_connection():
    connection = get_db_connection()

    assert connection is not None

    connection.close()