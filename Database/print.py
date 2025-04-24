import sqlite3

def get_all_tables_and_columns(db_path='./Database/data.db'):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Dictionary to store table structure
        database_schema = {}
        
        for table in tables:
            table_name = table[0]
            
            # Get column information for each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Store column details
            database_schema[table_name] = [
                {
                    'name': col[1],         # Column name
                    'type': col[2],         # Data type
                    'not_null': bool(col[3]),  # NOT NULL constraint
                    'default': col[4],       # Default value
                    'primary_key': bool(col[5])  # Is primary key
                }
                for col in columns
            ]
        
        return database_schema
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        conn.close()

def print_database_schema(schema,db_path='./Database/data.db'):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if not schema:
        print("No schema information available")
        return
    
    for table_name, columns in schema.items():
        print(f"\nTable: {table_name}")
        print("-" * (len(table_name) + 8))
        cursor.execute(f"SELECT * FROM {table_name};")
       
        # Fetch all rows from the table
        items = cursor.fetchall()
        print(f"Number of rows: {len(items)}")
        print(f"Number of columns: {len(columns)}")
        print(f"{'Column Name':<20} {'Data Type':<15} {'Constraints'}")
        print("-" * 50)
        for item in items:
            print(item)
        print("-" * 50)
        for col in columns:
            constraints = []
            if col['not_null']:
                constraints.append("NOT NULL")
            if col['primary_key']:
                constraints.append("PRIMARY KEY")
            if col['default'] is not None:
                constraints.append(f"DEFAULT {col['default']}")
                
            constraints_str = " ".join(constraints)
            print(f"{col['name']:20} {col['type']:15} {constraints_str}")


if __name__ == '__main__':
    schema = get_all_tables_and_columns()
    if schema:
        print_database_schema(schema)