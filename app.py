from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import mysql.connector
from mysql.connector import Error

# Define the database connection configuration
db_config = {
    'host': '35.196.59.220',  # The IP address of your MySQL instance
    'port': 3306,  # Default port for MySQL
    'user': 'root',  # The user you want to connect as
    'password': 'dbuserdbuser',  # Replace with your actual password
    'database': 'mealprep_db'  # The name of your database
}

app = FastAPI()

# Enable CORS to allow Angular frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Replace with your Angular frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Establish database connection globally (this is for demonstration purposes; consider using dependency injection in production)
connection = None


def connect_to_db():
    global connection
    if not connection or not connection.is_connected():
        connection = mysql.connector.connect(**db_config)


@app.get("/")
def hello_world():
    global where_am_i

    if where_am_i is None:
        where_am_i = "NOT IN DOCKER"

    return f'Hello, from {where_am_i}! I changed.'


# Endpoint to fetch data from the 'mealprep' table
@app.get("/mealprep")
def get_mealprep_data():
    print("mealprepping")
    try:
        connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM meal_plans;")  # Replace 'mealprep' with your actual table name
        rows = cursor.fetchall()

        # Define column names (optional) for better readability
        column_names = [column[0] for column in cursor.description]

        # Format the result as a list of dictionaries
        result = [dict(zip(column_names, row)) for row in rows]
        return result

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        cursor.close()


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
