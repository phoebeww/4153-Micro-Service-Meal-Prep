from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import uvicorn
import os
import logging
import time
from typing import Optional
import mysql.connector
from mysql.connector import Error

# Define the database connection configuration
db_config = {
    'host': '35.196.59.220',
    'port': 3306,
    'user': 'root',
    'password': 'dbuserdbuser',
    'database': 'mealplan_db' 
}

where_am_i = os.environ.get("WHEREAMI", None)
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS to allow Angular frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], #Angular frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Establish database connection globally (this is for demonstration purposes; consider using dependency injection in production)
connection = None

class MealPlanRequest(BaseModel):
    start_date: str  # in 'YYYY-MM-DD' format
    end_date: str    # in 'YYYY-MM-DD' format

def connect_to_db():
    global connection
    if not connection or not connection.is_connected():
        connection = mysql.connector.connect(**db_config)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    # Log before the request is processed
    start_time = time.time()

    # Call the next process in the pipeline
    response = await call_next(request)

    # Log after the request is processed
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} | Time: {process_time:.4f}s")

    return response

@app.get("/")
def hello_world():
    global where_am_i

    if where_am_i is None:
        where_am_i = "NOT IN DOCKER"

    return f'Hello, from {where_am_i}! I changed.'


# Endpoint to fetch data from the 'mealprep' table
# @app.get("/mealprep")
# def get_mealprep_data():
#     print("mealprepping")
#     try:
#         connect_to_db()
#         cursor = connection.cursor()
#         # cursor.execute("SELECT * FROM meal_plans;")
#         cursor.execute("SELECT wmp.* FROM weekly_meal_plans wmp JOIN daily_meal_plans dmp ON wmp.week_plan_id = dmp.week_plan_id WHERE dmp.date = '2024-10-25';")
#         rows = cursor.fetchall()

#         # Define column names (optional) for better readability
#         column_names = [column[0] for column in cursor.description]

#         # Format the result as a list of dictionaries
#         result = [dict(zip(column_names, row)) for row in rows]
#         return result

#     except Error as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {e}")

#     finally:
#         cursor.close()

@app.get("/mealprep")
def get_mealprep_data(date: str):
    print("Fetching meal prep data")
    try:
        connect_to_db()
        cursor = connection.cursor()

        # First query to get weekly meal plans
        query1 = """
        SELECT wmp.*
        FROM weekly_meal_plans wmp
        JOIN daily_meal_plans dmp ON wmp.week_plan_id = dmp.week_plan_id
        WHERE dmp.date = %s;
        """
        cursor.execute(query1, (date,))
        weekly_meal_plans = cursor.fetchall()
        
        # Get column names for the weekly meal plans
        weekly_column_names = [column[0] for column in cursor.description]
        weekly_result = [dict(zip(weekly_column_names, row)) for row in weekly_meal_plans]

        # Second query to get meal ids
        # query2 = """
        # SELECT meal_plans.*
        # FROM meal_plans
        # JOIN daily_meal_plans dmp ON dmp.meal_id = meal_plans.meal_id
        # WHERE dmp.date = %s;
        # """

        query2 = """
            SELECT 
                dmp.date,
                recipes_database.recipes_breakfast.name AS breakfast_recipe,
                recipes_database.recipes_lunch.name AS lunch_recipe,
                recipes_database.recipes_dinner.name AS dinner_recipe
            FROM mealplan_db.meal_plans
            JOIN mealplan_db.daily_meal_plans dmp ON dmp.meal_id = meal_plans.meal_id
            LEFT JOIN recipes_database.recipes AS recipes_breakfast ON meal_plans.breakfast_recipe = recipes_breakfast.recipe_id
            LEFT JOIN recipes_database.recipes AS recipes_lunch ON meal_plans.lunch_recipe = recipes_lunch.recipe_id
            LEFT JOIN recipes_database.recipes AS recipes_dinner ON meal_plans.dinner_recipe = recipes_dinner.recipe_id
            WHERE dmp.date = %s;
        """


        cursor.execute(query2, (date,))
        meals = cursor.fetchall()

        # Get column names for meals
        meals_column_names = [column[0] for column in cursor.description]
        meals_result = [dict(zip(meals_column_names, row)) for row in meals]

        # Combine results into a single response object
        combined_results = [weekly_result, meals_result]

        return combined_results

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        cursor.close()


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=5002)
