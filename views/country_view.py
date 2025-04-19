import flet as ft
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    apply_route_change_animation
)


def create_country_view(page, continent):
    countries = {
        "Europa": [
            {"name": "Polska", "flag": "🇵🇱", "enabled": True},
            {"name": "Niemcy", "flag": "🇩🇪", "enabled": True},
            {"name": "Francja", "flag": "🇫🇷", "enabled": False},
            {"name": "Włochy", "flag": "🇮🇹", "enabled": False},
            {"name": "Hiszpania", "flag": "🇪🇸", "enabled": False},
            {"name": "Wielka Brytania", "flag": "🇬🇧", "enabled": False}
        ],
        "Azja": [
            {"name": "Japonia", "flag": "🇯🇵", "enabled": False},
            {"name": "Chiny", "flag": "🇨🇳", "enabled": False},
            {"name": "Indie", "flag": "🇮🇳", "enabled": False},
            {"name": "Korea Południowa", "flag": "🇰🇷", "enabled": False}
        ],
        "Ameryka Północna": [
            {"name": "USA", "flag": "🇺🇸", "enabled": False},
            {"name": "Kanada", "flag": "🇨🇦", "enabled": False},
            {"name": "Meksyk", "flag": "🇲🇽", "enabled": False}
        ],
        "Ameryka Południowa": [
            {"name": "Brazylia", "flag": "🇧🇷", "enabled": False},
            {"name": "Argentyna", "flag": "🇦🇷", "enabled": False},
            {"name": "Chile", "flag": "🇨🇱", "enabled": False}
        ],
        "Afryka": [
            {"name": "Egipt", "flag": "🇪🇬", "enabled": False},
            {"name": "RPA", "flag": "🇿🇦", "enabled": False},
            {"name": "Maroko", "flag": "🇲🇦", "enabled": False}
        ],
        "Australia i Oceania": [
            {"name": "Australia", "flag": "🇦🇺", "enabled": False},
            {"name": "Nowa Zelandia", "flag": "🇳🇿", "enabled": False}
        ]
    }

    continent_countries = countries.get(continent, [])

    def on_country_click(e):
        selected_country = e.data
        print(f"Kliknięto kraj: {selected_country}")

        for country in continent_countries:
            if country["name"] == selected_country and not country["enabled"]:
                show_snackbar(
                    page,
                    f"Kraj {selected_country} będzie dostępny wkrótce!",
                    color=AppTheme.WARNING
                )
                return

        loading = show_loading(page, f"Wczytywanie miast w {selected_country}...")

        import time
        time.sleep(0.5)

        from views.city_view import create_city_view
        city_view = create_city_view(page, selected_country)

        hide_loading(page, loading)

        apply_route_change_animation(page, city_view)

    def go_back(e):
        print("Powrót z widoku krajów")
        try:
            from views.continent_view import create_continent_view
            continent_view = create_continent_view(page)
            apply_route_change_animation(page, continent_view, direction="backward")

            # Usuń poprzedni widok
            if len(page.views) > 1:
                page.views.pop(0)
            page.update()
        except Exception as ex:
            print(f"Błąd podczas powrotu: {ex}")
            import traceback
            traceback.print_exc()

            # Awaryjny powrót
            page.views.clear()
            from views.continent_view import create_continent_view
            page.views.append(create_continent_view(page))
            page.update()

    header = create_header(
        f"Kraje w {continent}",
        with_back_button=False,  # Zmiana - używamy własnego przycisku
        page=page,
        with_profile=True
    )

    country_cards = []

    for country in continent_countries:
        # Zawartość karty
        card_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    country["flag"],
                    size=48,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    country["name"],
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(
                    content=ft.Text(
                        "Dostępny" if country["enabled"] else "Wkrótce dostępny",
                        size=12,
                        color=AppTheme.SUCCESS if country["enabled"] else AppTheme.WARNING,
                        italic=True,
                        text_align=ft.TextAlign.CENTER
                    ),
                    margin=ft.margin.only(top=5)
                )
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            width=150,
            height=150,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        # Używamy GestureDetector zamiast on_click w Card
        card_with_gesture = ft.GestureDetector(
            content=ft.Card(
                content=card_content,
                elevation=3,
                margin=ft.margin.all(10),
            ),
            on_tap=lambda e, name=country["name"]: on_country_click(type('obj', (object,), {'data': name})),
            # Usunięto mouse_cursor
        )

        def create_hover_handler(card_widget, country_enabled):
            def on_hover(e):
                try:
                    if e.data == "true":
                        card_widget.elevation = 8
                        card_widget.content.scale = 1.05
                        card_widget.content.bgcolor = ft.colors.BLUE_50 if country_enabled else ft.colors.GREY_100
                    else:
                        card_widget.elevation = 3
                        card_widget.content.scale = 1.0
                        card_widget.content.bgcolor = ft.colors.WHITE
                    card_widget.update()
                except Exception as err:
                    print(f"Błąd w obsłudze hover: {err}")

            return on_hover

        # Zastosuj obsługę hover do karty
        card_with_gesture.content.on_hover = create_hover_handler(card_with_gesture.content, country["enabled"])
        country_cards.append(card_with_gesture)

    country_grid = ft.Row(
        controls=country_cards,
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

    def go_to_profile(e):
        loading = show_loading(page, "Wczytywanie profilu...")

        import time
        time.sleep(0.5)

        from views.profile_view import create_profile_view
        profile_view = create_profile_view(page)

        hide_loading(page, loading)

        apply_route_change_animation(page, profile_view)

    profile_button = create_action_button(
        "Mój profil",
        icon=ft.icons.PERSON,
        on_click=go_to_profile,
        color=AppTheme.PRIMARY
    )

    action_buttons = ft.Row(
        [back_button, profile_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    content = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Text(
                    f"Wybierz kraj aby zobaczyć dostępne miasta i zabytki",
                    size=16,
                    color=AppTheme.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER
                ),
                margin=ft.margin.symmetric(vertical=20)
            ),

            ft.Container(
                content=country_grid,
                padding=20,
                height=350,
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
        "/countries",
        [
            header,
            content
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )