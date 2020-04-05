from os import getenv

from sqlalchemy import create_engine

from cicada2.protos import runner_pb2


ENGINE = None

def get_engine():
    global ENGINE

    if ENGINE is not None:
        return ENGINE

    connection_string = getenv('RUNNER_CONNECTIONSTRING')

    if connection_string is not None:
        # NOTE: maybe expect connection string in JDBC format
        ENGINE = create_engine(connection_string)
        return ENGINE
    
    # postgresql://postgres:admin@db:5432/postgres

    driver = getenv('RUNNER_DRIVER')
    username = getenv('RUNNER_USERNAME')
    password = getenv('RUNNER_PASSWORD')
    host = getenv('RUNNER_HOST')
    port = getenv('RUNNER_PORT')
    database = getenv('RUNNER_DATABASE')

    assert None not in [driver, username, password, host, port, database], (
        """
        Must specify connectionString or the following:
        * username
        * password
        * host
        * port
        * database
        """
    )

    ENGINE = create_engine(
        f"{driver}://{username}:{password}@{host}:{port}/{database}"
    )
    return ENGINE


def run_action(action_type, params):
    # TODO: figure out error handling without terminating instance
    query = params['query']

    if action_type == 'SQLQuery':
        with get_engine().connect() as connection:
            result = connection.execute(query)
    else:
        raise ValueError(f"Action type {action_type} is invalid")

    if result.returns_rows:
        # item[0] is column name
        # item[1] is column value
        # row.values() is list of tuples for the row
        rows = [
            {item[0]: item[1] for item in row.values()}
            for row in result
        ]
    else:
        rows = []

    return {
        'rows': rows
    }
