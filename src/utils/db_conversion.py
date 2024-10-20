import sqlite3
import oracledb
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def map_sqlite_type_to_oracle(sqlite_type):
    sqlite_type = sqlite_type.upper()
    if "INT" in sqlite_type:
        return "NUMBER(38)"
    elif "CHAR" in sqlite_type or "CLOB" in sqlite_type or "TEXT" in sqlite_type:
        return "VARCHAR2(4000)"
    elif "BLOB" in sqlite_type:
        return "BLOB"
    elif "REAL" in sqlite_type or "FLOA" in sqlite_type or "DOUB" in sqlite_type:
        return "FLOAT"
    elif "NUM" in sqlite_type or "DEC" in sqlite_type:
        return "NUMBER"
    else:
        return "VARCHAR2(4000)"  # Default mapping


def create_oracle_table_from_sqlite_schema(sqlite_cursor, table_name):
    # Get column info from SQLite
    sqlite_cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns_info = sqlite_cursor.fetchall()

    # columns_info: (cid, name, type, notnull, dflt_value, pk)
    column_definitions = []
    pk_columns = []
    for col in columns_info:
        col_name = col[1]
        col_type = col[2]
        not_null = col[3]
        default_value = col[4]
        pk = col[5]

        # Map data types
        oracle_col_type = map_sqlite_type_to_oracle(col_type)

        # Construct column definition
        col_def = f'"{col_name}" {oracle_col_type}'
        if not_null:
            col_def += " NOT NULL"
        if default_value is not None:
            col_def += f" DEFAULT {default_value}"
        column_definitions.append(col_def)

        if pk:
            pk_columns.append(f'"{col_name}"')

    # Handle primary key constraint
    pk_constraint = ""
    if pk_columns:
        pk_columns_str = ", ".join(pk_columns)
        pk_constraint = (
            f',\n  CONSTRAINT "{table_name}_pk" PRIMARY KEY ({pk_columns_str})'
        )

    columns_sql = ",\n  ".join(column_definitions)
    create_table_sql = (
        f'CREATE TABLE "{table_name}" (\n  {columns_sql}{pk_constraint}\n)'
    )

    return create_table_sql


def main(sqlite_db_path, oracle_username, oracle_password, oracle_dsn):
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()
        logger.info("Connected to SQLite database.")

        # Connect to Oracle
        oracle_conn = oracledb.connect(
            user=oracle_username, password=oracle_password, dsn=oracle_dsn
        )
        oracle_cursor = oracle_conn.cursor()
        logger.info("Connected to Oracle database.")

        # Fetch tables from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cursor.fetchall()
        logger.info(f"Found {len(tables)} tables in SQLite database.")

        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            logger.info(f"Processing table {table_name}.")

            try:
                # Create Oracle table from SQLite schema
                oracle_create_table_sql = create_oracle_table_from_sqlite_schema(
                    sqlite_cursor, table_name
                )
                logger.debug(
                    f"Oracle CREATE TABLE SQL for {table_name}:\n{oracle_create_table_sql}"
                )

                # Drop table if exists
                try:
                    oracle_cursor.execute(
                        f'DROP TABLE "{table_name}" CASCADE CONSTRAINTS'
                    )
                    oracle_conn.commit()
                    logger.info(f"Dropped existing table {table_name} in Oracle.")
                except oracledb.DatabaseError as e:
                    (error_obj,) = e.args
                    if error_obj.code == 942:  # ORA-00942: table or view does not exist
                        logger.info(
                            f"Table {table_name} does not exist in Oracle. No need to drop."
                        )
                    else:
                        raise

                # Create table in Oracle
                oracle_cursor.execute(oracle_create_table_sql)
                oracle_conn.commit()
                logger.info(f"Created table {table_name} in Oracle.")

                # Fetch data from SQLite table
                sqlite_cursor.execute(f"SELECT * FROM '{table_name}';")
                rows = sqlite_cursor.fetchall()
                logger.info(f"Fetched {len(rows)} rows from {table_name} in SQLite.")

                if rows:
                    # Get column names
                    column_names = [
                        description[0] for description in sqlite_cursor.description
                    ]
                    columns_str = ", ".join(f'"{col}"' for col in column_names)
                    placeholders = ", ".join(
                        [":" + str(i + 1) for i in range(len(column_names))]
                    )

                    # Prepare insert statement
                    insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
                    logger.debug(f"Insert SQL for {table_name}: {insert_sql}")

                    # Insert data into Oracle
                    oracle_cursor.executemany(insert_sql, rows)
                    oracle_conn.commit()
                    logger.info(
                        f"Inserted {len(rows)} rows into {table_name} in Oracle."
                    )
                else:
                    logger.info(f"No data to insert for table {table_name}.")

            except Exception as e:
                logger.exception(
                    f"Failed to process table {table_name}. Continuing with next table."
                )

        # Close connections
        sqlite_conn.close()
        oracle_conn.close()
        logger.info("Migration completed successfully.")

    except Exception as e:
        logger.exception("An error occurred during migration.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python migrate_sqlite_to_oracle.py <sqlite_db_path> <oracle_username> <oracle_password> <oracle_dsn>"
        )
        sys.exit(1)

    sqlite_db_path = sys.argv[1]
    oracle_username = sys.argv[2]
    oracle_password = sys.argv[3]
    oracle_dsn = sys.argv[4]

    main(sqlite_db_path, oracle_username, oracle_password, oracle_dsn)