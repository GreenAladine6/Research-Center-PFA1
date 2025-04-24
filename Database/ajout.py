from sqlite3 import connect
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union

# [Previous class definitions for JSONDatabase and Database remain exactly the same...]
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
            # Initialize with all required tables
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

    def select_query(self, table: str, conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve records from a table with optional conditions."""
        if table not in self.data:
            return []
        
        if not conditions:
            return self.data[table]
        
        results = []
        for record in self.data[table]:
            match = True
            for key, value in conditions.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                results.append(record)
        return results

    def insert_query(self, table: str, record: Dict[str, Any]):
        """Insert a new record into a table."""
        if table not in self.data:
            self.data[table] = []
        
        # Auto-increment ID if not provided
        if "id" not in record:
            max_id = max([r.get("id", 0) for r in self.data[table]] or [0])
            record["id"] = max_id + 1
        
        self.data[table].append(record)
        self._save_data()
        return record["id"]

    def update_query(self, table: str, record_id: int, updates: Dict[str, Any]):
        """Update a record by ID."""
        if table not in self.data:
            return False
            
        for record in self.data[table]:
            if record.get("id") == record_id:
                record.update(updates)
                self._save_data()
                return True
        return False

    def delete_query(self, table: str, record_id: int):
        """Delete a record by ID."""
        if table not in self.data:
            return False
            
        original_length = len(self.data[table])
        self.data[table] = [r for r in self.data[table] if r.get("id") != record_id]
        if len(self.data[table]) < original_length:
            self._save_data()
            return True
        return False

    def close(self):
        """For compatibility with Database interface."""
        pass

class Database:
    def __init__(self, db_type: str = "sqlite", **kwargs):
        self.db_type = db_type.lower()
        
        if self.db_type == "sqlite":
            self.conn = connect(kwargs.get("db_path", "./Database/data.db"))
            self.cursor = self.conn.cursor()
        elif self.db_type == "json":
            self.conn = JSONDatabase(kwargs.get("json_path", "Database/data.json"))
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    def close(self):
        """Close the database connection."""
        if self.db_type == "sqlite":
            self.conn.close()
        else:
            pass  # JSON database doesn't need explicit closing

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
            return self.conn.select_query(table, conditions)

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

    

    
        
def populate_sample_data(db: Database):
    """Populate the database with sample data."""
    print("\nPopulating database with sample data...")
    
    # Add researcher grades
    grades = [
        "Undergraduate Researcher",
        "Graduate Researcher",
        "PhD Candidate",
        "Postdoctoral Researcher",
        "Assistant Professor",
        "Associate Professor",
        "Full Professor",
        "Research Scientist",
        "Senior Research Scientist",
        "Principal Investigator"
    ]
    
    if db.db_type == "sqlite":
        for grade in grades:
            db.execute_query("INSERT INTO GRADE (NAME_GRADE) VALUES (?)", (grade,))
    else:
        for grade in grades:
            db.insert_query(table="GRADE", record={"NAME_GRADE": grade})
    
    # Add laboratories
    labs = [
        {"NAME_LAB": "Bioinformatics Lab", "DIRECTOR": "Dr. Alice Johnson"},
        {"NAME_LAB": "Neuroscience Research Center", "DIRECTOR": "Dr. Robert Chen"},
        {"NAME_LAB": "Quantum Computing Lab", "DIRECTOR": "Dr. Maria Garcia"},
        {"NAME_LAB": "Environmental Science Lab", "DIRECTOR": "Dr. James Wilson"}
    ]
    
    if db.db_type == "sqlite":
        for lab in labs:
            db.execute_query(
                "INSERT INTO LABORATORY (NAME_LAB, DIRECTOR) VALUES (?, ?)",
                (lab["NAME_LAB"], lab["DIRECTOR"])
            )
    else:
        for lab in labs:
            db.insert_query(table="LABORATORY", record=lab)
    
    # Add researchers (10 researchers)
    researchers = [
        {"FULL_NAME": "Dr. Sarah Miller", "NUM_TEL": 5551001, "EMAIL": "s.miller@univ.edu", "ID_GRADE": 6},
        {"FULL_NAME": "Prof. David Kim", "NUM_TEL": 5551002, "EMAIL": "d.kim@univ.edu", "ID_GRADE": 7},
        {"FULL_NAME": "Dr. Emily Zhang", "NUM_TEL": 5551003, "EMAIL": "e.zhang@univ.edu", "ID_GRADE": 5},
        {"FULL_NAME": "Dr. Michael Brown", "NUM_TEL": 5551004, "EMAIL": "m.brown@univ.edu", "ID_GRADE": 8},
        {"FULL_NAME": "Dr. Jessica Lee", "NUM_TEL": 5551005, "EMAIL": "j.lee@univ.edu", "ID_GRADE": 9},
        {"FULL_NAME": "Dr. Thomas Wilson", "NUM_TEL": 5551006, "EMAIL": "t.wilson@univ.edu", "ID_GRADE": 10},
        {"FULL_NAME": "Lisa Park", "NUM_TEL": 5551007, "EMAIL": "l.park@univ.edu", "ID_GRADE": 2},
        {"FULL_NAME": "Daniel Chen", "NUM_TEL": 5551008, "EMAIL": "d.chen@univ.edu", "ID_GRADE": 3},
        {"FULL_NAME": "Sophia Martinez", "NUM_TEL": 5551009, "EMAIL": "s.martinez@univ.edu", "ID_GRADE": 4},
        {"FULL_NAME": "Ryan Johnson", "NUM_TEL": 5551010, "EMAIL": "r.johnson@univ.edu", "ID_GRADE": 1}
    ]
    
    if db.db_type == "sqlite":
        for researcher in researchers:
            db.execute_query(
                "INSERT INTO RESEARCHER (FULL_NAME, NUM_TEL, EMAIL, ID_GRADE) VALUES (?, ?, ?, ?)",
                (researcher["FULL_NAME"], researcher["NUM_TEL"], researcher["EMAIL"], researcher["ID_GRADE"])
            )
    else:
        for researcher in researchers:
            db.insert_query(table="RESEARCHER", record=researcher)
    
    # Add projects (4 projects)
    projects = [
        {
            "NAME_PROJECT": "Genome Sequencing Initiative",
            "BUDGET": 1500000.00,
            "DATE_BEGIN": "2023-01-15",
            "DATE__END": "2025-12-31",
            "STATE": "Active",
            "ID_MANGER": 6  # Dr. Thomas Wilson as manager
        },
        {
            "NAME_PROJECT": "Quantum Algorithm Development",
            "BUDGET": 850000.00,
            "DATE_BEGIN": "2023-03-01",
            "DATE__END": "2024-06-30",
            "STATE": "Active",
            "ID_MANGER": 2  # Prof. David Kim as manager
        },
        {
            "NAME_PROJECT": "Climate Change Impact Study",
            "BUDGET": 1200000.00,
            "DATE_BEGIN": "2022-09-01",
            "DATE__END": "2023-08-31",
            "STATE": "Completed",
            "ID_MANGER": 1  # Dr. Sarah Miller as manager
        },
        {
            "NAME_PROJECT": "Neural Network Optimization",
            "BUDGET": 950000.00,
            "DATE_BEGIN": "2023-05-10",
            "DATE__END": "2024-11-30",
            "STATE": "Active",
            "ID_MANGER": 5  # Dr. Jessica Lee as manager
        }
    ]
    
    if db.db_type == "sqlite":
        for project in projects:
            db.execute_query(
                """INSERT INTO PROJECT (NAME_PROJECT, BUDGET, DATE_BEGIN, DATE__END, STATE, ID_MANGER)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (project["NAME_PROJECT"], project["BUDGET"], project["DATE_BEGIN"],
                 project["DATE__END"], project["STATE"], project["ID_MANGER"])
            )
    else:
        for project in projects:
            db.insert_query(table="PROJECT", record=project)
    
    # Add event types
   
    # Add events (4 events)
    today = datetime.now()
    events = [
        {
            "TYPE_EV": "Conference",
            "DATE_BEG": (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            "HEURE": "09:00:00",
            "LIEU": "Convention Center, Room A",
            "DATEND": (today + timedelta(days=32)).strftime("%Y-%m-%d"),
            "ID_ORGANISOR": 1
        },
        {
            "TYPE_EV": "Workshop",
            "DATE_BEG": (today + timedelta(days=45)).strftime("%Y-%m-%d"),
            "HEURE": "13:30:00",
            "LIEU": "Science Building, Room 101",
            "DATEND": (today + timedelta(days=45)).strftime("%Y-%m-%d"),
            "ID_ORGANISOR": 3
        },
        {
            "TYPE_EV": "Seminar",
            "DATE_BEG": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "HEURE": "11:00:00",
            "LIEU": "Main Auditorium",
            "DATEND": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "ID_ORGANISOR": 2
        },
        {
            "TYPE_EV": "Symposium",
            "DATE_BEG": (today + timedelta(days=60)).strftime("%Y-%m-%d"),
            "HEURE": "10:00:00",
            "LIEU": "University Hall",
            "DATEND": (today + timedelta(days=62)).strftime("%Y-%m-%d"),
            "ID_ORGANISOR": 4
        }
    ]
    
    if db.db_type == "sqlite":
        for event in events:
            db.execute_query(
                """INSERT INTO EVENT (TYPE_EV, DATE_BEG, HEURE, LIEU, DATEND, ID_ORGANISOR)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (event["TYPE_EV"], event["DATE_BEG"], event["HEURE"],
                 event["LIEU"], event["DATEND"], event["ID_ORGANISOR"])
            )
    else:
        for event in events:
            db.insert_query(table="EVENT", record=event)
    
    print("Sample data populated successfully!")

def test_database(db_type="sqlite"):
    print(f"\nTesting {db_type.upper()} database...")
    
    # Initialize database
    db = Database(db_type=db_type)
    
    
    # Populate with sample data
    populate_sample_data(db)
    
    # Query and display some data
    print("\nSample data verification:")
    
    # Display grades
    grades = db.select_query("SELECT * FROM GRADE") if db_type == "sqlite" else db.select_query(table="GRADE")
    print(f"\nGrades ({len(grades)} entries):")
    # for grade in grades:
        # print(f"ID: {grade['ID_GRADE'] if db_type == 'sqlite' else grade['id']}, Name: {grade['NAME_GRADE']}")
    
    # Display researchers
    researchers = db.select_query("SELECT * FROM RESEARCHER") if db_type == "sqlite" else db.select_query(table="RESEARCHER")
    print(f"\nResearchers ({len(researchers)} entries):")
    for researcher in researchers:
        print(f"ID: {researcher['ID_RESEARCHER'] if db_type == 'sqlite' else researcher['id']}, Name: {researcher['FULL_NAME']}, Grade: {researcher['ID_GRADE']}")
    
    # Display projects
    projects = db.select_query("SELECT * FROM PROJECT") if db_type == "sqlite" else db.select_query(table="PROJECT")
    print(f"\nProjects ({len(projects)} entries):")
    for project in projects:
        print(f"ID: {project['ID_PROJECT'] if db_type == 'sqlite' else project['id']}, Name: {project['NAME_PROJECT']}, STATE: {project['STATE']}, BUDGET: {project['BUDGET']}")
    
    # Display events
    events = db.select_query("SELECT * FROM EVENT") if db_type == "sqlite" else db.select_query(table="EVENT")
    print(f"\nEvents ({len(events)} entries):")
    for event in events:
        print(f"ID: {event['ID_EVENT'] if db_type == 'sqlite' else event['id']}, Type: {event['TYPE_EV']}, Date: {event['DATE_BEG']}")
    
    db.close()
    print(f"\n{db_type.upper()} database test completed")

if __name__ == "__main__":
    print(f"Starting database setup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both database types
    test_database("sqlite")
    test_database("json")
    
    print("\nDatabase setup and population completed successfully!")