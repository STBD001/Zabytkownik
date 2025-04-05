class UserBuilding:
    def __init__(self, user_id=None, building_id=None, visit_date=None):
        self.user_id = user_id
        self.building_id = building_id
        self.visit_date = visit_date

    @classmethod
    def from_db_row(cls, row):
        if row is None:
            return None
        return cls(
            user_id=row['user_id'],
            building_id=row['building_id'],
            visit_date=row['visit_date']
        )