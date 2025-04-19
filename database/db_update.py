from database.db_config import get_connection


def update_database_schema():
    """
    Aktualizuje schemat bazy danych, dodając nowe kolumny do tabeli Building:
    - latitude: szerokość geograficzna zabytku
    - longitude: długość geograficzna zabytku
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Sprawdzamy czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(Building)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        # Dodajemy kolumny dla współrzędnych, jeśli nie istnieją
        columns_added = False
        if 'latitude' not in column_names:
            cursor.execute("ALTER TABLE Building ADD COLUMN latitude REAL")
            print("Dodano kolumnę latitude do tabeli Building")
            columns_added = True

        if 'longitude' not in column_names:
            cursor.execute("ALTER TABLE Building ADD COLUMN longitude REAL")
            print("Dodano kolumnę longitude do tabeli Building")
            columns_added = True

        # Dodajemy początkowe dane dla istniejących zabytków
        building_coords = {
            1: {"lat": 51.106993, "lng": 17.077128},  # Hala Stulecia
            2: {"lat": 51.114854, "lng": 17.046957},  # Katedra
            3: {"lat": 51.099731, "lng": 17.028114}   # Sky Tower
        }

        # Upewniamy się, że wszystkie zabytki mają współrzędne
        updates = 0
        for building_id, coords in building_coords.items():
            cursor.execute(
                "UPDATE Building SET latitude = ?, longitude = ? WHERE building_id = ?",
                (coords["lat"], coords["lng"], building_id)
            )
            updates += 1
            print(f"Zaktualizowano współrzędne dla zabytku ID {building_id}")

        if updates > 0 or columns_added:
            conn.commit()
            print(f"Zaktualizowano współrzędne dla {updates} zabytków")

        # Sprawdźmy, czy wszystkie zabytki mają poprawne współrzędne
        cursor.execute("SELECT building_id, name, latitude, longitude FROM Building")
        buildings = cursor.fetchall()
        print("\nObecne dane zabytków w bazie:")
        for building in buildings:
            print(f" - ID: {building['building_id']}, Nazwa: {building['name']}, " +
                  f"Współrzędne: ({building['latitude']}, {building['longitude']})")

        print("Aktualizacja schematu bazy danych zakończona pomyślnie.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Błąd podczas aktualizacji schematu bazy danych: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    update_database_schema()