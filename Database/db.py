import json
from datetime import datetime
from sqlite3 import connect
from typing import List, Dict, Any, Optional
from typing import Union

class JSONDatabase:
    def __init__(self, filename="Database/data.json"):
        self.filename = filename
        self._load_data()

    def _load_data(self):
        """Load database from JSON file."""
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {
                "PROJECT": [], "EVENT": [], "RESEARCHER": [], "WORK": [], 
                "RESERVE": [], "PARTICIPATE": [], "COLLABORATE": [], 
                "ASSIGN": [], "PUBLICATION": [], "EQUIPEMENT": [], 
                "PARTNER": [], "LABORATORY": [], "GRADE": [], "TYPE_EV": []
            }
            self._save_data()

    def _save_data(self):
        """Save database to JSON file."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)

    def select_query(self, table: str) -> List[Dict[str, Any]]:
        """Retrieve all records from a table."""
        return self.data.get(table, [])

    def select_filter(self, table: str, filters: Dict) -> List[Dict[str, Any]]:
        """Retrieve records from a table with optional filters."""
        results = []
        items = self.data.get(table, [])
        
        for item in items:
            matches_all_filters = True
            for key, value in filters.items():
                # Debug prints (optional)
                # print("filters")
                # print(key, value)
                # print("element key,value")
                # print(key, item.get(key, "N/A"))  # Safer access with .get()
                
                if key not in item or str(item.get(key, "N/A")) != str(value):
                    # print(item)
                    matches_all_filters = False
                    break
            
            if matches_all_filters:
                results.append(item)
        
        return results
    
    def get_item(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single record from a table filtered by id."""
        return next((item for item in self.data.get(table, []) if item.get("id") == id), None)

    def insert_query(self, table: str, record: Dict[str, Any]):
        """Insert a new record into a table."""
        record["id"] = len(self.data[table]) + 1  # Auto-increment ID
        self.data[table].append(record)
        self._save_data()
        return record["id"]

    def update_query(self, table: str, record_id: int, updates: Dict[str, Any]) -> bool:
        """Update a record by ID."""
        for i, record in enumerate(self.data[table]):
            if record["id"] == record_id:
                # Create updated record by merging existing and new data
                updated_record = record.copy()
                for key, value in updates.items():
                    updated_record[key] = value
                # Ensure ID remains unchanged
                updated_record["id"] = record_id
                # Update timestamp if present
                if "timestamp" in updated_record:
                    updated_record["timestamp"] = datetime.now().isoformat()
                # Replace old record
                self.data[table][i] = updated_record
                self._save_data()
                return True
        return False

    def delete_query(self, table: str, record_id: int) -> bool:
        """Delete a record by ID."""
        initial_length = len(self.data[table])
        self.data[table] = [r for r in self.data[table] if r["id"] != record_id]
        if len(self.data[table]) < initial_length:
            self._save_data()
            return True
        return False

    def close(self):
        """Close the database (not needed for JSON but kept for compatibility)."""
        pass

class Database:
    def __init__(self, db_type: str = "sqlite", **kwargs):
        self.db_type = db_type.lower()
        
        if self.db_type == "sqlite":
            self.conn = connect(kwargs.get("db_path", "Database/data.db"))
            self.cursor = self.conn.cursor()
        elif self.db_type == "json":
            self.conn = JSONDatabase(kwargs.get("json_path", "Database/data.json"))
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def execute_query(self, query: str, params: tuple = None):
        """Execute a query (SQLite only)."""
        if self.db_type != "sqlite":
            raise NotImplementedError("execute_query is only available for SQLite databases")
            
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def select_query(self, query: str = None, table: str = None, conditions: Dict[str, Any] = None) -> List[Union[Dict[str, Any], tuple]]:
        """Retrieve records from the database."""
        if self.db_type == "sqlite":
            if query:
                self.cursor.execute(query)
                columns = [desc[0] for desc in self.cursor.description]
                return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            else:
                raise ValueError("Query required for SQLite select")
        else:
            if conditions:
                return self.conn.select_filter(table, conditions)
            return self.conn.select_query(table)

    def insert_query(self, query: str = None, table: str = None, record: Dict[str, Any] = None) -> int:
        """Insert a new record into the database."""
        if self.db_type == "sqlite":
            if not query:
                raise ValueError("Query required for SQLite insert")
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.lastrowid
        else:
            if not table or not record:
                raise ValueError("Table and record required for JSON insert")
            return self.conn.insert_query(table, record)

    def update_query(self, query: str = None, table: str = None, record_id: int = None, updates: Dict[str, Any] = None) -> bool:
        """Update a record in the database."""
        if self.db_type == "sqlite":
            if not query:
                raise ValueError("Query required for SQLite update")
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount > 0
        else:
            if not table or record_id is None or not updates:
                raise ValueError("Table, record_id and updates required for JSON update")
            return self.conn.update_query(table, record_id, updates)

    def delete_query(self, query: str = None, table: str = None, record_id: int = None) -> bool:
        """Delete a record from the database."""
        if self.db_type == "sqlite":
            if not query:
                raise ValueError("Query required for SQLite delete")
            self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.rowcount > 0
        else:
            if not table or record_id is None:
                raise ValueError("Table and record_id required for JSON delete")
            return self.conn.delete_query(table, record_id)

    def create_table(self, query: str = None, table_name: str = None):
        """Create a table in the database."""
        if self.db_type == "sqlite":
            if not query:
                raise ValueError("Query required for SQLite table creation")
            self.cursor.execute(query)
            self.conn.commit()
        else:
            # For JSON, tables are automatically created when first used
            pass

    def create_tables(self):
        """Create all tables for the research database."""
        if self.db_type == "sqlite":
            self._create_sqlite_tables()
        else:
            # JSON database doesn't need explicit table creation
            print("JSON database initialized with all required tables")

    def _create_sqlite_tables(self):
        """Create all SQLite tables."""
        # Implementation not provided in the original code
        pass

    def close(self):
        """Close the database connection."""
        if self.db_type == "sqlite":
            self.conn.close()
        else:
            pass

if __name__ == "__main__":
    db = JSONDatabase()
    
    # Get a specific item
    projects = db.get_item("PROJECT", 1)
    print("project item:", projects)

    researchers = db.get_item("RESEARCHER", 1)
    print("researcher item:", researchers)

    events = db.get_item("EVENT", 1)
    print("event item:", events)

    ev_types = db.get_item("TYPE_EV", 1)
    print("event type item:", ev_types)