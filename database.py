import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "articles.db"


@contextmanager
def get_connection():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        yield connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL
            )
        """)
        connection.commit()


def insert_article(url, title):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO articles (url, title)
            VALUES (?, ?)
            ON CONFLICT(url) DO NOTHING
            """,
            (url, title),
        )
        connection.commit()

        return cursor.rowcount == 1


def get_articles():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        return connection.execute(
            "SELECT id, url, title FROM articles ORDER BY id DESC"
        ).fetchall()


def delete_article(article_id):
    with get_connection() as connection:
        cursor = connection.execute("""DELETE FROM articles WHERE id = ?""", (article_id,))
        connection.commit()

        return cursor.rowcount > 0