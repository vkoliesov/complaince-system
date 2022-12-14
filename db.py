import databases
import sqlalchemy
from decouple import config
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = f'postgresql://{config("POSTGRES_USER")}:{config("POSTGRES_PASSWORD")}@{config("POSTGRES_HOST")}:{config("POSTGRES_PORT")}/{config("POSTGRES_DB")}'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

Base = declarative_base(metadata=metadata)
