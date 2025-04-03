import flet as ft

def create_monument_view(page, city):
    monuments = {
        "Wrocław": [
            { "name": "Hala stulecia","image": "assets/Hala.jpeg","location": "51.107337, 17.076095","map_image": "assets/HalaMap.jpg"},
            {"name": "Katedra","image": "assets/Katedra.jpg","location": "51.114167, 17.045444","map_image": "assets/KatedraMap.jpg"},
            {"name": "SkyTower","image": "assets/SkyTower.jpg","location": "51.094688, 17.018316","map_image": "assets/SKMap.jpg"}
        ],
    }.get(city, [])

    def on_monuments_click(e):
        selected_monument = e.control.data
        page.views.append(create_monument_detail_view(page, selected_monument))
        page.update()

    def go_back(e):
        page.views.pop()
        page.update()

    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        )
    )

    monument_buttons = ft.Column(
        [
            ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.FLAG, color=ft.Colors.BLUE),
                        ft.Text(monument["name"], size=16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                on_click=on_monuments_click,
                data=monument,
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_900,
                    bgcolor=ft.Colors.BLUE_100,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
            )
            for monument in monuments
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    return ft.View(
        "/monuments",
        [
            ft.Text(f"Wybierz zabytek w {city}:", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            monument_buttons,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            back_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

def create_monument_detail_view(page, monument):
    def go_back(e):
        page.views.pop()
        page.update()

    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        )
    )

    add_photo_button = ft.ElevatedButton(
        "Dodaj zdjęcie",
        on_click=lambda e: print("Dodaj zdjęcie"),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_700,
        )
    )

    # Link do Google Maps z lokalizacją
    map_url = f"https://www.google.com/maps/search/?api=1&query={monument['location']}"

    return ft.View(
        f"/monuments/{monument['name']}",
        [
            ft.Text(monument["name"], size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Row(
                [
                    # Kolumna z obrazem zabytku
                    ft.Column(
                        [
                            ft.Image(
                                src=monument["image"],
                                width=500,
                                height=400,
                                fit=ft.ImageFit.CONTAIN,
                            )
                        ],
                        width=600,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    # Kolumna z mapą i lokalizacją
                    ft.Column(
                        [
                            ft.Image(
                                src=monument['map_image'],
                                width=500,
                                height=400,
                                fit=ft.ImageFit.CONTAIN,
                            ),
                            ft.Text(f"Lokalizacja: {monument['location']}", size=16),
                            ft.ElevatedButton(
                                "Pokaż na mapie",
                                on_click=lambda e: page.launch_url(map_url),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.BLUE_700,
                                )
                            )
                        ],
                        width=600,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            add_photo_button,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            back_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )