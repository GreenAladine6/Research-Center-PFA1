from sqlite3 import connect
import json
from datetime import datetime
from typing import List, Dict, Any, Union

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

    def create_tables(self):
        """Create all tables for the research database."""
        if self.db_type == "sqlite":
            self._create_sqlite_tables()
        else:
            # JSON database doesn't need explicit table creation
            print("JSON database initialized with all required tables")

    def _create_sqlite_tables(self):
        """Create all SQLite tables."""
        # Drop existing tables if they exist
        self._drop_tables()
        
        # Create tables
        self._create_grade_table()
        self._create_laboratory_table()
        self._create_researcher_table()
        self._create_project_table()
        self._create_partner_table()
        self._create_equipement_table()
        self._create_type_ev_table()
        self._create_event_table()
        self._create_publication_table()
        self._create_assign_table()
        self._create_collaborate_table()
        self._create_participate_table()
        self._create_reserve_table()
        self._create_work_table()

        print("All SQLite tables created successfully")

    def _drop_tables(self):
        tables = [
            "WORK", "RESERVE", "PARTICIPATE", "COLLABORATE", "ASSIGN",
            "PUBLICATION", "EVENT", "EQUIPEMENT", "PARTNER", "PROJECT",
            "RESEARCHER", "LABORATORY", "GRADE", "TYPE_EV"
        ]
        
        for table in tables:
            try:
                self.execute_query(f"DROP TABLE IF EXISTS {table}")
            except Exception as e:
                print(f"Error dropping table {table}: {e}")

    def _create_grade_table(self):
        self.execute_query('''
        CREATE TABLE GRADE (
            ID_GRADE INTEGER PRIMARY KEY,
            NAME_GRADE TEXT
        )
        ''')

    def _create_laboratory_table(self):
        self.execute_query('''
        CREATE TABLE LABORATORY (
            LABO_ID INTEGER PRIMARY KEY,
            NAME_LAB TEXT,
            DIRECTOR TEXT,
            foreign key (DIRECTOR) references RESEARCHER(ID_RESEARCHER) ON DELETE CASCADE
        )
        ''')

    def _create_researcher_table(self):
        self.execute_query('''
        CREATE TABLE RESEARCHER (
            ID_RESEARCHER INTEGER PRIMARY KEY,
            ID_GRADE INTEGER NOT NULL,
            FULL_NAME TEXT NOT NULL,
            NUM_TEL INTEGER NOT NULL,
            EMAIL TEXT,
            FOREIGN KEY (ID_GRADE) REFERENCES GRADE(ID_GRADE) ON DELETE CASCADE
        )
        ''')

    def _create_project_table(self):
        self.execute_query('''
        CREATE TABLE PROJECT (
            ID_PROJECT INTEGER PRIMARY KEY,
            ID_MANGER INTEGER,
            NAME_PROJECT TEXT,
            BUDGET REAL,
            DATE_BEGIN TEXT,
            DATE__END TEXT,
            STATE TEXT,
            foreign key (ID_MANGER) references RESEARCHER(ID_RESEARCHER) ON DELETE CASCADE
        )
        ''')

    def _create_partner_table(self):
        self.execute_query('''
        CREATE TABLE PARTNER (
            ID_PARTNER INTEGER PRIMARY KEY,
            NAME_PARTNER TEXT,
            EMAIL_PARTNER TEXT NOT NULL,
            PHONE INTEGER NOT NULL,
            ADRESS TEXT NOT NULL,
            CREATION_DATE TEXT NOT NULL,
            WEBSITE TEXT,
            NOTES TEXT,
            AMOUNT REAL
        )
        ''')

    def _create_equipement_table(self):
        self.execute_query('''
        CREATE TABLE EQUIPEMENT (
            ID_EQUIPEMENT INTEGER PRIMARY KEY,
            NAME_EQUIPEMENT TEXT,
            PURCHASE_DATE TEXT,
            LABORATOIRE_ID INTEGER,
            FOREIGN KEY (LABORATOIRE_ID) REFERENCES LABORATORY(LABO_ID) ON DELETE CASCADE
        )
        ''')

    def _create_type_ev_table(self):
        self.execute_query('''
        CREATE TABLE TYPE_EV (
            TYPE_EV TEXT PRIMARY KEY,
            DESCRIPTION TEXT
        )
        ''')

    def _create_event_table(self):
        self.execute_query('''
        CREATE TABLE EVENT (
            ID_EVENT INTEGER PRIMARY KEY,
            TYPE_EV TEXT NOT NULL,
            DATE_BEG TEXT NOT NULL,
            HEURE TEXT NOT NULL,
            LIEU TEXT NOT NULL,
            DATEND TEXT,
            ID_ORGANISOR INTEGER,
            FOREIGN KEY (TYPE_EV) REFERENCES TYPE_EV(TYPE_EV),
            FOREIGN KEY (ID_ORGANISOR) REFERENCES RESEARCHER(ID_RESEARCHER) ON DELETE CASCADE
        )
        ''')

    def _create_publication_table(self):
        self.execute_query('''
        CREATE TABLE PUBLICATION (
            ID_PUB INTEGER PRIMARY KEY,
            ID_RESEARCHER INTEGER NOT NULL,
            TITLE TEXT,
            DATE_PUB TEXT,
            LIEN TEXT,
            FOREIGN KEY (ID_RESEARCHER) REFERENCES RESEARCHER(ID_RESEARCHER)
        )
        ''')

    def _create_assign_table(self):
        self.execute_query('''
        CREATE TABLE ASSIGN (
            LABO_ID INTEGER NOT NULL,
            ID_PROJECT INTEGER NOT NULL,
            PRIMARY KEY (LABO_ID, ID_PROJECT),
            FOREIGN KEY (LABO_ID) REFERENCES LABORATORY(LABO_ID),
            FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT)
        )
        ''')

    def _create_collaborate_table(self):
        self.execute_query('''
        CREATE TABLE COLLABORATE (
            ID_PARTNER INTEGER NOT NULL,
            ID_PROJECT INTEGER NOT NULL,
            PRIMARY KEY (ID_PARTNER, ID_PROJECT),
            FOREIGN KEY (ID_PARTNER) REFERENCES PARTNER(ID_PARTNER),
            FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT)
        )
        ''')

    def _create_participate_table(self):
        self.execute_query('''
        CREATE TABLE PARTICIPATE (
            ID_EVENT INTEGER NOT NULL,
            ID_RESEARCHER INTEGER NOT NULL,
            PRIMARY KEY (ID_EVENT, ID_RESEARCHER),
            FOREIGN KEY (ID_EVENT) REFERENCES EVENT(ID_EVENT),
            FOREIGN KEY (ID_RESEARCHER) REFERENCES RESEARCHER(ID_RESEARCHER)
        )
        ''')

    def _create_reserve_table(self):
        self.execute_query('''
        CREATE TABLE RESERVE (
            ID_PROJECT INTEGER NOT NULL,
            ID_EQUIPEMENT INTEGER NOT NULL,
            ID_RESERVATION INTEGER,
            START_DATE TEXT,
            END_DATE TEXT,
            PRIMARY KEY (ID_PROJECT, ID_EQUIPEMENT),
            FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT),
            FOREIGN KEY (ID_EQUIPEMENT) REFERENCES EQUIPEMENT(ID_EQUIPEMENT)
        )
        ''')

    def _create_work_table(self):
        self.execute_query('''
        CREATE TABLE WORK (
            ID_PROJECT INTEGER NOT NULL,
            ID_RESEARCHER INTEGER NOT NULL,
            PRIMARY KEY (ID_PROJECT, ID_RESEARCHER),
            FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT),
            FOREIGN KEY (ID_RESEARCHER) REFERENCES RESEARCHER(ID_RESEARCHER)
        )
        ''')

    def close(self):
        """Close the database connection."""
        if self.db_type == "sqlite":
            self.conn.close()
        else:
            pass  # JSON database doesn't need explicit closing

