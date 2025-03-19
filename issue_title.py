import psycopg2
import openai
import json




def fetch_topics():
    print("Connecting to the database to fetch topics...")
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute('SELECT "name" from "topics"')
        name_result = cursor.fetchall()
        name = tuple(row[0] for row in name_result)

        print(f"Fetched topics: {name}")
        return name

    except Exception as e:
        print(f"Error fetching topics: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed after fetching topics.")


def adjective(word):
    print(f"Requesting OpenAI to generate an adjective for: {word}")
    model_name = "gpt-4-turbo"
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an AI that provides correct grammatical versions of words for given statements. Your response must be in a structured JSON format."},
                {"role": "user", "content": f"Give the correct grammatical version of '{word}' that fits the statement: 'Top _____ Issues in 2025'.\n\nRespond in JSON format:\n\n{{\"response\": [{{\"name\": \"adjective\"}}]}}\n\nDo not return the entire statement."}
            ],
            max_tokens=100
        )

        adjective_word = response.choices[0].message.content.strip()
        print(f"Raw API Response: {adjective_word}")

        parsed_summary = json.loads(adjective_word)
        result = parsed_summary["response"][0]["name"]
        
        print(f"Adjective for '{word}': {result}")
        return result

    except Exception as e:
        print(f"Error fetching adjective from OpenAI: {e}")
        return None


def fill_table():
    print("Starting table update process...")
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()

        # Fetch all topics
        topics = fetch_topics()
        if not topics:
            print("No topics found. Exiting update process.")
            return
        
        # Process each topic
        for name in topics:
            print(f"Processing topic: {name}")

            ad = adjective(name)
            if ad:
                print(f"Updating database: Setting adjective = '{ad}' for name = '{name}'")
                query = 'UPDATE topics SET adjective = %s WHERE name = %s'
                cursor.execute(query, (ad, name))
                conn.commit()
                print(f"Update successful for {name}.")
            else:
                print(f"Skipping update for {name} due to missing adjective.")

    except Exception as e:
        print(f"Error updating database: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed after updating topics.")


# Run the update process
fill_table()
