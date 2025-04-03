import flet as ft


def create_city_view(page, country):
    cities = {
        "Polska": ["Wrocław"],
        "Niemcy": ["Cooming Soon"],
    }.get(country, [])

    def on_city_click(e):
        selected_city = e.control.data
        from views.monument_view import create_monument_view
        page.views.append(create_monument_view(page, selected_city))
        page.update()

    def go_back(e):
        # Usuń bieżący widok (miast)
        page.views.pop()
        page.update()

    # Definicja przycisku powrotu
    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        )
    )

    city_buttons = ft.Column(
        [
            ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.FLAG, color=ft.Colors.BLUE),
                        ft.Text(city, size=16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                on_click=on_city_click,
                data=city,
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_900,
                    bgcolor=ft.Colors.BLUE_100,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
            )
            for city in cities
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    return ft.View(
        "/cities",
        [
            ft.Text(f"Wybierz miasto w {country}:", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            city_buttons,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            back_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )