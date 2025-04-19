import flet as ft
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    apply_route_change_animation
)


def create_city_view(page, country):
    cities = {
        "Polska": [
            {"name": "Wrocław", "image": "assets/Hala.jpeg", "enabled": True},
            {"name": "Kraków", "image": None, "enabled": False},
            {"name": "Warszawa", "image": None, "enabled": False},
            {"name": "Gdańsk", "image": None, "enabled": False}
        ],
        "Niemcy": [
            {"name": "Berlin", "image": None, "enabled": False},
            {"name": "Monachium", "image": None, "enabled": False},
            {"name": "Hamburg", "image": None, "enabled": False}
        ]
    }

    country_cities = cities.get(country, [])

    def on_city_click(e):
        selected_city = e.control.data

        for city in country_cities:
            if city["name"] == selected_city and not city["enabled"]:
                show_snackbar(
                    page,
                    f"Miasto {selected_city} będzie dostępne wkrótce!",
                    color=AppTheme.WARNING
                )
                return

        loading = show_loading(page, f"Wczytywanie zabytków w {selected_city}...")

        import time
        time.sleep(0.5)

        from views.monument_view import create_monument_view
        monument_view = create_monument_view(page, selected_city)

        hide_loading(page, loading)

        apply_route_change_animation(page, monument_view)

    def go_back(e):
        apply_route_change_animation(page, page.views[-2], direction="backward")
        page.views.pop()
        page.update()

    header = create_header(
        f"Miasta w {country}",
        with_back_button=True,
        page=page,
        with_profile=True
    )

    city_cards = []

    for city in country_cities:
        image = ft.Image(
            src=city["image"] if city["image"] else "assets/placeholder.jpg",
            width=200,
            height=120,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.only(
                top_left=10,
                top_right=10
            )
        )

        status_container = ft.Container(
            content=ft.Text(
                "Dostępne" if city["enabled"] else "Wkrótce dostępne",
                size=12,
                color=ft.colors.WHITE,
                text_align=ft.TextAlign.CENTER,
                weight=ft.FontWeight.BOLD
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=ft.border_radius.all(15),
            bgcolor=AppTheme.SUCCESS if city["enabled"] else AppTheme.WARNING,
            margin=ft.margin.only(bottom=10)
        )

        card_content = ft.Container(
            content=ft.Column([
                image,
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            city["name"],
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        status_container,
                        create_action_button(
                            "Zobacz zabytki",
                            icon=ft.icons.PLACE,
                            on_click=on_city_click,
                            color=AppTheme.PRIMARY,
                            width=180
                        ) if city["enabled"] else ft.Container(
                            content=ft.Text(
                                "Wkrótce dostępne...",
                                size=14,
                                color=AppTheme.TEXT_HINT,
                                italic=True
                            ),
                            margin=ft.margin.only(top=10)
                        )
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5),
                    padding=15
                )
            ],
                spacing=0),
            width=200,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        card = ft.Card(
            content=card_content,
            elevation=3,
            margin=ft.margin.all(10),
            on_click=on_city_click if city["enabled"] else None,
            data=city["name"]
        )

        if city["enabled"]:
            def on_hover(e):
                if e.data == "true":
                    e.control.elevation = 8
                    e.control.content.scale = 1.03
                else:
                    e.control.elevation = 3
                    e.control.content.scale = 1.0
                e.control.update()

            card.on_hover = on_hover

        city_cards.append(card)

    city_grid = ft.Row(
        controls=city_cards,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        wrap=True
    )

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY
    )

    def show_country_map(e):
        show_snackbar(
            page,
            f"Mapa wszystkich miast w {country} będzie dostępna wkrótce!",
            color=AppTheme.INFO
        )

    map_button = create_action_button(
        f"Mapa {country}",
        icon=ft.icons.MAP,
        on_click=show_country_map,
        color=AppTheme.PRIMARY
    )

    action_buttons = ft.Row(
        [back_button, map_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    if not city_cards:
        city_grid = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.icons.LOCATION_CITY,
                    size=64,
                    color=AppTheme.PRIMARY
                ),
                ft.Text(
                    f"Brak dostępnych miast w {country}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Dodajemy nowe miasta regularnie, sprawdź później!",
                    size=14,
                    color=AppTheme.TEXT_HINT,
                    text_align=ft.TextAlign.CENTER
                )
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
            padding=30,
            alignment=ft.alignment.center
        )

    content = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    f"Wybierz miasto aby zobaczyć dostępne zabytki",
                    size=16,
                    color=AppTheme.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER
                ),
                margin=ft.margin.symmetric(vertical=20)
            ),

            ft.Container(
                content=city_grid,
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(0, 2)
                )
            ),

            ft.Container(
                content=action_buttons,
                margin=ft.margin.only(top=20)
            )
        ]),
        padding=20,
        expand=True
    )

    return ft.View(
        "/cities",
        [
            header,
            content
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )