import json
import os
import sqlite3


def create_sql_queries(dataset_path:str = None, database_path:str = None, test_limit:int = None) -> tuple:
    # Read the JSON file containing the SQL queries
    with open(dataset_path, 'r') as json_file:
        data = json.load(json_file)

    # Limit the number of items if test_limit is set
    if test_limit is not None:
        data = data[:test_limit]

    # Initialize an empty list to store the query results
    original_query_results = []
    generated_query_results = []
    successful_retrievals = 0
    # Loop through each item in the data
    for idx, item in enumerate(data):
        db_id = item['db_id']  # Get the database ID (db folder name)
        original_query = item['Original SQL']    # Get the SQL query
        generated_query = item['Generated SQL']    # Get the SQL query
        question_id = item['question_id']  # Get the question ID


        # Construct the path to the database file
        db_path = os.path.join(database_path, db_id, f"{db_id}.sqlite")

        # Check if the database file exists
        if not os.path.exists(db_path):
            print(f"Database file '{db_path}' not found for question {question_id}")
            original_query_results.append([])
            generated_query_results.append([])
        else:
            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            try:
                # Execute the SQL query
                cursor.execute(original_query)
                # Fetch the results
                original_rows = cursor.fetchall()
                # Flatten the result to a single list (flat array)
                original_query_result = [item for row in original_rows for item in row]  # Flatten the list of tuples
                print(f"Original Query executed successfully for question {question_id}.")
                # Append the flat result to the list of all results
                original_query_results.append([original_query_result])

            except Exception as e:
                # Handle any errors that occur during query execution
                print(f"Error executing Original query for question {question_id}: {e}")
                original_query_results.append([])  # Append an empty list in case of error

            try:
                cursor.execute(generated_query)
                generated_rows = cursor.fetchall()
                # Flatten the result to a single list (flat array)
                generated_query_result = [item for row in generated_rows for item in row]  # Flatten the list of tuples
                print(f"Generated Query executed successfully for question {question_id}.")
                successful_retrievals += 1
                # Append the flat result to the list of all results
                generated_query_results.append([generated_query_result])

            except Exception as e:
                # Handle any errors that occur during query execution
                print(f"Error executing Generated query for question {question_id}: {e}")
                generated_query_results.append([])  # Append an empty list in case of error

            finally:
                # Close the database connection
                conn.close()

    print(f"Successful retrievals: {successful_retrievals}/500")
    return original_query_results, generated_query_results

# Function to compare two arrays entry by entry
def compare_retrievals(array1, array2):
    total_entries = len(array1)
    matching_entries = 0

    for entry1, entry2 in zip(array1, array2):
        if entry1 == entry2:
            matching_entries += 1

    return matching_entries, total_entries