import flet as ft

def create_login_view(page):
    username_field = ft.TextField(label="Nazwa użytkownika", width=300)
    password_field = ft.TextField(label="Hasło", width=300, password=True)

    def login(e):
        if username_field.value and password_field.value:
            print(f"Zalogowano jako: {username_field.value}")
            page.views.clear()
            # Importuj dopiero w funkcji, aby uniknąć importu cyklicznego
            from views.continent_view import create_continent_view
            page.views.append(create_continent_view(page))  # Przejdź do widoku kontynentów
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Proszę podać nazwę użytkownika i hasło."))
            page.snack_bar.open = True
            page.update()

    login_button = ft.ElevatedButton(
        text="Zaloguj",
        on_click=login,
    )

    return ft.View(
        "/login",
        [
            ft.Text("Logowanie", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            username_field,
            password_field,
            login_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
