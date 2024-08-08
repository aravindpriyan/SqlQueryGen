from flask import Flask, request, jsonify
import duckdb
import vanna
from vanna.remote import VannaDefault
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Initialize Vanna with your API key and model name
api_key = os.getenv("API_KEY")
vanna_model_name = os.getenv("VANNA_MODEL_NAME")
vn = VannaDefault(model=vanna_model_name, api_key=api_key)

# Create and populate table in DuckDB
def initialize_database(conn):
    conn.execute("""
        CREATE TABLE Table5 AS SELECT * FROM 'listings.csv';
        SELECT * FROM Table5
    """)

@app.route('/generateSql', methods=['POST'])
def generate_sql():
    try:
        # Create a new DuckDB connection for each request
        duckdb_conn = duckdb.connect(':memory:')
        initialize_database(duckdb_conn)

        # Get the question from the request body
        data = request.json
        question = data.get('question')

        if not question:
            return jsonify({"error": "No question provided"}), 400

        # Retrieve information schema using PRAGMA table_info
        #df_information_schema = duckdb_conn.execute("""
        #    PRAGMA table_info('Table5')
        #""").fetchdf()

        # Generate a training plan
        #plan = vn.get_training_plan_generic(df_information_schema)

        # Uncomment if you want to train the model
        # vn.train(plan=plan)

        # Ask the question and generate SQL
        response = vn.ask(question, visualize=False)
        sql_query = vn.generate_sql(question)

        return jsonify({"response": response, "sql_query": sql_query}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
