import flet as ft

def create_country_view(page, continent):
    countries = {
        "Europa": ["Polska", "Niemcy"],
        "Azja": ["Coming soon"],
        "Ameryka Północna": ["Coming soon"],
        "Ameryka Południowa": ["Coming soon"],
        "Afryka": ["Coming soon"],
        "Australia i Oceania": ["Coming soon"],
    }.get(continent, [])

    def on_country_click(e):
        selected_country = e.control.data
        from views.city_view import create_city_view
        page.views.append(create_city_view(page, selected_country))
        page.update()

    # Funkcja do powrotu do widoku kontynentów
    def go_back(e):
        # Usuń bieżący widok (krajów)
        page.views.pop()
        page.update()

    country_buttons = ft.Column(
        [
            ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.FLAG, color=ft.colors.BLUE),
                        ft.Text(country, size=16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                on_click=on_country_click,
                data=country,  # Dodanie data z nazwą kraju
                style=ft.ButtonStyle(
                    color=ft.colors.BLUE_900,
                    bgcolor=ft.colors.BLUE_100,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
            )
            for country in countries
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # Dodanie przycisku powrotu
    back_button = ft.ElevatedButton(
        text="Powrót",
        on_click=go_back,
        bgcolor=ft.colors.BLUE_GREY_400,
        color=ft.colors.WHITE,
    )

    return ft.View(
        "/countries",
        [
            ft.Text(f"Wybierz państwo ({continent}):", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            country_buttons,
            ft.Divider(height=20, color=ft.colors.TRANSPARENT),
            back_button,  # Dodanie przycisku powrotu
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )