import sqlite3
import numpy as np
import pandas as pd
import os
import re


# The schema linking code is largely based on DTS-SQL code by Mohammad Pourreza:
# https://github.com/MohammadrezaPourreza/DTS-SQL


def get_all_table_names(db_uri: str) -> list[str]:
    conn = sqlite3.connect(db_uri)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cursor.fetchall()
    conn.close()
    return [table_name[0] for table_name in table_names]

def get_table_schema_with_samples(
    db_uri: str, table_name: str, sample_limit: int = 0, columns_description: dict[str, str] = {}
) -> str:
    conn = sqlite3.connect(db_uri)
    cursor = conn.cursor()

    # Fetch table schema
    cursor.execute(f"PRAGMA table_info(`{table_name}`);")
    columns = cursor.fetchall()
    cursor.execute(f"PRAGMA foreign_key_list(`{table_name}`);")
    foreign_keys = cursor.fetchall()
    cursor.execute(f"PRAGMA index_list(`{table_name}`);")
    primary_key_indices = cursor.fetchall()
    primary_key_columns = []

    for index_info in primary_key_indices:
        index_name = index_info[1]
        cursor.execute(f"PRAGMA index_info(`{index_name}`);")
        index_columns = cursor.fetchall()
        primary_key_columns.extend(column[2] for column in index_columns)

    # Construct CREATE TABLE statement
    schema_str = f"CREATE TABLE `{table_name}` (\n"
    for column in columns:
        column_name = column[1]
        data_type = column[2]
        schema_str += f"  {column_name} {data_type}"
        if column_name in primary_key_columns:
            schema_str += " PRIMARY KEY"
        for foreign_key in foreign_keys:
            if column_name == foreign_key[3]:
                schema_str += f" REFERENCES {foreign_key[2]}({foreign_key[4]})"
        if column_name in columns_description:
            schema_str += f" -- '{columns_description[column_name]}'"

        schema_str += ",\n"
    schema_str = schema_str.rstrip(",\n")
    schema_str += "\n);\n"

    
    cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {sample_limit};")
    sample_rows = cursor.fetchall()

    if len(sample_rows) > 0:
        schema_str += f"Sample rows from `{table_name}`:\n"
        for row in sample_rows:
            formatted_row = ", ".join(str(item) for item in row)
            schema_str += f"{formatted_row}\n"

    conn.close()
    return schema_str

def remove_spaces(text):
  return re.sub(r'\s+', ' ', text)

def load_descriptions(db_path: str, table_name: str) -> list[str]:
    if not os.path.exists(f"{db_path}/database_description/{table_name}.csv"):
        return {}
    try:
        df = pd.read_csv(f"{db_path}/database_description/{table_name}.csv")
    except Exception:
        return {}
    if "column_description" not in df.columns or "value_description" not in df.columns:
        return {}
    columns_description = {}
    for index, row in df.iterrows():
        if np.nan != row["column_description"] and pd.notna(row["column_description"]):
            columns_description[row["original_column_name"]] = remove_spaces(row["column_description"])
            if np.nan != row["value_description"] and pd.notna(row["value_description"]):
                columns_description[row["original_column_name"]] += f" has values: ({remove_spaces(row['value_description'])})"
    return columns_description

def generate_schema_for_instance(row, base_databases_dir):
    db_id = row['db_id']
    
    # Set up database paths
    db_uri = f"{base_databases_dir}/{db_id}/{db_id}.sqlite"
    
    # Get table names and build schema
    table_names = get_all_table_names(db_uri)
    database_schema = ""
    
    for table_name in table_names:
        columns_description = load_descriptions(db_id, table_name)
        schema = get_table_schema_with_samples(db_uri, table_name, 0, columns_description)
        database_schema += schema + "\n"
    
    return database_schema.strip()