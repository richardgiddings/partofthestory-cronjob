import psycopg
from decouple import config

DB_HOST     = config('DB_HOST')
DB_NAME     = config('DB_NAME')
DB_USER     = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_PORT     = config('DB_PORT')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

"""
BRIEF SUMMARY

We want to delete story parts that were started
more than 3 days ago but have not been completed and make the story 
available again.

To do this we:
- Identify the stories involved
- If these stories have completed parts we want to make the story available again
- Delete the parts that have not been completed in 3 days
- If the stories only had the one part just delete the story too
"""

with psycopg.connect(DATABASE_URL) as conn:

    with conn.cursor() as cur:

        # The story_id of expired parts
        cur.execute(
            """
            SELECT 
                story_id 
            FROM 
                part 
            WHERE 
                date_complete IS NULL AND 
                user_id IS NOT NULL AND
                date_started < NOW() - INTERVAL '3 days'
            """
        )
        story_ids_of_expired_parts = [record[0] for record in cur]
        print(f"Stories ids with expired parts {story_ids_of_expired_parts}")


        # If a story's latest part has not been completed in 3 days
        # and there are parts that have been completed (last_user_id exists)
        # then make the story available for editing
        story_update_query = """
            UPDATE 
                story 
            SET 
                locked = false 
            WHERE 
                id = ANY(%s) AND
                last_user_id IS NOT NULL;
            """
        result = psycopg.ClientCursor(conn).mogrify(
            story_update_query, (story_ids_of_expired_parts,)
        )
        cur.execute(story_update_query, (story_ids_of_expired_parts,))
        print(f"{cur.rowcount} stories were updated using:")
        print(result)


        # Delete the latest part for the
        # story that hasn't been finished in 3 days
        part_delete_query = """
            DELETE FROM 
                part 
            WHERE 
                date_complete IS NULL AND 
                user_id IS NOT NULL AND 
                date_started < NOW() - INTERVAL '3 days';
            """
        result = psycopg.ClientCursor(conn).mogrify(
            part_delete_query
        )
        cur.execute(part_delete_query)
        print(f"{cur.rowcount} parts were deleted using:")
        print(result)


        # Now we have deleted the parts we can delete the stories with
        # only one part. Note the addition of "last_user_id IS NULL".
        story_delete_query = """
            DELETE FROM 
                story 
            WHERE 
                id = ANY(%s) AND
                last_user_id IS NULL;
            """
        result = psycopg.ClientCursor(conn).mogrify(
            story_delete_query, (story_ids_of_expired_parts,)
        )
        cur.execute(story_delete_query, (story_ids_of_expired_parts,))
        print(f"{cur.rowcount} stories were deleted as there were no finished parts using:")
        print(result)