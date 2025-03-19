import openai
import pandas as pd
import re
import json

def clean_html(text):
    """Removes HTML tags and extra whitespace from the text."""
    clean_text = re.sub(r"<[^>]*>", " ", text)  # Remove HTML tags
    clean_text = re.sub(r"\s+", " ", clean_text).strip()  # Remove extra spaces
    return clean_text

def load_email_data(excel_file):
    """Loads the email data, extracts 'bodyHTML' column, and concatenates all content."""
    try:
        df = pd.read_excel(excel_file)

        if "bodyHTML" not in df.columns:
            print("Error: 'bodyHTML' column not found in Excel file.")
            return None

        # Clean HTML content and join all emails into a single text
        all_text = " ".join(clean_html(text) for text in df["bodyHTML"].dropna())

        # Check token size (Approximation: 1 word ≈ 1.3 tokens)
        token_estimate = len(all_text.split())  
        print(f"📊 Processed Text Size: ~{token_estimate} tokens")

        return all_text

    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None

def summarize_large_email_data_single_call(excel_file, output_summary_file="email_summary.json"):
    """Summarizes the entire email dataset in one API call."""
    all_text = load_email_data(excel_file)
    
    if not all_text or len(all_text.strip()) == 0:
        print("❌ No valid text data found!")
        return

    # Ensure text fits within OpenAI's 128k token limit
    MAX_WORDS = 90000  # Keep buffer for token limit
    all_text = " ".join(all_text.split()[:MAX_WORDS])

    model_name = "gpt-4-turbo"

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Initialize OpenAI Client
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},  # ✅ Correct format
            messages=[
                {"role": "system", "content": "You are an AI that summarizes long emails. You must respond in a structured JSON format."},
                {"role": "user", "content": f"Summarize this text:\n{all_text}. Format the response as follows and give 5 headings and descriptions:\n\n{{'response': [{{'heading': 'Title', 'description': 'Summary'}}]}}"}
            ],
            max_tokens=2000
        )


        
        # Extract structured JSON response
        final_summary = response.choices[0].message.content.strip()
        parsed_summary = json.loads(final_summary)  # Convert string to JSON

        # Save the summary to a file
        with open(output_summary_file, "w", encoding="utf-8") as f:
            json.dump(parsed_summary, f, indent=2)

        print(f"✅ Summary saved in {output_summary_file}")

    except Exception as e:
        print(f"❌ Error in OpenAI API call: {e}")

# Example Usage
if __name__ == "__main__":
    excel_file = "Housing_1_2020.xlsx"  # Change this to your actual Excel file
    final_file=f'data/{excel_file}'
    summarize_large_email_data_single_call(final_file)
