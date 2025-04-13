import json
from datetime import datetime
from typing import List, Dict, Any, Optional

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

    def get_item(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single record from a table filtered by id.
        
        Args:
            table: Name of the table to query
            id: ID of the record to retrieve
            
        Returns:
            The matching record or None if not found
        """
        return next((item for item in self.data.get(table, []) if item.get("id") == id), None)

    def insert_query(self, table: str, record: Dict[str, Any]):
        """Insert a new record into a table."""
        record["id"] = len(self.data[table]) + 1  # Auto-increment ID
        self.data[table].append(record)
        self._save_data()

    def update_query(self, table: str, record_id: int, updates: Dict[str, Any]):
        """Update a record by ID."""
        for record in self.data[table]:
            if record["id"] == record_id:
                record.update(updates)
                self._save_data()
                return True
        return False  # If record not found

    def delete_query(self, table: str, record_id: int):
        """Delete a record by ID."""
        self.data[table] = [r for r in self.data[table] if r["id"] != record_id]
        self._save_data()

    def close(self):
        """Close the database (not needed for JSON but kept for compatibility)."""
        pass

# Example Usage
if __name__ == "__main__":
    db = JSONDatabase()
    

    # Get a specific item
    research = db.get_item("", 1)
    print("research item:", research)
    


