import os


class DB_PROPERTIES:
    host = os.getenv('POSTGRES_HOST', 'localhost')
    database = 'postgres'
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'pass')
    port = 5432
    connections = 2
