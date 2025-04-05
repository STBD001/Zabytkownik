# database/models/user.py
import hashlib


class User:
    def __init__(self, user_id=None, nickname=None, password_hash=None, number_of_achievements=0):
        self.user_id = user_id
        self.nickname = nickname
        self.password_hash = password_hash
        self.number_of_achievements = number_of_achievements

    @classmethod
    def from_db_row(cls, row):
        """Tworzy obiekt User z wiersza bazy danych"""
        if row is None:
            return None
        return cls(
            user_id=row['user_id'],
            nickname=row['nickname'],
            password_hash=row['password_hash'],
            number_of_achievements=row['number_of_achievements']
        )

    @staticmethod
    def hash_password(password):
        """Tworzy hash hasła dla bezpiecznego przechowywania"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        """Sprawdza, czy podane hasło jest poprawne"""
        return self.password_hash == User.hash_password(password)