import pytest
from sqlalchemy import text

from backend.app.database import make_engine, session_factory, transaction


def test_transaction_rolls_back_and_enables_foreign_keys():
    engine = make_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE sample (id INTEGER PRIMARY KEY)"))
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1
    with pytest.raises(RuntimeError):
        for session in transaction(session_factory(engine)):
            session.execute(text("INSERT INTO sample VALUES (1)"))
            raise RuntimeError("abort")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM sample")) == 0
    engine.dispose()
