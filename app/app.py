import os
import logging
from flask import Flask, request, jsonify

import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("MYSQL_DATABASE", "todo_db")
DB_USER = os.getenv("MYSQL_USER", "todo_user")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "todo_password")


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        logging.info("Database initialized")

    except Error as error:
        logging.error("Database initialization failed: %s", error)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/health")
def health():
    try:
        connection = get_db_connection()

        if connection.is_connected():
            connection.close()
            return jsonify({
                "status": "healthy",
                "database": "connected"
            }), 200

    except Error as error:
        logging.error("Health check failed: %s", error)

    return jsonify({
        "status": "unhealthy",
        "database": "disconnected"
    }), 503


@app.route("/todos", methods=["GET"])
def get_todos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, completed FROM todos ORDER BY id DESC"
    )

    todos = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(todos)


@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    title = data["title"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO todos (title) VALUES (%s)",
        (title,)
    )

    connection.commit()

    todo_id = cursor.lastrowid

    cursor.close()
    connection.close()

    logging.info("Created todo %s", todo_id)

    return jsonify({
        "id": todo_id,
        "title": title,
        "completed": False
    }), 201


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()

    if not data or "completed" not in data:
        return jsonify({"error": "completed is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE todos SET completed = %s WHERE id = %s",
        (data["completed"], todo_id)
    )

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({"error": "Todo not found"}), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Todo updated successfully"
    })


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM todos WHERE id = %s",
        (todo_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({"error": "Todo not found"}), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Todo deleted successfully"
    })


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000
    )
