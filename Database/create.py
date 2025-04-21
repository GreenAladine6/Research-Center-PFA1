import sqlite3
import json
import os
from datetime import datetime

def create_database():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'data.db')
    
    # Connect to SQLite database (will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
    /*==============================================================*/
    /* Table : GRADE                                               */
    /*==============================================================*/
    CREATE TABLE GRADE (
       ID_GRADE             INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME_GRA             TEXT
    );

    /*==============================================================*/
    /* Table : LABORATORY                                          */
    /*==============================================================*/
    CREATE TABLE LABORATORY (
       LABO_ID              INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME_LAB             TEXT,
       DIRECTOR             TEXT,
       foreign KEY (DIRECTOR) REFERENCES RESEARCHER(ID_RESEARCHER)
    );

    /*==============================================================*/
    /* Table : PARTNER                                             */
    /*==============================================================*/
    CREATE TABLE PARTNER (
       PARTNER_ID           INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME_PAR             TEXT,
       EMAIL_PAR            TEXT NOT NULL,
       PHONE                INTEGER NOT NULL,
       ADRESS               TEXT NOT NULL,
       CREATION_DATE        DATE NOT NULL,
       WEBSITE              TEXT,
       NOTES                TEXT,
       AMOUNT               REAL,
    );

    /*==============================================================*/
    /* Table : TYPE_EV                                             */
    /*==============================================================*/
    CREATE TABLE TYPE_EV (
       TYPE_EV              TEXT PRIMARY KEY,
       DESCRIPTION          TEXT
    );

    /*==============================================================*/
    /* Table : PROJECT                                             */
    /*==============================================================*/
    CREATE TABLE PROJECT (
       ID_PROJECT           INTEGER PRIMARY KEY AUTOINCREMENT,
       ID_MANGER           INTEGER,
       NAME_PROJECT        TEXT,
       BUDGET               REAL,
       DATE_BEGIN          DATE,
       DATE__END           DATE,
       STATUS               TEXT,
        foreign KEY (ID_MANGER) REFERENCES RESEARCHER(ID_RESEARCHER)
    );

    /*==============================================================*/
    /* Table : RESEARCHER                                          */
    /*==============================================================*/
    CREATE TABLE RESEARCHER (
       ID_RESEARCHER        INTEGER PRIMARY KEY AUTOINCREMENT,
       ID_GRADE             INTEGER NOT NULL,
       FULL_NAME            TEXT NOT NULL,
       NUM_TEL              INTEGER NOT NULL,
       EMAIL_REAS           TEXT,
       FOREIGN KEY (ID_GRADE) REFERENCES GRADE(ID_GRADE)
    );

    /*==============================================================*/
    /* Table : EQUIPEMENT                                          */
    /*==============================================================*/
    CREATE TABLE EQUIPEMENT (
       ID_EQUIPEMENT        INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME_EQ              TEXT,
       PURCHASE_DATE        DATE,
       LABORATOIRE_ID       INTEGER,
       FOREIGN KEY (LABORATOIRE_ID) REFERENCES LABORATORY(LABO_ID)
    );

    /*==============================================================*/
    /* Table : EVENT                                               */
    /*==============================================================*/
    CREATE TABLE EVENT (
       ID_EVEN              INTEGER PRIMARY KEY AUTOINCREMENT,
       TYPE_EV              TEXT NOT NULL,
       DATE_BEG             DATE NOT NULL,
       HEURE               DATETIME NOT NULL,
       LIEU                 TEXT NOT NULL,
       DATEND              DATE,
       ID_ORGANISOR        INTEGER,
       FOREIGN KEY (TYPE_EV) REFERENCES TYPE_EV(TYPE_EV),
       FOREIGN KEY (ID_ORGANISOR) REFERENCES RESEARCHER(ID_RESEARCHER)
    );

    /*==============================================================*/
    /* Table : PUBLICATION                                         */
    /*==============================================================*/
    CREATE TABLE PUBLICATION (
       ID_PUB               INTEGER PRIMARY KEY AUTOINCREMENT,
       ID_RESEARCHER        INTEGER NOT NULL,
       TITLE                TEXT,
       DATE_PUB            TEXT,
       LIEN                 TEXT,
       FOREIGN KEY (ID_RESEARCHER) REFERENCES RESEARCHER(ID_RESEARCHER)
    );

    /*==============================================================*/
    /* Table : ASSIGN                                              */
    /*==============================================================*/
    CREATE TABLE ASSIGN (
       ID_LABO              INTEGER NOT NULL,
       ID_PROJECT           INTEGER NOT NULL,
       PRIMARY KEY (ID_LABO, ID_PROJECT),
       FOREIGN KEY (ID_LABO) REFERENCES LABORATORY(ID_LABO),
       FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT)
    );

    /*==============================================================*/
    /* Table : COLLABORATE                                         */
    /*==============================================================*/
    CREATE TABLE COLLABORATE (
       PARTNER_ID           INTEGER NOT NULL,
       ID_PROJECT           INTEGER NOT NULL,
       PRIMARY KEY (PARTNER_ID, ID_PROJECT),
       FOREIGN KEY (PARTNER_ID) REFERENCES PARTNER(PARTNER_ID),
       FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT)
    );

    /*==============================================================*/
    /* Table : PARTICIPATE                                         */
    /*==============================================================*/
    CREATE TABLE PARTICIPATE (
       ID_EVEN              INTEGER NOT NULL,
       ID_RESEARCHER        INTEGER NOT NULL,
       PRIMARY KEY (ID_EVEN, ID_RESEARCHER),
       FOREIGN KEY (ID_EVEN) REFERENCES EVENT(ID_EVEN),
       FOREIGN KEY (ID_RESEARCHER) REFERENCES RESEARCHER(ID_RESEARCHER)
    );

    /*==============================================================*/
    /* Table : RESERVE                                             */
    /*==============================================================*/
    CREATE TABLE RESERVE (
       ID_PROJECT           INTEGER NOT NULL,
       ID_EQUIPEMENT        INTEGER NOT NULL,
       ID_RESERVATION       INTEGER,
       START_DATE          DATE,
       END_DATE            DATE,
       PRIMARY KEY (ID_PROJECT, ID_EQUIPEMENT),
       FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT),
       FOREIGN KEY (ID_EQUIPEMENT) REFERENCES EQUIPEMENT(ID_EQUIPEMENT)
    );

    /*==============================================================*/
    /* Table : WORK                                                */
    /*==============================================================*/
    CREATE TABLE WORK (
       ID_PROJECT           INTEGER NOT NULL,
       ID_RESEARCHER        INTEGER NOT NULL,
       PRIMARY KEY (ID_PROJECT, ID_RESEARCHER),
       FOREIGN KEY (ID_PROJECT) REFERENCES PROJECT(ID_PROJECT),
       FOREIGN KEY (ID_RESEARCHER) REFERENCES RESEARCHER(ID_RESEARCHER)
    );
    """)

    # Create indexes
    cursor.executescript("""
    CREATE INDEX ASSIGN_FK ON ASSIGN (LABO_ID);
    CREATE INDEX ASSIGN2_FK ON ASSIGN (ID_PROJECT);
    CREATE INDEX COLLABORATE_FK ON COLLABORATE (PARTNER_ID);
    CREATE INDEX COLLABORATE2_FK ON COLLABORATE (ID_PROJECT);
    CREATE INDEX IS_FK ON EVENT (TYPE_EV);
    CREATE INDEX PARTICIPATE_FK ON PARTICIPATE (ID_EVEN);
    CREATE INDEX PARTICIPATE2_FK ON PARTICIPATE (ID_RESEARCHER);
    CREATE INDEX ADD_FK ON PUBLICATION (ID_RESEARCHER);
    CREATE INDEX HAVE_FK ON RESEARCHER (ID_GRADE);
    CREATE INDEX RESERVE_FK ON RESERVE (ID_PROJECT);
    CREATE INDEX RESERVE2_FK ON RESERVE (ID_EQUIPEMENT);
    CREATE INDEX WORK_FK ON WORK (ID_PROJECT);
    CREATE INDEX WORK2_FK ON WORK (ID_RESEARCHER);
    """)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def export_schema_to_json():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'data.db')
    json_path = os.path.join(script_dir, 'data.json')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = {}
    
    for table in tables:
        table_name = table[0]
        if table_name == 'sqlite_sequence':
            continue
            
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        
        # Format columns
        columns_info = []
        for col in columns:
            columns_info.append({
                'name': col[1],
                'type': col[2],
                'not_null': bool(col[3]),
                'default_value': col[4],
                'primary_key': bool(col[5])
            })
        
        # Format foreign keys
        fk_info = []
        for fk in foreign_keys:
            # Find the column name that matches the sequence number
            from_column = None
            for col in columns:
                if col[0] == fk[3]:  # seq is the 4th element (0-based index 3)
                    from_column = col[1]
                    break
            
            if from_column:
                fk_info.append({
                    'from_column': from_column,
                    'to_table': fk[2],  # to table is the 3rd element
                    'to_column': fk[4]   # to column is the 5th element
                })
        
        schema[table_name] = {
            'columns': columns_info,
            'foreign_keys': fk_info
        }
    
    conn.close()
    
    # Save to JSON file
    with open(json_path, 'w') as f:
        json.dump(schema, f, indent=2)

def main():
    print("Creating database...")
    create_database()
    print("Database created successfully.")
    
    print("Exporting schema to JSON...")
    export_schema_to_json()
    print("Schema exported to data.json")

if __name__ == '__main__':
    main()