def test_database(db_type="sqlite"):
    print(f"\nTesting {db_type.upper()} database...")
    
    # Initialize database
    db = Database(db_type=db_type)
    db.create_tables()
    
    # Test data
    grade_data = {"NAME_GRADE": "Senior Researcher"} if db_type == "json" else None
    lab_data = {"NAME_LAB": "BioTech Lab", "DIRECTOR": "Dr. Smith"} if db_type == "json" else None
    
    # Insert test data
    if db_type == "sqlite":
        db.execute_query("INSERT INTO GRADE (NAME_GRADE) VALUES (?)", ("Senior Researcher",))
        db.execute_query("INSERT INTO LABORATORY (NAME_LAB, DIRECTOR) VALUES (?, ?)", 
                        ("BioTech Lab", "Dr. Smith"))
    else:
        db.insert_query(table="GRADE", record={"NAME_GRA": "Senior Researcher"})
        db.insert_query(table="LABORATORY", record={"NAME_LAB": "BioTech Lab", "DIRECTOR": "Dr. Smith"})
    
    # Query data
    grades = db.select_query("SELECT * FROM GRADE") if db_type == "sqlite" else db.select_query(table="GRADE")
    labs = db.select_query("SELECT * FROM LABORATORY") if db_type == "sqlite" else db.select_query(table="LABORATORY")
    
    print("Grades:", grades)
    print("Laboratories:", labs)
    
    db.close()
    print(f"{db_type.upper()} database test completed")

if __name__ == "__main__":
    print(f"Starting database setup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both database types
    test_database("sqlite")
    test_database("json")
    
    print("Database setup completed successfully!")