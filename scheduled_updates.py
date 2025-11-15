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

        # if a story has parts that have not been completed in 3 days
        # and there are parts that have been completed (last_user_id exists)
        # then make the story available for editing
        cur.execute(
            """
            UPDATE story 
               SET locked = false 
             WHERE 
                id IN (
                    SELECT story_id 
                    FROM part 
                    WHERE 
                        date_complete IS NULL AND 
                        user_id IS NOT NULL AND  
                        date_started < NOW() - INTERVAL '3 days'
                )
                AND last_user_id IS NOT NULL;
            """
        )
        print(f"{cur.rowcount} stories were updated")

        # if a story has parts that have not been completed in 3 days
        # but there are no parts that have been completed (last_user_id is null) 
        # then just remove the story, for now just store the story_ids as we 
        # can't delete until we have removed the part due to the foreign key
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
        delete_these_stories = [record[0] for record in cur]

        # now that we have updated the stories delete the latest part for the
        # story that hasn't been finished in 3 days
        cur.execute(
            """
            DELETE 
              FROM part 
             WHERE 
                date_complete IS NULL AND 
                user_id IS NOT NULL AND 
                date_started < NOW() - INTERVAL '3 days';
            """
        )
        print(f"{cur.rowcount} parts were deleted")

        # now we have deleted the parts we can delete the stories
        # note the addition of "last_user_id IS NULL" as we only want
        # the stories that have no saved parts
        cur.execute(
            """
            DELETE 
              FROM story 
             WHERE 
                id IN (%s) AND
                last_user_id IS NULL;
            """,
            delete_these_stories
        )
        print(f"{cur.rowcount} stories were deleted as there were no finished parts")