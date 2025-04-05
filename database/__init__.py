import os
from database.db_config import get_connection, DB_PATH
from database.models.user import User


def initialize_database():
    db_exists = os.path.exists(DB_PATH)

    conn = get_connection()
    cursor = conn.cursor()

    if not db_exists:
        cursor.executescript('''
        -- Tworzenie tabeli User
        CREATE TABLE User (
            user_id INTEGER PRIMARY KEY,
            nickname TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            number_of_achievements INTEGER DEFAULT 0
        );

        -- Tworzenie tabeli Building
        CREATE TABLE Building (
            building_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            image_path TEXT
        );

        -- Tworzenie tabeli łączącej UserBuilding
        CREATE TABLE UserBuilding (
            user_id INTEGER,
            building_id INTEGER,
            visit_date TEXT,
            PRIMARY KEY (user_id, building_id),
            FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
            FOREIGN KEY (building_id) REFERENCES Building(building_id) ON DELETE CASCADE
        );

        -- Indeksy dla poprawy wydajności
        CREATE INDEX idx_userbuilding_user ON UserBuilding(user_id);
        CREATE INDEX idx_userbuilding_building ON UserBuilding(building_id);
        ''')

        conn.commit()
        print("Baza danych zainicjalizowana pomyślnie.")
    else:
        print("Baza danych już istnieje.")

    conn.close()
    return DB_PATH


def seed_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM User")
    if cursor.fetchone()[0] > 0:
        print("Dane już istnieją w bazie.")
        conn.close()
        return

