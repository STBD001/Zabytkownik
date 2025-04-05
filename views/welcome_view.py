import flet as ft


def create_welcome_view(page):
    def go_to_register(e):
        from views.register_view import create_register_view
        page.views.append(create_register_view(page))
        page.update()

    def go_to_login(e):
        from views.login_view import create_login_view
        page.views.append(create_login_view(page))
        page.update()

    register_button = ft.ElevatedButton(
        text="Zarejestruj",
        on_click=go_to_register,
        width=200,
        bgcolor=ft.colors.BLUE_500,
        color=ft.colors.WHITE,
    )

    login_button = ft.ElevatedButton(
        text="Zaloguj",
        on_click=go_to_login,
        width=200,
        bgcolor=ft.colors.GREEN_500,
        color=ft.colors.WHITE,
    )

    return ft.View(
        "/welcome",
        [
            ft.Text("Witaj w Zabytkowniku!", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            register_button,
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            login_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )