import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

with open("sql/analytics.sql", "r") as f:
    sql_script = f.read()

# Separate queries by semicolon
queries = [q.strip() for q in sql_script.split(";") if q.strip()]

with engine.connect() as conn:
    for idx, query in enumerate(queries, 1):
        print(f"\n==================== Query {idx} Output ====================")
        result = conn.execute(text(query))
        if result.returns_rows:
            rows = result.fetchall()
            keys = result.keys()
            print(" | ".join(keys))
            print("-" * 60)
            for row in rows:
                print(row)