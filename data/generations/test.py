import json
dataset_path = "data/generations/base_model_generations_cleaned.json"

# Read the JSON file containing the SQL queries
with open(dataset_path, 'r') as json_file:
    data = json.load(json_file)
    counter = 0
    for entry in data:
        if entry["Generated SQL"] == None:
            counter += 1
    print(f"'None' in generated sql:{counter}")