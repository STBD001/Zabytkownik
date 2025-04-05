from database.db_config import get_connection
from database.models.user import User


class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        """Pobiera użytkownika po ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User.from_db_row(row)

    @staticmethod
    def get_by_nickname(nickname):
        """Pobiera użytkownika po nicku"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE nickname = ?", (nickname,))
        row = cursor.fetchone()
        conn.close()
        return User.from_db_row(row)

    @staticmethod
    def get_all():
        """Pobiera wszystkich użytkowników"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User")
        users = [User.from_db_row(row) for row in cursor.fetchall()]
        conn.close()
        return users

    @staticmethod
    def create(user):
        """Tworzy nowego użytkownika"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO User (nickname, password_hash, number_of_achievements) VALUES (?, ?, ?)",
            (user.nickname, user.password_hash, user.number_of_achievements)
        )
        user.user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user

    @staticmethod
    def update(user):
        """Aktualizuje dane użytkownika"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE User SET nickname = ?, password_hash = ?, number_of_achievements = ? WHERE user_id = ?",
            (user.nickname, user.password_hash, user.number_of_achievements, user.user_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    @staticmethod
    def delete(user_id):
        """Usuwa użytkownika o podanym ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE user_id = ?", (user_id,))
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def authenticate(nickname, password):
        """Autoryzuje użytkownika na podstawie nicku i hasła"""
        user = UserRepository.get_by_nickname(nickname)
        if user and user.verify_password(password):
            return user
        return None

    @staticmethod
    def update_achievements(user_id, achievements_count):
        """Aktualizuje liczbę osiągnięć użytkownika"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE User SET number_of_achievements = ? WHERE user_id = ?",
            (achievements_count, user_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0