import os
import psycopg2
import openai
import json
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader  # Only for reading files

# Load environment variables
load_dotenv()

# Fetch environment variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Connect to PostgreSQL (Supabase DB)
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    cursor = connection.cursor()
    print("Connected to database successfully!")
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()

# Load documents
documents = SimpleDirectoryReader(
    "/Users/youssef/Desktop/Audi/Test").load_data()

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY


def get_embedding(text):
    """Fetch the OpenAI embedding for a given text."""
    response = openai.embeddings.create(
        input=text, model="text-embedding-ada-002"
    )
    return response.data[0].embedding


# Insert each document into the Supabase table
for doc in documents:
    text_content = doc.text
    embedding = get_embedding(text_content)

    # Convert embedding list to JSON for storage
    embedding_json = json.dumps(embedding)

    try:
        cursor.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            (text_content, embedding_json)
        )
        connection.commit()
        print("Inserted document successfully!")
    except Exception as e:
        print(f"Failed to insert document: {e}")
        connection.rollback()


# Close connection
cursor.close()
connection.close()
print("Connection closed.")
