import psycopg2
import pandas as pd



# Connect to the database
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    cursor = conn.cursor()
    
    # Query to extract all data from 'name' column in 'topics' table
    query = "SELECT name FROM topics"
    cursor.execute(query)
    
    # Fetch data
    data = cursor.fetchall()
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["Name"])
    
    # Save to Excel
    excel_filename = "topics_names.xlsx"
    df.to_excel(excel_filename, index=False)
    
    print(f"Data successfully saved to {excel_filename}")

except Exception as e:
    print(f"Error: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
