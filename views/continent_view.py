import flet as ft


def create_continent_view(page):
    continents = ["Europa", "Azja", "Ameryka Północna", "Ameryka Południowa", "Afryka", "Australia i Oceania"]

    def on_continent_click(e):
        selected_continent = e.control.data
        from views.country_view import create_country_view
        page.views.append(create_country_view(page, selected_continent))
        page.update()

    def show_profile(e):
        from views.profile_view import create_profile_view
        page.views.append(create_profile_view(page))
        page.update()

    def logout(e):
        page.session_clear()
        page.views.clear()
        from views.welcome_view import create_welcome_view
        page.views.append(create_welcome_view(page))
        page.update()

    profile_button = ft.ElevatedButton(
        text="Mój profil",
        on_click=show_profile,
        bgcolor=ft.colors.BLUE_500,
        color=ft.colors.WHITE,
    )

    logout_button = ft.ElevatedButton(
        text="Wyloguj",
        on_click=logout,
        bgcolor=ft.colors.RED_500,
        color=ft.colors.WHITE,
    )

    header_row = ft.Row(
        [
            profile_button,
            logout_button
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=10
    )

    continent_buttons = ft.Column(
        [
            ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.LANDSCAPE, color=ft.colors.GREEN),
                        ft.Text(continent, size=16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                on_click=on_continent_click,
                data=continent,
                style=ft.ButtonStyle(
                    color=ft.colors.BLUE_900,
                    bgcolor=ft.colors.BLUE_100,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
            )
            for continent in continents
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    return ft.View(
        "/continents",
        [
            header_row,
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            ft.Text("Wybierz kontynent:", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            continent_buttons,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
    )