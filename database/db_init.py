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
            user_photo_path TEXT,
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
        # Sprawdźmy czy kolumna user_photo_path istnieje
        cursor.execute("PRAGMA table_info(UserBuilding)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'user_photo_path' not in column_names:
            print("Dodawanie kolumny user_photo_path do tabeli UserBuilding...")
            cursor.execute("ALTER TABLE UserBuilding ADD COLUMN user_photo_path TEXT")
            conn.commit()
            print("Kolumna user_photo_path dodana pomyślnie.")
        else:
            print("Kolumna user_photo_path już istnieje.")

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

    # Przykładowi użytkownicy z haszami haseł
    users = [
        (1, "turysta123", User.hash_password("haslo123"), 5),
        (2, "zabytkowy_fan", User.hash_password("fan1234"), 12),
        (3, "podroznik", User.hash_password("podroznik2023"), 8)
    ]
    cursor.executemany("INSERT INTO User VALUES (?, ?, ?, ?)", users)

    # Przykładowe zabytki
    buildings = [
        (1, "Hala Stulecia", "Zabytkowa hala widowiskowo-sportowa we Wrocławiu.", "assets/Hala.jpeg"),
        (2, "Katedra św. Jana Chrzciciela", "Gotycka katedra we Wrocławiu.", "assets/Katedra.jpg"),
        (3, "Sky Tower", "Najwyższy budynek mieszkalno-biurowy w Polsce, znajdujący się we Wrocławiu.", "assets/SkyTower.jpg")
    ]
    cursor.executemany("INSERT INTO Building VALUES (?, ?, ?, ?)", buildings)

    # Przykładowe wizyty
    visits = [
        (1, 1, "2023-06-15", None),
        (1, 2, "2023-07-22", None),
        (2, 1, "2023-05-10", None),
        (2, 3, "2023-08-05", None),
        (3, 2, "2023-09-12", None)
    ]
    cursor.executemany("INSERT INTO UserBuilding VALUES (?, ?, ?, ?)", visits)

    conn.commit()
    conn.close()
    print("Przykładowe dane dodane do bazy.")