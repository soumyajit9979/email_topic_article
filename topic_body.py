import psycopg2
import pandas as pd

def fetch_filtered_emails(topic_name, org_id, year):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()

        cursor.execute('SELECT "id" FROM "topics" WHERE "name" = %s AND "organizationId" = %s', (topic_name, org_id))
        topic_result = cursor.fetchone()
        
        if not topic_result:
            print(f"Topic '{topic_name}' not found for Organization ID {org_id}.")
            return
        
        topic_id = topic_result[0]
        print("topic_id: ",topic_id)

        cursor.execute('SELECT "emailId" FROM "emails_topics" WHERE "topicId" = %s', (topic_id,))
        email_id_results = cursor.fetchall()
        
        if not email_id_results:
            print(f"No emails found for topic '{topic_name}' in Organization ID {org_id}.")
            return
        
        email_ids = tuple(row[0] for row in email_id_results)
        print("email_ids: ",email_ids)
        query = '''
            SELECT "bodyHTML" 
            FROM "emails" 
            WHERE "id" IN %s AND "organizationId" = %s 
            AND EXTRACT(YEAR FROM "date") = %s
        '''
        cursor.execute(query, (email_ids, org_id, year))
        email_data = cursor.fetchall()
        print("email_data",email_data)
        if not email_data:
            print(f"No emails found for topic '{topic_name}', Organization ID {org_id}, in year {year}.")
            return

        df = pd.DataFrame(email_data, columns=["bodyHTML"])

        excel_filename = f"data/{topic_name}_{org_id}_{year}.xlsx"
        df.to_excel(excel_filename, index=False)

        print(f"Data successfully saved to {excel_filename}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# if "__name__"=="__main__":
topic_name_input = input("Enter the topic name: ")
org_id_input = input("Enter the organization ID: ")
year_input = input("Enter the year (YYYY): ")

fetch_filtered_emails(topic_name_input, org_id_input, year_input)
