import flet as ft
from database.repositories.user_repository import UserRepository


def create_login_view(page):
    username_field = ft.TextField(label="Nazwa użytkownika", width=300)
    password_field = ft.TextField(label="Hasło", width=300, password=True)
    error_text = ft.Text("", color=ft.colors.RED_500)

    def login(e):
        if username_field.value and password_field.value:
            user = UserRepository.authenticate(username_field.value, password_field.value)

            if user:
                page.session_set("current_user", user)
                page.session_set("current_user_id", user.user_id)

                page.views.clear()
                from views.continent_view import create_continent_view
                page.views.append(create_continent_view(page))
                page.update()
            else:
                error_text.value = "Nieprawidłowa nazwa użytkownika lub hasło"
                page.update()
        else:
            error_text.value = "Proszę podać nazwę użytkownika i hasło"
            page.update()

    login_button = ft.ElevatedButton(
        text="Zaloguj",
        on_click=login,
        width=200,
        bgcolor=ft.colors.BLUE_500,
        color=ft.colors.WHITE,
    )

    def go_back(e):
        page.views.pop()
        page.update()

    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        bgcolor=ft.colors.BLUE_GREY_400,
        color=ft.colors.WHITE,
    )

    return ft.View(
        "/login",
        [
            ft.Text("Logowanie", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            username_field,
            password_field,
            error_text,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            login_button,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            back_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )