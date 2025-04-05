import flet as ft
from database.repositories.user_repository import UserRepository
from database.models.user import User


def create_register_view(page):
    username_field = ft.TextField(label="Nazwa użytkownika", width=300)
    password_field = ft.TextField(label="Hasło", width=300, password=True)
    confirm_password_field = ft.TextField(label="Potwierdź hasło", width=300, password=True)
    error_text = ft.Text("", color=ft.colors.RED_500)

    def register(e):
        if username_field.value and password_field.value and confirm_password_field.value:
            if password_field.value == confirm_password_field.value:
                existing_user = UserRepository.get_by_nickname(username_field.value)

                if existing_user:
                    error_text.value = "Użytkownik o takiej nazwie już istnieje"
                    page.update()
                    return

                password_hash = User.hash_password(password_field.value)
                new_user = User(
                    nickname=username_field.value,
                    password_hash=password_hash,
                    number_of_achievements=0
                )
                created_user = UserRepository.create(new_user)

                if created_user:
                    page.views.clear()
                    from views.login_view import create_login_view
                    page.views.append(create_login_view(page))
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Rejestracja zakończona pomyślnie! Możesz się teraz zalogować."))
                    page.snack_bar.open = True
                    page.update()
                else:
                    error_text.value = "Błąd podczas rejestracji. Spróbuj ponownie."
                    page.update()
            else:
                error_text.value = "Hasła nie są identyczne!"
                page.update()
        else:
            error_text.value = "Proszę wypełnić wszystkie pola!"
            page.update()

    register_button = ft.ElevatedButton(
        text="Zarejestruj",
        on_click=register,
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
        "/register",
        [
            ft.Text("Rejestracja", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            username_field,
            password_field,
            confirm_password_field,
            error_text,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            register_button,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            back_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )