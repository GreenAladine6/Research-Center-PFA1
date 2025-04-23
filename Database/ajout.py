from sqlite3 import connect
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union

# [Previous class definitions for JSONDatabase and Database remain exactly the same...]
class Database:
    def __init__(self, db_type: str):
        self.db_type = db_type
        if db_type == "sqlite":
            self.conn = connect("data.db")
            self.cursor = self.conn.cursor()
        elif db_type == "json":
            self.data = {
                "GRADE": [],
                "LABORATORY": [],
                "RESEARCHER": [],
                "PROJECT": [],
                "PARTNER": [],
                "EQUIPEMENT": [],
                "TYPE_EV": [],
                "EVENT": [],
                "PUBLICATION": [],}s
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
            db.execute_query("INSERT INTO GRADE (NAME_GRA) VALUES (?)", (grade,))
    else:
        for grade in grades:
            db.insert_query(table="GRADE", record={"NAME_GRA": grade})
    
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
        {"FULL_NAME": "Dr. Sarah Miller", "NUM_TEL": 5551001, "EMAIL_REAS": "s.miller@univ.edu", "ID_GRADE": 6},
        {"FULL_NAME": "Prof. David Kim", "NUM_TEL": 5551002, "EMAIL_REAS": "d.kim@univ.edu", "ID_GRADE": 7},
        {"FULL_NAME": "Dr. Emily Zhang", "NUM_TEL": 5551003, "EMAIL_REAS": "e.zhang@univ.edu", "ID_GRADE": 5},
        {"FULL_NAME": "Dr. Michael Brown", "NUM_TEL": 5551004, "EMAIL_REAS": "m.brown@univ.edu", "ID_GRADE": 8},
        {"FULL_NAME": "Dr. Jessica Lee", "NUM_TEL": 5551005, "EMAIL_REAS": "j.lee@univ.edu", "ID_GRADE": 9},
        {"FULL_NAME": "Dr. Thomas Wilson", "NUM_TEL": 5551006, "EMAIL_REAS": "t.wilson@univ.edu", "ID_GRADE": 10},
        {"FULL_NAME": "Lisa Park", "NUM_TEL": 5551007, "EMAIL_REAS": "l.park@univ.edu", "ID_GRADE": 2},
        {"FULL_NAME": "Daniel Chen", "NUM_TEL": 5551008, "EMAIL_REAS": "d.chen@univ.edu", "ID_GRADE": 3},
        {"FULL_NAME": "Sophia Martinez", "NUM_TEL": 5551009, "EMAIL_REAS": "s.martinez@univ.edu", "ID_GRADE": 4},
        {"FULL_NAME": "Ryan Johnson", "NUM_TEL": 5551010, "EMAIL_REAS": "r.johnson@univ.edu", "ID_GRADE": 1}
    ]
    
    if db.db_type == "sqlite":
        for researcher in researchers:
            db.execute_query(
                "INSERT INTO RESEARCHER (FULL_NAME, NUM_TEL, EMAIL_REAS, ID_GRADE) VALUES (?, ?, ?, ?)",
                (researcher["FULL_NAME"], researcher["NUM_TEL"], researcher["EMAIL_REAS"], researcher["ID_GRADE"])
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
    event_types = [
        {"TYPE_EV": "Conference", "DESCRIPTION": "Academic conference"},
        {"TYPE_EV": "Workshop", "DESCRIPTION": "Training workshop"},
        {"TYPE_EV": "Seminar", "DESCRIPTION": "Department seminar"},
        {"TYPE_EV": "Symposium", "DESCRIPTION": "Research symposium"}
    ]
    
    if db.db_type == "sqlite":
        for et in event_types:
            db.execute_query(
                "INSERT INTO TYPE_EV (TYPE_EV, DESCRIPTION) VALUES (?, ?)",
                (et["TYPE_EV"], et["DESCRIPTION"])
            )
    else:
        for et in event_types:
            db.insert_query(table="TYPE_EV", record=et)
    
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
    for grade in grades:
        print(f"ID: {grade['ID_GRADE'] if db_type == 'sqlite' else grade['id']}, Name: {grade['NAME_GRA']}")
    
    # Display researchers
    researchers = db.select_query("SELECT * FROM RESEARCHER") if db_type == "sqlite" else db.select_query(table="RESEARCHER")
    print(f"\nResearchers ({len(researchers)} entries):")
    for researcher in researchers:
        print(f"ID: {researcher['ID_RESEARCHER'] if db_type == 'sqlite' else researcher['id']}, Name: {researcher['FULL_NAME']}, Grade: {researcher['ID_GRADE']}")
    
    # Display projects
    projects = db.select_query("SELECT * FROM PROJECT") if db_type == "sqlite" else db.select_query(table="PROJECT")
    print(f"\nProjects ({len(projects)} entries):")
    for project in projects:
        print(f"ID: {project['ID_PROJECT'] if db_type == 'sqlite' else project['id']}, Name: {project['NAME_PROJECT']}, Status: {project['STATE']}")
    
    # Display events
    events = db.select_query("SELECT * FROM EVENT") if db_type == "sqlite" else db.select_query(table="EVENT")
    print(f"\nEvents ({len(events)} entries):")
    for event in events:
        print(f"ID: {event['ID_EVEN'] if db_type == 'sqlite' else event['id']}, Type: {event['TYPE_EV']}, Date: {event['DATE_BEG']}")
    
    db.close()
    print(f"\n{db_type.upper()} database test completed")

if __name__ == "__main__":
    print(f"Starting database setup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both database types
    test_database("sqlite")
    test_database("json")
    
    print("\nDatabase setup and population completed successfully!")