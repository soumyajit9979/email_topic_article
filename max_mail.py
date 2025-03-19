import psycopg2

def find_topic_with_max_emails():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()

        # Query to count emails per topic
        query = '''
            SELECT t."name", COUNT(et."emailId") AS email_count
            FROM "topics" t
            JOIN "emails_topics" et ON t."id" = et."topicId"
            GROUP BY t."name"
            ORDER BY email_count DESC
            LIMIT 1
        '''
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            topic_name, email_count = result
            print(f"Topic with maximum emails: {topic_name} ({email_count} emails)")
        else:
            print("No topics found with emails.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Run the function
find_topic_with_max_emails()
