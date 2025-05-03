import random
import string
import os
import bcrypt
from datetime import datetime, timedelta
from sqlite3 import OperationalError
from db import Database, JSONDatabase

def populate_large_data(db: Database):
    """Populate the database with a large amount of sample data for all tables, keeping only 100 items per table."""
    print("\nPopulating database with large sample data (max 100 items per table)...")

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

    def random_description(prefix: str = "Overview of") -> str:
        topics = ["research advancements", "scientific discoveries", "technological innovations",
                  "collaborative efforts", "experimental methodologies", "data-driven insights"]
        return f"{prefix} {random.choice(topics)} in {random_string(10)} field."

    def random_bio(name: str) -> str:
        interests = ["machine learning", "genomics", "quantum physics", "climate science",
                     "neuroscience", "robotics", "data science"]
        return f"{name} is a researcher specializing in {random.choice(interests)} with over {random.randint(3, 15)} years of experience."

    def generate_hashed_password(password: str = None) -> str:
        if password is None:
            password = "researcher123"
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    # Modified insert function that enforces the 100-item limit
    def limited_insert(table: str, record: dict) -> int:
        if db.db_type == "sqlite":
            if table == "GRADE":
                db.execute_query("INSERT INTO GRADE (NAME_GRADE) VALUES (?)", (record["NAME_GRADE"],))
            elif table == "TYPE_EV":
                db.execute_query("INSERT INTO TYPE_EV (TYPE_EV, DESCRIPTION) VALUES (?, ?)",
                                (record["TYPE_EV"], record["DESCRIPTION"]))
            elif table == "RESEARCHER":
                db.execute_query(
                    """INSERT INTO RESEARCHER (FULL_NAME, NUM_TEL, EMAIL, ID_GRADE, BIO, PASSWORD)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (record["FULL_NAME"], record["NUM_TEL"], record["EMAIL"],
                     record["ID_GRADE"], record["BIO"], record["PASSWORD"])
                )
            elif table == "LABORATORY":
                db.execute_query(
                    "INSERT INTO LABORATORY (NAME_LAB, DIRECTOR) VALUES (?, ?)",
                    (record["NAME_LAB"], record["DIRECTOR"])
                )
            elif table == "PROJECT":
                db.execute_query(
                    """INSERT INTO PROJECT (NAME_PROJECT, BUDGET, DATE_BEGIN, DATE_END, STATE, ID_MANAGER, DESCRIPTION)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (record["NAME_PROJECT"], record["BUDGET"], record["DATE_BEGIN"],
                     record["DATE_END"], record["STATE"], record["ID_MANAGER"], record["DESCRIPTION"])
                )
            elif table == "PARTNER":
                db.execute_query(
                    """INSERT INTO PARTNER (NAME_PARTNER, EMAIL_PARTNER, PHONE, ADRESS, CREATION_DATE, WEBSITE, NOTES, AMOUNT)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (record["NAME_PARTNER"], record["EMAIL_PARTNER"], record["PHONE"], record["ADRESS"],
                     record["CREATION_DATE"], record["WEBSITE"], record["NOTES"], record["AMOUNT"])
                )
            elif table == "EQUIPEMENT":
                db.execute_query(
                    "INSERT INTO EQUIPEMENT (NAME_EQUIPEMENT, PURCHASE_DATE, LABORATOIRE_ID) VALUES (?, ?, ?)",
                    (record["NAME_EQUIPEMENT"], record["PURCHASE_DATE"], record["LABORATOIRE_ID"])
                )
            elif table == "EVENT":
                db.execute_query(
                    """INSERT INTO EVENT (NAME_EVENT, TYPE_EV, DATE_BEG, HOUR, PLACE, DATEND, ID_ORGANISOR, DESCRIPTION)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (record["NAME_EVENT"], record["TYPE_EV"], record["DATE_BEGIN"], record["HOUR"],
                     record["PLACE"], record["DATE_END"], record["ID_ORGANISOR"], record["DESCRIPTION"])
                )
            elif table == "PUBLICATION":
                db.execute_query(
                    """INSERT INTO PUBLICATION (TITLE, DATE, LINK, ID_RESEARCHER, DESCRIPTION)
                    VALUES (?, ?, ?, ?, ?)""",
                    (record["TITLE"], record["DATE"], record["LINK"],
                     record["ID_RESEARCHER"], record["DESCRIPTION"])
                )
            elif table == "ASSIGN":
                db.execute_query(
                    "INSERT OR IGNORE INTO ASSIGN (LABO_ID, ID_PROJECT) VALUES (?, ?)",
                    (record["LABO_ID"], record["ID_PROJECT"])
                )
            elif table == "COLLABORATE":
                db.execute_query(
                    "INSERT OR IGNORE INTO COLLABORATE (ID_PARTNER, ID_PROJECT) VALUES (?, ?)",
                    (record["ID_PARTNER"], record["ID_PROJECT"])
                )
            elif table == "PARTICIPATE":
                db.execute_query(
                    "INSERT OR IGNORE INTO PARTICIPATE (ID_EVENT, ID_RESEARCHER) VALUES (?, ?)",
                    (record["ID_EVENT"], record["ID_RESEARCHER"])
                )
            elif table == "RESERVE":
                db.execute_query(
                    """INSERT OR IGNORE INTO RESERVE (ID_PROJECT, ID_EQUIPEMENT, ID_RESERVATION, START_DATE, END_DATE)
                    VALUES (?, ?, ?, ?, ?)""",
                    (record["ID_PROJECT"], record["ID_EQUIPEMENT"], record["ID_RESERVATION"],
                     record["START_DATE"], record["END_DATE"])
                )
            elif table == "WORK":
                db.execute_query(
                    "INSERT OR IGNORE INTO WORK (ID_PROJECT, ID_RESEARCHER) VALUES (?, ?)",
                    (record["ID_PROJECT"], record["ID_RESEARCHER"])
                )
            db.cursor.execute("SELECT last_insert_rowid()")
            return db.cursor.fetchone()[0]
        else:
            current_items = db.conn.select_query(table)
            if len(current_items) >= 100:
                excess = len(current_items) - 99
                db.conn.data[table] = db.conn.data[table][excess:]
            return db.conn.insert_query(table, record)

    # 1. Add Grades (20 grades) - Limited to 100
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
    for grade in grades[:100]:
        if db.db_type == "sqlite":
            db.execute_query("INSERT INTO GRADE (NAME_GRADE) VALUES (?)", (grade,))
            db.cursor.execute("SELECT last_insert_rowid()")
            grade_ids.append(db.cursor.fetchone()[0])
        else:
            grade_id = limited_insert("GRADE", {"NAME_GRADE": grade})
            if grade_id:
                grade_ids.append(grade_id)

    # 2. Add Event Types (50 types) - Limited to 100
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
    for event_type in event_types[:100]:
        if db.db_type == "sqlite":
            db.execute_query("INSERT INTO TYPE_EV (TYPE_EV, DESCRIPTION) VALUES (?, ?)",
                            (event_type, f"Description for {event_type}"))
        else:
            limited_insert("TYPE_EV", {"TYPE_EV": event_type, "DESCRIPTION": f"Description for {event_type}"})

    # 3. Add Researchers (100 researchers)
    researcher_ids = []
    first_names = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Michael", "Isabella"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Wilson", "Davis", "Clark", "Harris", "Lewis", "Walker"]
    for i in range(100):
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        researcher = {
            "FULL_NAME": full_name,
            "NUM_TEL": random_phone(),
            "EMAIL": random_email(full_name),
            "ID_GRADE": random.choice(grade_ids),
            "BIO": random_bio(full_name),
            "PASSWORD": generate_hashed_password()
        }
        researcher_id = limited_insert("RESEARCHER", researcher)
        if researcher_id:
            researcher_ids.append(researcher_id)

    # 4. Add Laboratories (50 labs) - Limited to 100
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
        lab_id = limited_insert("LABORATORY", lab)
        if lab_id:
            lab_ids.append(lab_id)

    # 5. Add Projects (100 projects)
    project_names = [
        "Genome Sequencing", "Quantum Algorithm", "Climate Impact", "Neural Network",
        "AI for Healthcare", "Sustainable Energy", "Nanotech Development", "Bioinformatics Pipeline",
        "Robotics Automation", "Data Privacy", "Cancer Research", "Materials Discovery"
    ]
    project_ids = []
    for i in range(100):
        start_date = random_date(2020, 2024)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(180, 1095))).strftime("%Y-%m-%d")
        project = {
            "NAME_PROJECT": f"{project_names[i % len(project_names)]} Project {i + 1}",
            "BUDGET": round(random.uniform(100000, 5000000), 2),
            "DATE_BEGIN": start_date,
            "DATE_END": end_date,
            "STATE": random.choice(["Not Started", "In Progress", "Completed", "Canceled"]),
            "ID_MANAGER": random.choice(researcher_ids),
            "DESCRIPTION": random_description("Project overview for")
        }
        project_id = limited_insert("PROJECT", project)
        if project_id:
            project_ids.append(project_id)

    # 6. Add Partners (100 partners)
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
        partner_id = limited_insert("PARTNER", partner)
        if partner_id:
            partner_ids.append(partner_id)

    # 7. Add Equipment (100 pieces)
    equipment_names = [
        "Microscope", "Spectrometer", "Centrifuge", "PCR Machine", "HPLC System",
        "Mass Spectrometer", "Quantum Computer", "3D Printer", "Laser Cutter",
        "EEG Machine", "MRI Scanner", "Flow Cytometer"
    ]
    equipment_ids = []
    for i in range(100):
        equipment = {
            "NAME_EQUIPEMENT": f"{equipment_names[i % len(equipment_names)]} {i + 1}",
            "PURCHASE_DATE": random_date(2015, 2024),
            "LABORATOIRE_ID": random.choice(lab_ids)
        }
        equipment_id = limited_insert("EQUIPEMENT", equipment)
        if equipment_id:
            equipment_ids.append(equipment_id)

    # 8. Add Events (100 events)
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
    for i in range(100):
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
            "DESCRIPTION": random_description("Event overview for")
        }
        event_id = limited_insert("EVENT", event)
        if event_id:
            event_ids.append(event_id)

    # 9. Add Publications (100 publications)
    publication_titles = [
        "Advances in", "Breakthroughs in", "New Insights into", "Exploring",
        "Innovations in", "Future of", "Applications of", "Challenges in"
    ]
    publication_ids = []
    for i in range(100):
        publication = {
            "TITLE": f"{publication_titles[i % len(publication_titles)]} {random.choice(project_names)} {i + 1}",
            "DATE": random_date(2020, 2025),
            "LINK": f"https://journal.org/publication/{i + 1}",
            "ID_RESEARCHER": random.choice(researcher_ids),
            "DESCRIPTION": random_description("Publication summary for")
        }
        publication_id = limited_insert("PUBLICATION", publication)
        if publication_id:
            publication_ids.append(publication_id)

    # 10. Add Junction Tables - Limited to 100 records each
    # ASSIGN: Laboratories assigned to Projects
    for i in range(100):
        assign = {
            "LABO_ID": random.choice(lab_ids),
            "ID_PROJECT": random.choice(project_ids)
        }
        limited_insert("ASSIGN", assign)

    # COLLABORATE: Projects collaborating with Partners
    for i in range(100):
        collaborate = {
            "ID_PARTNER": random.choice(partner_ids),
            "ID_PROJECT": random.choice(project_ids)
        }
        limited_insert("COLLABORATE", collaborate)

    # PARTICIPATE: Researchers participating in Events
    for i in range(100):
        participate = {
            "ID_EVENT": random.choice(event_ids),
            "ID_RESEARCHER": random.choice(researcher_ids)
        }
        limited_insert("PARTICIPATE", participate)

    # RESERVE: Equipment reserved for Projects
    for i in range(100):
        start_date = random_date(2023, 2025)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d")
        reserve = {
            "ID_PROJECT": random.choice(project_ids),
            "ID_EQUIPEMENT": random.choice(equipment_ids),
            "ID_RESERVATION": i + 1,
            "START_DATE": start_date,
            "END_DATE": end_date
        }
        limited_insert("RESERVE", reserve)

    # WORK: Researchers working on Projects
    for i in range(100):
        work = {
            "ID_PROJECT": random.choice(project_ids),
            "ID_RESEARCHER": random.choice(researcher_ids)
        }
        limited_insert("WORK", work)

    # For SQLite: After all inserts, enforce limits by deleting excess records
    if db.db_type == "sqlite":
        tables_to_limit = ["RESEARCHER", "LABORATORY", "PROJECT", "PARTNER",
                          "EQUIPEMENT", "EVENT", "PUBLICATION", "ASSIGN",
                          "COLLABORATE", "PARTICIPATE", "RESERVE", "WORK",
                          "GRADE", "TYPE_EV"]
        for table in tables_to_limit:
            db.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = db.cursor.fetchone()[0]
            if count > 100:
                db.cursor.execute(f"DELETE FROM {table} WHERE id NOT IN "
                                 f"(SELECT id FROM {table} ORDER BY id DESC LIMIT 100)")
                db.conn.commit()
                print(f"Trimmed {table} from {count} to 100 records")

    print("Large sample data populated successfully (max 100 items per table)!")

def main():
    print(f"Starting database population at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    db_dir = "./Database"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")

    db_type = "json"
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