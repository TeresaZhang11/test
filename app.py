from flask import Flask, request, jsonify
import mysql.connector
from openai import OpenAI
import json
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
)

db_config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': 'sys'
}


app = Flask(__name__)


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({
            'error': 'Invalid Question'
        }), 400
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user","content": question,
                }
            ],
            model="gpt-3.5-turbo", 
        )
        print(response.model_dump_json())
        response = json.loads(response.model_dump_json())
        response = response['choices'][0]['message']['content']
        print(response)

        

        return jsonify({
            'question':question,
            'response': response
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500



def save_data(question, response):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "INSERT INTO history (question, answer) VALUES (%s, %s)"
        cursor.execute(query, (question, response))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
# save_data("question", "response")

@app.route('/history', methods=['GET'])
def history():
    connection = None
    cursor = None
    try:

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True) 

        query = "SELECT question, answer FROM history"
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    app.run()
    



