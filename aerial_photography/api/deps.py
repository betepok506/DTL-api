from typing import Generator
from aerial_photography.database.session import SessionLocal
from sqlalchemy import exc


def get_db_session() -> Generator:
    # engine = create_async_engine(settings.DATABASE_URL)
    factory = SessionLocal()
    try:
        yield factory
        factory.commit()
    except exc.SQLAlchemyError:
        factory.rollback()
        raise
    finally:
        factory.close()
