from database.db_config import get_connection
from database.models.building import Building


class BuildingRepository:
    @staticmethod
    def get_by_id(building_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Building WHERE building_id = ?", (building_id,))
        row = cursor.fetchone()
        conn.close()
        return Building.from_db_row(row)

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Building")
        buildings = [Building.from_db_row(row) for row in cursor.fetchall()]
        conn.close()
        return buildings

    @staticmethod
    def get_buildings_by_city(city_name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Building WHERE description LIKE ?", (f'%{city_name}%',))
        buildings = [Building.from_db_row(row) for row in cursor.fetchall()]
        conn.close()
        return buildings

    @staticmethod
    def create(building):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Building (name, description, image_path, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
            (building.name, building.description, building.image_path, building.latitude, building.longitude)
        )
        building.building_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return building

    @staticmethod
    def update(building):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Building SET name = ?, description = ?, image_path = ?, latitude = ?, longitude = ? WHERE building_id = ?",
            (building.name, building.description, building.image_path, building.latitude, building.longitude, building.building_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    @staticmethod
    def delete(building_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Building WHERE building_id = ?", (building_id,))
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return result