import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from app.config.app_config import app_config
from app.helper.logger_helper import logger

db_location = app_config.CONFIG_PATH / 'database.db'

# 创建引擎
engine = create_engine(
    f'sqlite:///{db_location}',
    echo=app_config.DB_ECHO_SQL,
    connect_args={
        'check_same_thread': False
    }
)

# 封装获取会话
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# 创建Base
Base = declarative_base()


@contextmanager
def get_database_session(auto_commit=True):
    session = SessionLocal()
    try:
        yield session
        if auto_commit:
            session.commit()
    except Exception as e:
        logger.error(f'数据库操作错误：{str(e)} - {traceback.format_exc()}')
        session.rollback()
        raise e
    finally:
        session.close()
