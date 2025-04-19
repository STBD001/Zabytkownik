import flet as ft
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    show_confirmation_dialog, apply_route_change_animation
)


def create_continent_view(page):
    print("Tworzenie widoku kontynentów...")

    # Sprawdź, czy istnieje sesja użytkownika
    current_user = page.session_get("current_user")
    if not current_user:
        print("BŁĄD: Brak danych użytkownika w sesji")
        # Dodaj awaryjne dane użytkownika, żeby widok mógł się załadować
        from database.models.user import User
        default_user = User(user_id=0, nickname="Gość", password_hash="", number_of_achievements=0)
        page.session_set("current_user", default_user)
        page.session_set("current_user_id", 0)
    else:
        print(f"Zalogowany użytkownik: {current_user.nickname} (ID: {current_user.user_id})")

    continents = [
        {"name": "Europa", "icon": ft.icons.EURO, "color": AppTheme.PRIMARY, "enabled": True},
        {"name": "Azja", "icon": ft.icons.TEMPLE_BUDDHIST, "color": ft.colors.RED_700, "enabled": False},
        {"name": "Ameryka Północna", "icon": ft.icons.MAP, "color": ft.colors.AMBER_700, "enabled": False},
        {"name": "Ameryka Południowa", "icon": ft.icons.FOREST, "color": ft.colors.GREEN_700, "enabled": False},
        {"name": "Afryka", "icon": ft.icons.LANDSCAPE, "color": ft.colors.ORANGE_700, "enabled": False},
        {"name": "Australia i Oceania", "icon": ft.icons.WAVES, "color": ft.colors.CYAN_700, "enabled": False}
    ]

    def on_continent_click(e):
        selected_continent = e.control.data

        for continent in continents:
            if continent["name"] == selected_continent and not continent["enabled"]:
                show_snackbar(
                    page,
                    f"Kontynent {selected_continent} będzie dostępny wkrótce!",
                    color=AppTheme.WARNING
                )
                return

        loading = show_loading(page, f"Wczytywanie krajów kontynentu {selected_continent}...")

        import time
        time.sleep(0.5)

        from views.country_view import create_country_view
        country_view = create_country_view(page, selected_continent)

        hide_loading(page, loading)

        apply_route_change_animation(page, country_view)

    def show_profile(e):
        loading = show_loading(page, "Wczytywanie profilu...")

        import time
        time.sleep(0.5)

        from views.profile_view import create_profile_view
        profile_view = create_profile_view(page)

        hide_loading(page, loading)

        apply_route_change_animation(page, profile_view)

    def logout(e):
        def confirm_logout():
            page.session_clear()
            page.views.clear()
            from views.welcome_view import create_welcome_view
            page.views.append(create_welcome_view(page))
            show_snackbar(page, "Zostałeś wylogowany", color=AppTheme.SUCCESS)

        show_confirmation_dialog(
            page,
            "Wylogowanie",
            "Czy na pewno chcesz się wylogować?",
            confirm_logout
        )

    current_user = page.session_get("current_user")
    user_nickname = current_user.nickname if current_user else "Użytkownik"
    print(f"Bieżący użytkownik: {user_nickname}")

    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.PERSON, size=24, color=ft.colors.WHITE),
                ft.Text(
                    f"Witaj, {user_nickname}!",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Text(
                "Wybierz kontynent, który chcesz zwiedzić",
                size=14,
                color=ft.colors.WHITE,
                text_align=ft.TextAlign.CENTER
            )
        ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER),
        width=page.width,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[AppTheme.PRIMARY, AppTheme.SECONDARY]
        ),
        border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
        animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        animate_opacity=ft.animation.Animation(800, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.colors.BLACK38,
            offset=ft.Offset(0, 4)
        ),
        opacity=0
    )

    def animate_header():
        header.opacity = 1
        page.update()

    page.run_task(animate_header)

    profile_button = create_action_button(
        "Mój profil",
        icon=ft.icons.PERSON,
        on_click=show_profile,
        color=AppTheme.PRIMARY
    )

    logout_button = create_action_button(
        "Wyloguj",
        icon=ft.icons.LOGOUT,
        on_click=logout,
        color=AppTheme.ERROR
    )

    action_buttons = ft.Row(
        [profile_button, logout_button],
        alignment=ft.MainAxisAlignment.END,
        spacing=10
    )

    continent_cards = []

    for continent in continents:
        icon_container = ft.Container(
            content=ft.Icon(
                continent["icon"],
                size=48,
                color=ft.colors.WHITE
            ),
            width=80,
            height=80,
            border_radius=40,
            bgcolor=continent["color"],
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.colors.BLACK26,
                offset=ft.Offset(0, 2)
            )
        )

        status_text = ft.Text(
            "Dostępny" if continent["enabled"] else "Wkrótce dostępny",
            size=12,
            color=AppTheme.SUCCESS if continent["enabled"] else AppTheme.WARNING,
            italic=True
        )

        card_content = ft.Container(
            content=ft.Column([
                icon_container,
                ft.Text(
                    continent["name"],
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                ),
                status_text
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
            padding=20,
            border_radius=15,
            bgcolor=ft.colors.WHITE,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        card = ft.Card(
            content=card_content,
            elevation=3,
            margin=ft.margin.all(10),
            on_click=on_continent_click,
            data=continent["name"]
        )

        def create_hover_handler(card_color):
            def on_hover(e):
                try:
                    if e.data == "true":
                        e.control.elevation = 8
                        e.control.content.scale = 1.05
                        e.control.content.bgcolor = ft.colors.with_opacity(0.1, card_color)
                    else:
                        e.control.elevation = 3
                        e.control.content.scale = 1.0
                        e.control.content.bgcolor = ft.colors.WHITE
                    e.control.update()
                except Exception as err:
                    print(f"Błąd w obsłudze hover: {err}")

            return on_hover

        card.on_hover = create_hover_handler(continent["color"])
        continent_cards.append(card)

    continent_grid = ft.Column([
        ft.Row(
            continent_cards[:3],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        ft.Row(
            continent_cards[3:],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
    ], spacing=10)

    footer = ft.Container(
        content=ft.Column([
            ft.Divider(height=1, color=ft.colors.GREY_300),
            ft.Row([
                ft.Text(
                    "Zabytkownik v1.0",
                    size=12,
                    color=AppTheme.TEXT_HINT
                ),
                ft.Text(
                    "© 2023 Zabytkownik Team",
                    size=12,
                    color=AppTheme.TEXT_HINT
                )
            ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10)
        ]),
        padding=ft.padding.symmetric(vertical=10, horizontal=20),
        margin=ft.margin.only(top=20)
    )

    view = ft.View(
        "/continents",
        [
            header,
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=action_buttons,
                        padding=ft.padding.symmetric(horizontal=20)
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Wybierz kontynent",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        margin=ft.margin.symmetric(vertical=20),
                        alignment=ft.alignment.center
                    ),
                    continent_grid,
                    footer
                ]),
                padding=20,
                expand=True
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )

    print("Widok kontynentów utworzony pomyślnie.")
    return view