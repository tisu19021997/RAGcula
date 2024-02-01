import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

POSTGRE_ASYNC_ENGINE = os.environ["POSTGRE_ASYNC_ENGINE"]
POSTGRE_ENGINE = os.environ["POSTGRE_ENGINE"]
POSTGRE_CONNECTION_STRING = os.environ["POSTGRE_CONNECTION_STRING"]
VECTOR_STORE_TABLE_NAME = os.environ["VECTOR_STORE_TABLE_NAME"]
