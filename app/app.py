from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import execute_values
from langchain_openai import OpenAIEmbeddings
import os

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:0000@localhost/kelog')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

print(f"OpenAI API Key: {OPENAI_API_KEY}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {str(e)}")
    exit(1)

try:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                embedding vector(1536)
            )
        """)
        conn.commit()
    print("Table 'articles' created or already exists")
except Exception as e:
    print(f"Error creating table: {str(e)}")
    exit(1)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)

@app.route('/article', methods=['POST'])
def create_article():
    try:
        data = request.json
        article_id = data['id']
        title = data['title']
        embedding = embeddings.embed_query(title)
        
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO articles (id, title, embedding) VALUES (%s, %s, %s) RETURNING id",
                (article_id, title, embedding)
            )
            inserted_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({"id": inserted_id}), 201
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error creating article: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/article/<int:id>', methods=['PUT'])
def update_article(id):
    try:
        data = request.json
        embedding = embeddings.embed_query(data['title'])
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE articles SET title = %s, embedding = %s WHERE id = %s",
                (data['title'], embedding, id)
            )
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"error": "Article not found"}), 404
            return jsonify({"id": id}), 204
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error updating article: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/article/<int:id>', methods=['DELETE'])
def delete_article(id):
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM articles WHERE id = %s", (id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"error": "Article not found"}), 404
            return jsonify({"id": id}), 204
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error deleting article: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/article/<int:id>/similar', methods=['GET'])
def get_similar_articles(id):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT embedding FROM articles WHERE id = %s", (id,))
            result = cur.fetchone()
            if result is None:
                return jsonify({"error": "Article not found"}), 404
            embedding = result[0]
            cur.execute(
                "SELECT id FROM articles WHERE id != %s ORDER BY embedding <-> %s LIMIT 10",
                (id, embedding)
            )
            similar_ids = [row[0] for row in cur.fetchall()]
            print(similar_ids)
        return jsonify({"similar_ids": similar_ids})
    except Exception as e:
        app.logger.error(f"Error finding similar articles: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)