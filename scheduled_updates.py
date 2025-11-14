import psycopg
from decouple import config

DB_HOST     = config('DB_HOST')
DB_NAME     = config('DB_NAME')
DB_USER     = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_PORT     = config('DB_PORT')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:      
        cur.execute(
            "UPDATE story SET locked = false WHERE id in (SELECT story_id from part WHERE date_complete IS NULL AND user_id IS NOT NULL AND date_started < NOW() - INTERVAL '3 days');"
        )
        print(f"{cur.rowcount} stories were updated")
        cur.execute(
            "UPDATE part SET user_id = null, part_text = '' WHERE date_complete IS NULL AND user_id IS NOT NULL AND date_started < NOW() - INTERVAL '3 days';"
        )
        print(f"{cur.rowcount} parts were updated")