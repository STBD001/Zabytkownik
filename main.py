import flet as ft
from views.welcome_view import create_welcome_view

def main(page: ft.Page):
    page.title = "Zabytkownik"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_100

    # Ustaw początkowy widok na widok powitalny
    page.views.append(create_welcome_view(page))
    page.update()

# Uruchom aplikację
ft.app(target=main)