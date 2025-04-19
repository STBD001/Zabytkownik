class UserBuilding:
    def __init__(self, user_id=None, building_id=None, visit_date=None, user_photo_path=None):
        self.user_id = user_id
        self.building_id = building_id
        self.visit_date = visit_date
        self.user_photo_path = user_photo_path

    @classmethod
    def from_db_row(cls, row):
        if row is None:
            return None

        user_photo_path = None
        if row and 'user_photo_path' in row.keys():
            user_photo_path = row['user_photo_path']

        return cls(
            user_id=row['user_id'],
            building_id=row['building_id'],
            visit_date=row['visit_date'],
            user_photo_path=user_photo_path
        )