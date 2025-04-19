from database.db_config import get_connection
from database.repositories.building_repository import BuildingRepository


def fix_database():
    """Funkcja naprawiająca dane w bazie"""

    # Sprawdźmy istniejące budynki
    all_buildings = BuildingRepository.get_all()

    print(f"Znaleziono {len(all_buildings)} budynków w bazie danych:")
    for b in all_buildings:
        print(f" - ID: {b.building_id}, Nazwa: {b.name}")

    # Sprawdźmy czy wszystkie budynki mają współrzędne
    conn = get_connection()
    cursor = conn.cursor()

    # Sprawdzamy czy Sky Tower ma współrzędne
    cursor.execute("SELECT latitude, longitude FROM Building WHERE building_id = 3")
    sky_tower = cursor.fetchone()
    if sky_tower:
        print(f"Sky Tower ma współrzędne: lat={sky_tower['latitude']}, lng={sky_tower['longitude']}")
        if sky_tower['latitude'] is None or sky_tower['longitude'] is None:
            print("Aktualizacja współrzędnych dla Sky Tower...")
            cursor.execute(
                "UPDATE Building SET latitude = ?, longitude = ? WHERE building_id = ?",
                (51.099731, 17.028114, 3)
            )
            conn.commit()
            print("Współrzędne Sky Tower zaktualizowane")
    else:
        print("Brak wpisu Sky Tower w bazie danych!")

    # Upewnijmy się, że wszystkie budynki mają współrzędne
    building_coords = {
        1: {"lat": 51.106993, "lng": 17.077128},  # Hala Stulecia
        2: {"lat": 51.114854, "lng": 17.046957},  # Katedra
        3: {"lat": 51.099731, "lng": 17.028114}  # Sky Tower
    }

    for building_id, coords in building_coords.items():
        cursor.execute(
            "UPDATE Building SET latitude = ?, longitude = ? WHERE building_id = ?",
            (coords["lat"], coords["lng"], building_id)
        )

    conn.commit()
    print("Wszystkie współrzędne budynków zaktualizowane")

    # Sprawdźmy jeszcze raz wszystkie budynki
    cursor.execute("SELECT building_id, name, latitude, longitude FROM Building")
    buildings = cursor.fetchall()
    print("\nAktualne dane budynków:")
    for b in buildings:
        print(f" - ID: {b['building_id']}, Nazwa: {b['name']}, Współrzędne: ({b['latitude']}, {b['longitude']})")

    conn.close()

    return True


# Wywołaj funkcję naprawiającą bazę danych
if __name__ == "__main__":
    fix_database()