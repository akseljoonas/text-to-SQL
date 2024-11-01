from utils.execution_utils import create_sql_queries, compare_retrievals

DATABASE_DIR = "databases/dev_databases/"

# path to the json file containing the generated and true sql queries
dataset_path = "data/generations/full_finetuned_generations.json"

test_limit = None  # Set this to None to process all items, or any integer to limit to first N items

original_retrievals, test_retrievals = create_sql_queries(dataset_path=dataset_path,
                                    database_path=DATABASE_DIR,
                                    test_limit=test_limit)

# Compare the two arrays and print the result
matching, total = compare_retrievals(original_retrievals, test_retrievals)

print(f"Matching entries: {matching}/{total}")