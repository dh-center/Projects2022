import os


class SEARCH_PROPERTIES:
    host = os.getenv('SEARCH_HOST', 'localhost')
    port = 8083
