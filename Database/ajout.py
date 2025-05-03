import random
import string
import os
import bcrypt
from datetime import datetime, timedelta
from sqlite3 import OperationalError
from db import Database, JSONDatabase  # Adjust import based on your project structure

def populate_large_data(db: Database):
    """Populate the database with a large amount of sample data for all tables."""
    print("\nPopulating database with large sample data...")

    # Helper functions
    def random_string(length: int) -> str:
        return ''.join(random.choices(string.ascii_letters, k=length))

    def random_email(name: str) -> str:
        domains = ["univ.edu", "research.org", "science.net", "academy.edu"]
        return f"{name.lower().replace(' ', '.')}{random.randint(1, 999)}@{random.choice(domains)}"

    def random_date(start_year: int = 2020, end_year: int = 2026) -> str:
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

    def random_time() -> str:
        hours = random.randint(8, 18)
        minutes = random.choice([0, 15, 30, 45])
        return f"{hours:02d}:{minutes:02d}"

    def random_phone() -> int:
        return random.randint(1000000000, 9999999999)

    # New helper function for descriptions
    def random_description(prefix: str = "Overview of") -> str:
        topics = ["research advancements", "scientific discoveries", "technological innovations",
                  "collaborative efforts", "experimental methodologies", "data-driven insights"]
        return f"{prefix} {random.choice(topics)} in {random_string(10)} field."

    # New helper function for biography
    def random_bio(name: str) -> str:
        interests = ["machine learning", "genomics", "quantum physics", "climate science",
                     "neuroscience", "robotics", "data science"]
        return f"{name} is a researcher specializing in {random.choice(interests)} with over {random.randint(3, 15)} years of experience."

    # New helper function for password with hashing
    def generate_hashed_password(password: str = None) -> str:
        """Generate a hashed password using bcrypt with test defaults."""
        # Default to test password if not provided
        if password is None:
            password = "researcher123"
        
        # Generate secure hash
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    # 1. Add Grades (20 grades) - Unchanged
    grades = [
        "Undergraduate Researcher", "Graduate Researcher", "PhD Candidate",
        "Postdoctoral Researcher", "Assistant Professor", "Associate Professor",
        "Full Professor", "Research Scientist", "Senior Research Scientist",
        "Principal Investigator", "Lab Technician", "Research Assistant",
        "Visiting Scholar", "Adjunct Professor", "Research Fellow",
        "Senior Research Fellow", "Lab Manager", "Data Scientist",
        "Bioinformatician", "Project Coordinator"
    ]
    grade_ids = []
    for grade in grades:
        if db.db_type == "sqlite":
            db.execute_query("INSERT INTO GRADE (NAME_GRADE) VALUES (?)", (grade,))
            db.cursor.execute("SELECT last_insert_rowid()")
            grade_ids.append(db.cursor.fetchone()[0])
        else:
            grade_id = db.insert_query(table="GRADE", record={"NAME_GRADE": grade})
            grade_ids.append(grade_id)

    # 2. Add Event Types (50 types) - Unchanged
    event_types = [
        "Conference", "Workshop", "Seminar", "Symposium", "Webinar",
        "Lecture Series", "Panel Discussion", "Hackathon", "Networking Event",
        "Poster Session", "Roundtable", "Training Session", "Guest Lecture",
        "Research Forum", "Industry Meetup", "Career Fair", "Science Fair",
        "Data Science Bootcamp", "AI Summit", "Biotech Expo", "Quantum Computing Workshop",
        "Environmental Summit", "Neuroscience Colloquium", "Robotics Demo",
        "Innovation Showcase", "Startup Pitch", "Tech Talk", "Policy Forum",
        "Ethics in Science Seminar", "Open House", "Lab Tour", "Research Showcase",
        "Collaborative Workshop", "Funding Pitch", "Grant Writing Seminar",
        "Peer Review Session", "Journal Club", "Tech Transfer Workshop",
        "Citizen Science Event", "Public Lecture", "STEM Outreach",
        "Diversity in Science Panel", "Climate Action Forum", "Bioethics Roundtable",
        "AI Ethics Seminar", "Quantum Tech Summit", "Genomics Workshop",
        "Neurotech Demo", "Sustainable Tech Forum", "Research Retreat"
    ]
    for event_type in event_types:
        if db.db_type == "sqlite":
            db.execute_query("INSERT INTO TYPE_EV (TYPE_EV, DESCRIPTION) VALUES (?, ?)",
                            (event_type, f"Description for {event_type}"))
        else:
            db.insert_query(table="TYPE_EV", record={"TYPE_EV": event_type, "DESCRIPTION": f"Description for {event_type}"})

    # 3. Add Researchers (500 researchers) - Modified to include hashed password
    researcher_ids = []
    first_names = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Michael", "Isabella"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Wilson", "Davis", "Clark", "Harris", "Lewis", "Walker"]
    for i in range(500):
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        researcher = {
            "FULL_NAME": full_name,
            "NUM_TEL": random_phone(),
            "EMAIL": random_email(full_name),
            "ID_GRADE": random.choice(grade_ids),
            "BIO": random_bio(full_name),
            "PASSWORD": generate_hashed_password()  # Now using hashed password
        }
        if db.db_type == "sqlite":
            db.execute_query(
                """INSERT INTO RESEARCHER (FULL_NAME, NUM_TEL, EMAIL, ID_GRADE, BIO, PASSWORD)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (researcher["FULL_NAME"], researcher["NUM_TEL"], researcher["EMAIL"],
                 researcher["ID_GRADE"], researcher["BIO"], researcher["PASSWORD"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            researcher_ids.append(db.cursor.fetchone()[0])
        else:
            researcher_id = db.insert_query(table="RESEARCHER", record=researcher)
            researcher_ids.append(researcher_id)

    # 4. Add Laboratories (50 labs) - Unchanged
    lab_names = [
        "Bioinformatics", "Neuroscience", "Quantum Computing", "Environmental Science",
        "Robotics", "Genomics", "AI Research", "Materials Science", "Biophysics",
        "Data Science", "Climate Research", "Nanotechnology", "Biomedical Engineering",
        "Astrophysics", "Chemical Engineering", "Cybersecurity", "Synthetic Biology",
        "Energy Systems", "Photonics", "Computational Biology"
    ]
    lab_ids = []
    for i in range(50):
        lab = {
            "NAME_LAB": f"{lab_names[i % len(lab_names)]} Lab {i + 1}",
            "DIRECTOR": random.choice(researcher_ids)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                "INSERT INTO LABORATORY (NAME_LAB, DIRECTOR) VALUES (?, ?)",
                (lab["NAME_LAB"], lab["DIRECTOR"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            lab_ids.append(db.cursor.fetchone()[0])
        else:
            lab_id = db.insert_query(table="LABORATORY", record=lab)
            lab_ids.append(lab_id)

    # 5. Add Projects (200 projects) - Modified to include DESCRIPTION
    project_names = [
        "Genome Sequencing", "Quantum Algorithm", "Climate Impact", "Neural Network",
        "AI for Healthcare", "Sustainable Energy", "Nanotech Development", "Bioinformatics Pipeline",
        "Robotics Automation", "Data Privacy", "Cancer Research", "Materials Discovery"
    ]
    project_ids = []
    for i in range(200):
        start_date = random_date(2020, 2024)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(180, 1095))).strftime("%Y-%m-%d")
        project = {
            "NAME_PROJECT": f"{project_names[i % len(project_names)]} Project {i + 1}",
            "BUDGET": round(random.uniform(100000, 5000000), 2),
            "DATE_BEGIN": start_date,
            "DATE_END": end_date,
            "STATE": random.choice(["Not Started", "In Progress", "Completed", "Canceled"]),
            "ID_MANAGER": random.choice(researcher_ids),
            "DESCRIPTION": random_description("Project overview for")  # New DESCRIPTION field
        }
        if db.db_type == "sqlite":
            db.execute_query(
                """INSERT INTO PROJECT (NAME_PROJECT, BUDGET, DATE_BEGIN, DATE_END, STATE, ID_MANAGER, DESCRIPTION)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (project["NAME_PROJECT"], project["BUDGET"], project["DATE_BEGIN"],
                 project["DATE_END"], project["STATE"], project["ID_MANAGER"], project["DESCRIPTION"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            project_ids.append(db.cursor.fetchone()[0])
        else:
            project_id = db.insert_query(table="PROJECT", record=project)
            project_ids.append(project_id)

    # 6. Add Partners (100 partners) - Unchanged
    partner_types = ["Industry", "Academic", "Government", "Non-Profit"]
    partner_ids = []
    for i in range(100):
        partner_name = f"{random_string(5)} {random_string(7)} Organization"
        partner = {
            "NAME_PARTNER": partner_name,
            "EMAIL_PARTNER": random_email(partner_name),
            "PHONE": random_phone(),
            "ADRESS": f"{random.randint(100, 999)} {random_string(8)} St, City {i + 1}",
            "CREATION_DATE": random_date(2000, 2020),
            "WEBSITE": f"https://www.{partner_name.lower().replace(' ', '')}.org",
            "NOTES": f"Notes for partner {i + 1}",
            "AMOUNT": round(random.uniform(50000, 1000000), 2)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                """INSERT INTO PARTNER (NAME_PARTNER, EMAIL_PARTNER, PHONE, ADRESS, CREATION_DATE, WEBSITE, NOTES, AMOUNT)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (partner["NAME_PARTNER"], partner["EMAIL_PARTNER"], partner["PHONE"], partner["ADRESS"],
                 partner["CREATION_DATE"], partner["WEBSITE"], partner["NOTES"], partner["AMOUNT"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            partner_ids.append(db.cursor.fetchone()[0])
        else:
            partner_id = db.insert_query(table="PARTNER", record=partner)
            partner_ids.append(partner_id)

    # 7. Add Equipment (300 pieces) - Unchanged
    equipment_names = [
        "Microscope", "Spectrometer", "Centrifuge", "PCR Machine", "HPLC System",
        "Mass Spectrometer", "Quantum Computer", "3D Printer", "Laser Cutter",
        "EEG Machine", "MRI Scanner", "Flow Cytometer"
    ]
    equipment_ids = []
    for i in range(300):
        equipment = {
            "NAME_EQUIPEMENT": f"{equipment_names[i % len(equipment_names)]} {i + 1}",
            "PURCHASE_DATE": random_date(2015, 2024),
            "LABORATOIRE_ID": random.choice(lab_ids)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                "INSERT INTO EQUIPEMENT (NAME_EQUIPEMENT, PURCHASE_DATE, LABORATOIRE_ID) VALUES (?, ?, ?)",
                (equipment["NAME_EQUIPEMENT"], equipment["PURCHASE_DATE"], equipment["LABORATOIRE_ID"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            equipment_ids.append(db.cursor.fetchone()[0])
        else:
            equipment_id = db.insert_query(table="EQUIPEMENT", record=equipment)
            equipment_ids.append(equipment_id)

    # 8. Add Events (300 events) - Modified to include DESCRIPTION
    event_names = [
        "Research Conference", "Machine Learning Workshop", "AI Seminar", "Research Symposium",
        "Quantum Computing Forum", "Bioinformatics Summit", "Climate Science Webinar",
        "Robotics Showcase", "Data Science Bootcamp", "Neuroscience Colloquium"
    ]
    places = [
        "Convention Center", "Science Building", "Main Auditorium", "University Hall",
        "Tech Park", "Innovation Hub", "Research Complex", "Lecture Hall"
    ]
    event_ids = []
    for i in range(300):
        start_date = random_date(2023, 2026)
        duration = random.randint(1, 5)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=duration)).strftime("%Y-%m-%d")
        event = {
            "NAME_EVENT": f"{event_names[i % len(event_names)]} {i + 1}",
            "TYPE_EV": random.choice(event_types),
            "DATE_BEGIN": start_date,
            "HOUR": random_time(),
            "PLACE": f"{places[i % len(places)]}, Room {random.randint(1, 10)}",
            "DATE_END": end_date,
            "ID_ORGANISOR": random.choice(researcher_ids),
            "DESCRIPTION": random_description("Event overview for")  # New DESCRIPTION field
        }
        if db.db_type == "sqlite":
            db.execute_query(
                """INSERT INTO EVENT (NAME_EVENT, TYPE_EV, DATE_BEG, HOUR, PLACE, DATEND, ID_ORGANISOR, DESCRIPTION)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (event["NAME_EVENT"], event["TYPE_EV"], event["DATE_BEGIN"], event["HOUR"],
                 event["PLACE"], event["DATE_END"], event["ID_ORGANISOR"], event["DESCRIPTION"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            event_ids.append(db.cursor.fetchone()[0])
        else:
            event_id = db.insert_query(table="EVENT", record=event)
            event_ids.append(event_id)

    # 9. Add Publications (500 publications) - Modified to include DESCRIPTION
    publication_titles = [
        "Advances in", "Breakthroughs in", "New Insights into", "Exploring",
        "Innovations in", "Future of", "Applications of", "Challenges in"
    ]
    publication_ids = []
    for i in range(500):
        publication = {
            "TITLE": f"{publication_titles[i % len(publication_titles)]} {random.choice(project_names)} {i + 1}",
            "DATE_PUB": random_date(2020, 2025),
            "LIEN": f"https://journal.org/publication/{i + 1}",
            "ID_RESEARCHER": random.choice(researcher_ids),
            "DESCRIPTION": random_description("Publication summary for")  # New DESCRIPTION field
        }
        if db.db_type == "sqlite":
            db.execute_query(
                """INSERT INTO PUBLICATION (TITLE, DATE_PUB, LIEN, ID_RESEARCHER, DESCRIPTION)
                VALUES (?, ?, ?, ?, ?)""",
                (publication["TITLE"], publication["DATE_PUB"], publication["LIEN"],
                 publication["ID_RESEARCHER"], publication["DESCRIPTION"])
            )
            db.cursor.execute("SELECT last_insert_rowid()")
            publication_ids.append(db.cursor.fetchone()[0])
        else:
            publication_id = db.insert_query(table="PUBLICATION", record=publication)
            publication_ids.append(publication_id)

    # 10. Add Junction Tables - Unchanged
    # ASSIGN: Laboratories assigned to Projects (700 records)
    for i in range(700):
        assign = {
            "LABO_ID": random.choice(lab_ids),
            "ID_PROJECT": random.choice(project_ids)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                "INSERT OR IGNORE INTO ASSIGN (LABO_ID, ID_PROJECT) VALUES (?, ?)",
                (assign["LABO_ID"], assign["ID_PROJECT"])
            )
        else:
            existing = db.select_query(table="ASSIGN", conditions=assign)
            if not existing:
                db.insert_query(table="ASSIGN", record=assign)

    # COLLABORATE: Projects collaborating with Partners (600 records)
    for i in range(600):
        collaborate = {
            "ID_PARTNER": random.choice(partner_ids),
            "ID_PROJECT": random.choice(project_ids)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                "INSERT OR IGNORE INTO COLLABORATE (ID_PARTNER, ID_PROJECT) VALUES (?, ?)",
                (collaborate["ID_PARTNER"], collaborate["ID_PROJECT"])
            )
        else:
            existing = db.select_query(table="COLLABORATE", conditions=collaborate)
            if not existing:
                db.insert_query(table="COLLABORATE", record=collaborate)

    # PARTICIPATE: Researchers participating in Events (1200 records)
    for i in range(1200):
        participate = {
            "ID_EVENT": random.choice(event_ids),
            "ID_RESEARCHER": random.choice(researcher_ids)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                "INSERT OR IGNORE INTO PARTICIPATE (ID_EVENT, ID_RESEARCHER) VALUES (?, ?)",
                (participate["ID_EVENT"], participate["ID_RESEARCHER"])
            )
        else:
            existing = db.select_query(table="PARTICIPATE", conditions=participate)
            if not existing:
                db.insert_query(table="PARTICIPATE", record=participate)

    # RESERVE: Equipment reserved for Projects (800 records)
    for i in range(800):
        start_date = random_date(2023, 2025)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d")
        reserve = {
            "ID_PROJECT": random.choice(project_ids),
            "ID_EQUIPEMENT": random.choice(equipment_ids),
            "ID_RESERVATION": i + 1,
            "START_DATE": start_date,
            "END_DATE": end_date
        }
        if db.db_type == "sqlite":
            db.execute_query(
                """INSERT OR IGNORE INTO RESERVE (ID_PROJECT, ID_EQUIPEMENT, ID_RESERVATION, START_DATE, END_DATE)
                VALUES (?, ?, ?, ?, ?)""",
                (reserve["ID_PROJECT"], reserve["ID_EQUIPEMENT"], reserve["ID_RESERVATION"],
                 reserve["START_DATE"], reserve["END_DATE"])
            )
        else:
            existing = db.select_query(table="RESERVE", conditions={
                "ID_PROJECT": reserve["ID_PROJECT"],
                "ID_EQUIPEMENT": reserve["ID_EQUIPEMENT"]
            })
            if not existing:
                db.insert_query(table="RESERVE", record=reserve)

    # WORK: Researchers working on Projects (1000 records)
    for i in range(1000):
        work = {
            "ID_PROJECT": random.choice(project_ids),
            "ID_RESEARCHER": random.choice(researcher_ids)
        }
        if db.db_type == "sqlite":
            db.execute_query(
                "INSERT OR IGNORE INTO WORK (ID_PROJECT, ID_RESEARCHER) VALUES (?, ?)",
                (work["ID_PROJECT"], work["ID_RESEARCHER"])
            )
        else:
            existing = db.select_query(table="WORK", conditions=work)
            if not existing:
                db.insert_query(table="WORK", record=work)

    print("Large sample data populated successfully!")

def main():
    print(f"Starting database population at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    db_dir = "./Database"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")

    db_type = "json"  # Only JSON
    print(f"\nPopulating {db_type.upper()} database...")
    try:
        db = Database(db_type=db_type, db_path="./Database/data.db", json_path="./Database/data.json")
        print(f"Creating tables for {db_type.upper()} database...")
        db.create_tables()
        populate_large_data(db)
        db.close()
        print(f"{db_type.upper()} database population completed")
    except Exception as e:
        print(f"Error populating {db_type.upper()} database: {e}")
        raise

    print("\nDatabase population completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Database population failed: {e}")