class Building:
    def __init__(self, building_id=None, name=None, description=None, image_path=None, latitude=None, longitude=None):
        self.building_id = building_id
        self.name = name
        self.description = description
        self.image_path = image_path
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_db_row(cls, row):
        if row is None:
            return None

        latitude = row['latitude'] if 'latitude' in row.keys() else None
        longitude = row['longitude'] if 'longitude' in row.keys() else None

        return cls(
            building_id=row['building_id'],
            name=row['name'],
            description=row['description'],
            image_path=row['image_path'],
            latitude=latitude,
            longitude=longitude
        )