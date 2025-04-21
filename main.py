import flet as ft
import threading
from database.db_init import initialize_database, seed_database
from database.db_update import update_database_schema
from views.welcome_view import create_welcome_view
from ui_helpers import AppTheme, show_loading, hide_loading
from setup_reference_dirs import setup_reference_directories
from translations import TranslationManager, get_text


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
    print("Inicjalizacja aplikacji...")

    loading = show_loading(page, "Uruchamianie Zabytkownika...")

    try:
        initialize_database()
        seed_database()
        update_database_schema()

        setup_reference_directories()

        try:
            from db_update_fix import fix_database
            print("Uruchamianie naprawy bazy danych...")
            fix_database()
            print("Naprawa bazy danych zakończona")
        except ImportError:
            print("Moduł naprawy bazy danych nie jest dostępny")
        except Exception as e:
            print(f"Błąd podczas naprawy bazy danych: {e}")
    except Exception as e:
        print(f"Błąd podczas inicjalizacji bazy danych: {e}")
        import traceback
        traceback.print_exc()

    page.title = "Zabytkownik"

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

    dark_mode_preference = page.session_get("dark_mode", False)
    if dark_mode_preference:
        AppTheme._DARK_MODE = True

    language_preference = page.session_get("language", "pl")
    if language_preference in TranslationManager.LANGUAGES:
        TranslationManager.set_language(language_preference)

    page.theme = AppTheme.create_theme()
    page.theme_mode = ft.ThemeMode.DARK if AppTheme._DARK_MODE else ft.ThemeMode.LIGHT

    page.padding = 0
    page.window_width = 800
    page.window_height = 600
    page.window_min_width = 400

    def route_change(route):
        print(f"Nowa trasa: {route.route}")

    page.on_route_change = route_change

    try:
        error_view = ft.View(
            "/error",
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text(get_text("error"), size=24, color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                        ft.Text(get_text("try_again"), size=16),
                        ft.ElevatedButton(get_text("refresh"), on_click=lambda _: page.window_close())
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
        )

        welcome_view = create_welcome_view(page)
        if not welcome_view:
            print("Błąd: Widok powitalny nie został utworzony")
            page.views.append(error_view)
        else:
            page.views.append(welcome_view)
            print("Widok powitalny dodany pomyślnie")

        page.update()

        hide_loading(page, loading)
        page.update()

        print("Aplikacja uruchomiona pomyślnie")
    except Exception as e:
        print(f"Błąd krytyczny podczas uruchamiania aplikacji: {e}")
        import traceback
        traceback.print_exc()

        try:
            hide_loading(page, loading)
            page.views.clear()
            page.views.append(error_view)
            page.update()
        except:
            pass


if __name__ == "__main__":
    ft.app(target=main)