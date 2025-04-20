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
        print(f"Kliknięto kontynent: {e.control.data}")
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

        try:
            import time
            time.sleep(0.5)

            from views.country_view import create_country_view
            country_view = create_country_view(page, selected_continent)

            if country_view:
                hide_loading(page, loading)
                apply_route_change_animation(page, country_view)
            else:
                raise Exception(f"Nie udało się utworzyć widoku dla kontynentu {selected_continent}")

        except Exception as ex:
            print(f"Błąd podczas ładowania krajów: {ex}")
            import traceback
            traceback.print_exc()

            hide_loading(page, loading)
            show_snackbar(page, f"Błąd ładowania krajów: {str(ex)}", color=AppTheme.ERROR)

    def show_profile(e):
        print("Kliknięto przycisk Mój profil")
        loading = show_loading(page, "Wczytywanie profilu...")

        try:
            import time
            time.sleep(0.5)

            from views.profile_view import create_profile_view
            profile_view = create_profile_view(page)

            if profile_view:
                hide_loading(page, loading)
                # Dodaj widok profilu do stosu widoków
                apply_route_change_animation(page, profile_view)
            else:
                raise Exception("Nie udało się utworzyć widoku profilu")
        except Exception as ex:
            print(f"Błąd podczas ładowania profilu: {ex}")
            import traceback
            traceback.print_exc()

            hide_loading(page, loading)
            show_snackbar(page, f"Błąd podczas ładowania profilu: {str(ex)}", color=AppTheme.ERROR)
        finally:
            # Upewnij się, że ładowanie jest zawsze ukrywane
            try:
                hide_loading(page, loading)
            except:
                pass

    def logout(e):
        print("Kliknięto przycisk wylogowania")

        # Zamiast dialogu, użyjmy BottomSheet
        logout_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Wylogowanie",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.PRIMARY
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Czy na pewno chcesz się wylogować?",
                        size=16,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row([
                        ft.ElevatedButton(
                            "Anuluj",
                            on_click=lambda e: close_sheet(),
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=AppTheme.SECONDARY
                            )
                        ),
                        ft.ElevatedButton(
                            "Wyloguj",
                            on_click=lambda e: perform_logout(),
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=AppTheme.ERROR
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                padding=20,
                width=page.width
            ),
            open=True
        )

        def close_sheet():
            page.overlay.remove(logout_sheet)
            page.update()

        def perform_logout():
            close_sheet()
            page.session_clear()
            page.views.clear()
            from views.welcome_view import create_welcome_view
            page.views.append(create_welcome_view(page))
            show_snackbar(page, "Zostałeś wylogowany", color=AppTheme.SUCCESS)

        page.overlay.append(logout_sheet)
        page.update()

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
        opacity=1  # Zmieniono - od razu widoczne
    )

    # Przycisk profilu z obsługą kliknięcia
    profile_button = ft.ElevatedButton(
        text="Mój profil",
        icon=ft.icons.PERSON,
        on_click=show_profile,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=AppTheme.PRIMARY,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=AppTheme.BORDER_RADIUS_MD),
            elevation=5,
            animation_duration=AppTheme.ANIMATION_DURATION_MS,
        ),
    )

    # Przycisk wylogowania z obsługą kliknięcia
    logout_button = ft.ElevatedButton(
        text="Wyloguj",
        icon=ft.icons.LOGOUT,
        on_click=logout,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=AppTheme.ERROR,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=AppTheme.BORDER_RADIUS_MD),
            elevation=5,
            animation_duration=AppTheme.ANIMATION_DURATION_MS,
        ),
    )

    action_buttons = ft.Row(
        [profile_button, logout_button],
        alignment=ft.MainAxisAlignment.END,
        spacing=10
    )

    def create_button_hover_handler(button, color, enabled):
        def hover_handler(e):
            try:
                if e.data == "true" and enabled:
                    button.bgcolor = ft.colors.with_opacity(0.8, color)
                    button.scale = 1.05
                    button.shadow = ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=6,
                        color=ft.colors.BLACK26,
                        offset=ft.Offset(0, 3)
                    )
                else:
                    button.bgcolor = color if enabled else ft.colors.GREY_700
                    button.scale = 1.0
                    button.shadow = ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=4,
                        color=ft.colors.BLACK12,
                        offset=ft.Offset(0, 2)
                    )
                button.update()
            except Exception as err:
                print(f"Błąd hovera przycisku: {err}")

        return hover_handler

    def create_hover_handler(container, color, enabled, button):
        def hover_handler(e):
            try:
                if e.data == "true":
                    # Zawsze pokazujemy efekt hover, niezależnie czy kontynent jest włączony
                    container.bgcolor = ft.colors.with_opacity(0.1, color)
                    container.scale = 1.05
                    container.shadow = ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=10,
                        color=ft.colors.BLACK26,
                        offset=ft.Offset(0, 5)
                    )
                    # Dodaj efekt dla przycisku
                    button.scale = 1.05
                    button.shadow = ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=6,
                        color=ft.colors.BLACK26,
                        offset=ft.Offset(0, 3)
                    )
                else:
                    container.bgcolor = ft.colors.WHITE
                    container.scale = 1.0
                    container.shadow = ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.colors.BLACK12,
                        offset=ft.Offset(0, 2)
                    )
                    # Zresetuj efekt przycisku
                    button.scale = 1.0
                    button.shadow = ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=4,
                        color=ft.colors.BLACK12,
                        offset=ft.Offset(0, 2)
                    )
                container.update()
                button.update()
            except Exception as err:
                print(f"Błąd hovera: {err}")

        return hover_handler

    # Inny sposób tworzenia kart kontynentów
    continent_cards = []

    for continent_data in continents:
        # Tworzenie kontenera z ikoną
        icon_container = ft.Container(
            content=ft.Icon(
                continent_data["icon"],
                size=48,
                color=ft.colors.WHITE
            ),
            width=80,
            height=80,
            border_radius=40,
            bgcolor=continent_data["color"],
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.colors.BLACK26,
                offset=ft.Offset(0, 2)
            )
        )

        # Status kontynentu (dostępny/niedostępny)
        status_text = ft.Text(
            "Dostępny" if continent_data["enabled"] else "Wkrótce dostępny",
            size=12,
            color=AppTheme.SUCCESS if continent_data["enabled"] else AppTheme.WARNING,
            italic=True,
            weight=ft.FontWeight.BOLD  # Pogrubiony tekst statusu
        )

        # Przycisk z ikoną strzałki
        icon_text = ft.Row(
            [
                ft.Icon(ft.icons.ARROW_FORWARD, size=16, color=ft.colors.WHITE),
                ft.Text("Wybierz", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Poprawione przyciski dla niedostępnych kontynentów
        if continent_data["enabled"]:
            # Przyciski dla dostępnych kontynentów - kolor zgodny z kontynentem
            continent_button = ft.Container(
                content=icon_text,
                width=140,
                height=40,
                border_radius=5,
                bgcolor=continent_data["color"],
                alignment=ft.alignment.center,
                on_click=on_continent_click if continent_data["enabled"] else None,
                data=continent_data["name"],
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(0, 2)
                ),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
        else:
            # Przyciski dla niedostępnych kontynentów - lepiej widoczne
            continent_button = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.LOCK_CLOCK, size=16, color=ft.colors.WHITE),
                        ft.Text("Wkrótce", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
                    ],
                    spacing=5,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=140,
                height=40,
                border_radius=5,
                bgcolor=ft.colors.GREY_700,  # Ciemniejszy szary kolor
                alignment=ft.alignment.center,
                on_click=on_continent_click,
                data=continent_data["name"],
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(0, 2)
                ),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

            # Dodaj ozdobny border dla przycisków niedostępnych kontynentów
            continent_button.border = ft.border.all(1, continent_data["color"])

        # Dodaj efekt hover do przycisku
        continent_button.on_hover = create_button_hover_handler(
            continent_button,
            continent_data["color"] if continent_data["enabled"] else ft.colors.GREY_700,
            continent_data["enabled"]
        )

        # ZMIANA: Zwiększona wysokość karty, aby pomieścić przyciski
        # Karta kontynentu w formie kontenera - poprawiony wygląd
        continent_card = ft.Container(
            content=ft.Column([
                icon_container,
                ft.Text(
                    continent_data["name"],
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                ),
                status_text,
                ft.Container(
                    height=15
                ),
                continent_button
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            width=190,  # Zwiększona szerokość karty
            height=270,  # Zwiększona wysokość karty z 250 na 270
            padding=20,
            margin=10,
            border_radius=15,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.BLACK12,
                offset=ft.Offset(0, 2)
            ),
            # Hover efekt
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

        # Dodaj delikatne obramowanie w kolorze kontynentu
        continent_card.border = ft.border.all(2, ft.colors.with_opacity(0.3, continent_data["color"]))

        # Dodaj efekt hover do kontenera
        continent_card.on_hover = create_hover_handler(
            continent_card,
            continent_data["color"],
            continent_data["enabled"],
            continent_button
        )

        continent_cards.append(continent_card)

    # ZMIANA: Dostosowany układ kontynentów - zwiększony spacing i margines
    # Układ kontynentów w dwóch rzędach
    continent_grid = ft.Column([
        ft.Row(
            continent_cards[:3],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15  # Zwiększony spacing między kartami
        ),
        ft.Container(height=10),  # Dodany odstęp między rzędami
        ft.Row(
            continent_cards[3:],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15  # Zwiększony spacing między kartami
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
                    "© 2025 Zabytkownik Team (Stefan Wojciechowski)",
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

    # ZMIANA: Dodano więcej przestrzeni dla całego kontenera
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
                padding=25,
                expand=True
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )

    print("Widok kontynentów utworzony pomyślnie.")
    return view