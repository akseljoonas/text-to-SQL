import pandas as pd 
import json

from utils.schema_linking_utils import generate_schema_for_instance

# The database directory needs to be downloaded manually and added to the repository
BASE_DABATASES_DIR =  "databases/dev_databases/" 

dataset = "data/raw/MINIDEV/mini_dev_sqlite.json"
output_file_path = "data/processed/MINIDEV/mini_dev_dataset.json"

df = pd.read_json(dataset)

# Loop over each row and generate schema for each instance
for idx, row in df.iterrows():
# Generate the schema for the current row
    database_schema = generate_schema_for_instance(row, BASE_DABATASES_DIR)
        
    # Add the generated schema to a new field 'database_schema' in the row
    df.at[idx, 'database_schema'] = database_schema


# Specify the file name
file_name = output_file_path

# Convert DataFrame to dictionary
data = df.to_dict(orient="records")

# Write the dictionary to a JSON file
with open(file_name, 'w') as json_file:
    json.dump(data, json_file, indent=4)
