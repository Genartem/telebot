
import psycopg2

connection = psycopg2.connect(
    database = 'translate_bot',
    user = 'postgres',
    password = '123',
    host = 'localhost'
)

with connection.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id SERIAL PRIMARY KEY,
            source_text TEXT NOT NULL,
            telegram_id BIGINT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    connection.commit()
