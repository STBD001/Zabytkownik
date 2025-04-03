import flet as ft

def create_register_view(page):
    username_field = ft.TextField(label="Nazwa użytkownika", width=300)
    password_field = ft.TextField(label="Hasło", width=300, password=True)
    confirm_password_field = ft.TextField(label="Potwierdź hasło", width=300, password=True)

    def register(e):
        if username_field.value and password_field.value and confirm_password_field.value:
            if password_field.value == confirm_password_field.value:
                print(f"Zarejestrowano użytkownika: {username_field.value}")
                page.views.clear()
                # Importuj dopiero w funkcji, aby uniknąć importu cyklicznego
                from views.login_view import create_login_view
                page.views.append(create_login_view(page))  # Przejdź do widoku logowania
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Hasła nie są identyczne!"))
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Proszę wypełnić wszystkie pola!"))
            page.snack_bar.open = True
            page.update()

    register_button = ft.ElevatedButton(
        text="Zarejestruj",
        on_click=register,
        width=200,
        bgcolor=ft.colors.BLUE_500,
        color=ft.colors.WHITE,
    )

    return ft.View(
        "/register",
        [
            ft.Text("Rejestracja", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            username_field,
            password_field,
            confirm_password_field,
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            register_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
