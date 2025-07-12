import sqlite3
def describe_schema(db_path):

    ### generating a schema description ##
    #conn = sqlite3.connect('/home/shivargha/langGraph-agentic-playground/InsightQuery_Agent/Chinook_Sqlite.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ## Select all tables ##
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    schema_description = ""
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        schema_description += f"\nTable: {table}\n"
        for col in columns:
            schema_description += f" - {col[1]} ({col[2]})\n"

    return schema_description

if __name__ == "__main__":
    db_path = "/home/shivargha/langGraph-agentic-playground/SQLQuery_Agent/Chinook_Sqlite.sqlite"
    schema = describe_schema(db_path)
    print(schema)