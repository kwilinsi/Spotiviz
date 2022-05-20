from sqlalchemy.orm import sessionmaker, scoped_session

GLOBAL_ENGINE = None

Session = scoped_session(sessionmaker())
