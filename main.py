import flet as ft
from database.db_init import initialize_database, seed_database
from views.welcome_view import create_welcome_view

class SimpleSession:
    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def clear(self):
        self._data.clear()


def main(page: ft.Page):
    initialize_database()
    seed_database()

    page.title = "Zabytkownik"
    page.theme_mode = ft.ThemeMode.LIGHT
    page._session = SimpleSession()

    def get_session_value(key, default=None):
        return page._session.get(key, default)

    def set_session_value(key, value):
        page._session.set(key, value)

    def clear_session():
        page._session.clear()

    page.session_get = get_session_value
    page.session_set = set_session_value
    page.session_clear = clear_session

    def route_change(route):
        print(f"Nowa trasa: {route.route}")

    page.on_route_change = route_change

    page.views.append(create_welcome_view(page))

    page.update()

if __name__ == "__main__":
    ft.app(target=main)