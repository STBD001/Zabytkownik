from database.db_config import get_connection
from database.models.user_building import UserBuilding
from datetime import datetime


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
    def add_visit(user_id, building_id, visit_date=None):
        """Dodaje wizytę użytkownika w budynku"""
        if visit_date is None:
            visit_date = datetime.now().strftime('%Y-%m-%d')

        existing_visit = UserBuildingRepository.check_visit(user_id, building_id)
        if existing_visit:
            return existing_visit

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO UserBuilding (user_id, building_id, visit_date) VALUES (?, ?, ?)",
            (user_id, building_id, visit_date)
        )
        conn.commit()

        new_visit = UserBuilding(user_id, building_id, visit_date)

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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM UserBuilding WHERE user_id = ? AND building_id = ?",
            (user_id, building_id)
        )
        result = cursor.rowcount > 0

        if result:
            cursor.execute("SELECT COUNT(*) FROM UserBuilding WHERE user_id = ?", (user_id,))
            achievements_count = cursor.fetchone()[0]

            cursor.execute(
                "UPDATE User SET number_of_achievements = ? WHERE user_id = ?",
                (achievements_count, user_id)
            )

        conn.commit()
        conn.close()
        return result