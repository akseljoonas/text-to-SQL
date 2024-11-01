from utils.execution_utils import create_sql_queries, compare_retrievals

# Paths to files 
#DELETED IDs:
# lora, finetuned: 518, 701
# base modeL: 584 (for generated), 701, 345
dataset_path = "data/generations/base_model_generations_cleaned.json"

DATABASE_DIR = "databases/dev_databases/"  # Directory where your database subfolders are stored

# Number of items to process (set to None to process all items, or an integer to limit)
test_limit = None  # Set this to None to process all items, or any integer to limit to first N items

original_retrievals, test_retrievals = create_sql_queries(dataset_path=dataset_path,
                                    database_path=DATABASE_DIR,
                                    test_limit=test_limit)

# Compare the two arrays and print the result
matching, total = compare_retrievals(original_retrievals, test_retrievals)

print(f"Matching entries: {matching}/{total}")