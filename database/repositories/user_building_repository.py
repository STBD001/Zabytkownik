from database.db_config import get_connection
from database.models.user_building import UserBuilding
from datetime import datetime
import shutil
import os


class UserBuildingRepository:
    @staticmethod
    def get_user_buildings(user_id):
        """Pobiera wszystkie budynki odwiedzone przez użytkownika"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ub.*, b.name, b.description, b.image_path 
            FROM UserBuilding ub 
            JOIN Building b ON ub.building_id = b.building_id 
            WHERE ub.user_id = ?
        """, (user_id,))

        results = cursor.fetchall()
        print(f"Zapytanie zwróciło {len(results)} wyników dla użytkownika {user_id}")

        if results and len(results) > 0:
            print(f"Dostępne kolumny: {', '.join(results[0].keys())}")
            for i, result in enumerate(results[:3]):
                print(f"Wynik {i + 1}:")
                for key in result.keys():
                    print(f"  {key}: {result[key]}")

        conn.close()
        return results

    @staticmethod
    def check_visit(user_id, building_id):
        """Sprawdza, czy użytkownik odwiedził już dany budynek"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM UserBuilding WHERE user_id = ? AND building_id = ?",
            (user_id, building_id)
        )
        visit = cursor.fetchone()
        conn.close()

        return UserBuilding.from_db_row(visit) if visit else None

    @staticmethod
    def add_visit(user_id, building_id, visit_date=None, user_photo_path=None):
        """Dodaje wizytę użytkownika w budynku"""
        if visit_date is None:
            visit_date = datetime.now().strftime('%Y-%m-%d')

        existing_visit = UserBuildingRepository.check_visit(user_id, building_id)

        if existing_visit:
            if user_photo_path and existing_visit.user_photo_path != user_photo_path:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE UserBuilding SET user_photo_path = ? WHERE user_id = ? AND building_id = ?",
                    (user_photo_path, user_id, building_id)
                )
                conn.commit()
                conn.close()
                existing_visit.user_photo_path = user_photo_path
            return existing_visit

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO UserBuilding (user_id, building_id, visit_date, user_photo_path) VALUES (?, ?, ?, ?)",
            (user_id, building_id, visit_date, user_photo_path)
        )
        conn.commit()

        new_visit = UserBuilding(user_id, building_id, visit_date, user_photo_path)

        cursor.execute("SELECT COUNT(*) FROM UserBuilding WHERE user_id = ?", (user_id,))
        achievements_count = cursor.fetchone()[0]

        cursor.execute(
            "UPDATE User SET number_of_achievements = ? WHERE user_id = ?",
            (achievements_count, user_id)
        )
        conn.commit()
        conn.close()

        return new_visit

    @staticmethod
    def remove_visit(user_id, building_id):
        """Usuwa wizytę użytkownika w budynku"""
        visit = UserBuildingRepository.check_visit(user_id, building_id)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM UserBuilding WHERE user_id = ? AND building_id = ?",
            (user_id, building_id)
        )
        result = cursor.rowcount > 0

        if result:
            if visit and visit.user_photo_path and os.path.exists(visit.user_photo_path):
                try:
                    os.remove(visit.user_photo_path)
                except Exception as e:
                    print(f"Błąd podczas usuwania zdjęcia: {e}")

            cursor.execute("SELECT COUNT(*) FROM UserBuilding WHERE user_id = ?", (user_id,))
            achievements_count = cursor.fetchone()[0]

            cursor.execute(
                "UPDATE User SET number_of_achievements = ? WHERE user_id = ?",
                (achievements_count, user_id)
            )

        conn.commit()
        conn.close()
        return result

    @staticmethod
    def save_user_photo(user_id, building_id, temp_photo_path):
        """
        Zapisuje zdjęcie użytkownika do trwałego miejsca i aktualizuje ścieżkę w bazie danych.
        """
        if not os.path.exists(temp_photo_path):
            print(f"Błąd: Tymczasowa ścieżka do zdjęcia nie istnieje: {temp_photo_path}")
            return None

        try:
            # Określ ścieżkę do katalogu projektu - to jest kluczowa zmiana
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(f"Katalog aplikacji: {app_dir}")

            # Katalog na zdjęcia będzie w głównym katalogu projektu
            user_photos_dir = os.path.join(app_dir, 'user_photos')

            print(f"Tworzenie katalogu zdjęć użytkownika: {user_photos_dir}")
            if not os.path.exists(user_photos_dir):
                os.makedirs(user_photos_dir, exist_ok=True)

            file_ext = os.path.splitext(temp_photo_path)[1]
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            new_filename = f"user_{user_id}_building_{building_id}_{timestamp}{file_ext}"
            new_photo_path = os.path.join(user_photos_dir, new_filename)

            print(f"Kopiowanie zdjęcia z {temp_photo_path} do {new_photo_path}")
            shutil.copy2(temp_photo_path, new_photo_path)

            # Sprawdź czy plik został skopiowany poprawnie
            if not os.path.exists(new_photo_path):
                print(f"Błąd: Nie udało się skopiować pliku do {new_photo_path}")
                return None

            print(f"Plik pomyślnie skopiowany do {new_photo_path}")

            # Dodajemy pełną ścieżkę do bazy danych, żeby uniknąć problemów z lokalizacją
            visit = UserBuildingRepository.check_visit(user_id, building_id)
            if visit:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE UserBuilding SET user_photo_path = ? WHERE user_id = ? AND building_id = ?",
                    (new_photo_path, user_id, building_id)  # Używamy pełnej ścieżki
                )
                conn.commit()
                conn.close()

                if visit.user_photo_path and os.path.exists(
                        visit.user_photo_path) and visit.user_photo_path != new_photo_path:
                    try:
                        os.remove(visit.user_photo_path)
                        print(f"Usunięto stare zdjęcie: {visit.user_photo_path}")
                    except Exception as e:
                        print(f"Błąd podczas usuwania starego zdjęcia: {e}")
            else:
                UserBuildingRepository.add_visit(user_id, building_id, None, new_photo_path)  # Używamy pełnej ścieżki

            return new_photo_path

        except Exception as e:
            print(f"Błąd podczas zapisywania zdjęcia użytkownika: {e}")
            import traceback
            traceback.print_exc()
            return None