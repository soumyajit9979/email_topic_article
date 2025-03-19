import openai
import pandas as pd
import psycopg2
import re
import json
import os
import winsound
# Set OpenAI API Key
# Clean HTML from text
def clean_html(text):
    clean_text = re.sub(r"<[^>]*>", " ", text)  # Remove HTML tags
    clean_text = re.sub(r"\s+", " ", clean_text).strip()  # Remove extra spaces
    return clean_text

# Extract topic_name, organization_id, and year from filename
def extract_metadata(filename):
    try:
        base_name = os.path.splitext(filename)[0]  # Remove file extension
        parts = base_name.split("_")
        if len(parts) >= 3:
            topic_name = parts[0]  # First part is topic_name
            organization_id = parts[1]  # Second part is organizationId
            year = parts[2]  # Third part is year
            return topic_name, organization_id, year
        else:
            raise ValueError(" Filename format is incorrect. Expected: topic_organizationId_year.xlsx")
    except Exception as e:
        print(f" Error extracting metadata from filename: {e}")
        return None, None, None

# Load and preprocess email data
def load_email_data(excel_file):
    try:
        df = pd.read_excel(excel_file)

        if "bodyHTML" not in df.columns:
            print("Error: 'bodyHTML' column not found in Excel file.")
            return None

        all_text = " ".join(clean_html(text) for text in df["bodyHTML"].dropna())

        token_estimate = len(all_text.split())  
        print(f"📊 Processed Text Size: ~{token_estimate} tokens")

        return all_text

    except Exception as e:
        print(f"rror reading Excel file: {e}")
        return None

# Function to summarize email data and store in PostgreSQL
def summarize_and_store_in_db(excel_file):
    """Summarizes email data and saves in the PostgreSQL database."""
    
    # Extract metadata from filename
    topic_name, organization_id, year = extract_metadata(excel_file)
    
    if not topic_name or not organization_id or not year:
        print("Failed to extract topic_name, organization_id, or year from filename.")
        return

    all_text = load_email_data(excel_file)
    
    if not all_text or len(all_text.strip()) == 0:
        print("No valid text data found!")
        return

    MAX_WORDS = 90000  # Keep buffer for OpenAI token limit
    all_text = " ".join(all_text.split()[:MAX_WORDS])

    model_name = "gpt-4-turbo"

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an AI that summarizes long emails. You must respond in a structured JSON format."},
                {"role": "user", "content": f"Summarize this text:\n{all_text}. Format the response as follows and give 5 headings and descriptions:\n\n{{'response': [{{'heading': 'Title', 'description': 'Summary'}}]}}"}
            ],
            max_tokens=2000
        )

        # Extract structured JSON response
        final_summary = response.choices[0].message.content.strip()
        parsed_summary = json.loads(final_summary)  # Convert string to JSON

        # Convert JSON to a string for database storage
        summary_json_str = json.dumps(parsed_summary)

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO "topic_analysis" ("organizationId", "topic_name", "year", "top_issues_json","topicId")
        VALUES (%s, %s, %s, %s,%s);
        """
        cursor.execute(insert_query, (organization_id, topic_name, year, summary_json_str,1))

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Summary successfully stored in the database.")

    except Exception as e:
        print(f"Error: {e}")

# Run script
if __name__ == "__main__":
    excel_file = "Housing_1_2020.xlsx"  # Change to actual Excel file
    final_file=f"data/{excel_file}"
    summarize_and_store_in_db(final_file)
    winsound.Beep(2500,500)
