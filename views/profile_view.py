import flet as ft
from database.repositories.user_repository import UserRepository
from database.repositories.user_building_repository import UserBuildingRepository
from database.repositories.building_repository import BuildingRepository
import os
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    show_confirmation_dialog, apply_route_change_animation
)


def show_visited_monuments_map(e, user_id, page):
    print(f"Uruchamiam funkcję pokazywania mapy dla użytkownika {user_id}")
    try:
        loading = show_loading(page, "Wczytywanie mapy odwiedzonych zabytków...")

        # Dodajemy opóźnienie dla pewności
        import time
        time.sleep(0.5)

        # Bezpośrednio importujemy i tworzymy mapę
        try:
            from views.map_view import create_map_view
            # Przekazujemy user_id dla filtrowania odwiedzonych zabytków
            map_view = create_map_view(page, None, user_id)

            print(f"Utworzono widok mapy dla użytkownika {user_id}")

            # Wyświetl mapę
            if map_view:
                apply_route_change_animation(page, map_view)
                page.update()
                print("Zastosowano animację i zaktualizowano stronę")
            else:
                raise Exception("Nie udało się utworzyć widoku mapy")
        except ImportError as e:
            print(f"Błąd importu modułu map_view: {e}")
            raise

        hide_loading(page, loading)

    except Exception as ex:
        # Wyświetl szczegóły błędu
        print(f"BŁĄD podczas pokazywania mapy zabytków: {ex}")
        import traceback
        traceback.print_exc()

        try:
            hide_loading(page, loading)
        except:
            pass

        show_snackbar(page, f"Wystąpił błąd: {str(ex)}", color=AppTheme.ERROR)


def create_profile_view(page):
    print("Tworzenie widoku profilu...")
    current_user_id = page.session_get("current_user_id")
    if not current_user_id:
        print("BŁĄD: Brak ID użytkownika w sesji")
        page.views.clear()
        from views.welcome_view import create_welcome_view
        page.views.append(create_welcome_view(page))
        show_snackbar(page, "Musisz być zalogowany, aby zobaczyć profil", color=AppTheme.WARNING)
        page.update()
        return None

    loading = show_loading(page, "Wczytywanie profilu...")

    try:
        user = UserRepository.get_by_id(current_user_id)
        if not user:
            print(f"Nie znaleziono użytkownika o ID: {current_user_id}")
            raise Exception(f"Nie znaleziono użytkownika o ID: {current_user_id}")

        print(f"Pobieranie odwiedzonych zabytków dla użytkownika: {user.nickname} (ID: {current_user_id})")
        visited_buildings_data = UserBuildingRepository.get_user_buildings(current_user_id)
        print(f"Znaleziono {len(visited_buildings_data) if visited_buildings_data else 0} odwiedzonych zabytków")

        hide_loading(page, loading)
    except Exception as e:
        print(f"Błąd podczas wczytywania danych profilu: {e}")
        import traceback
        traceback.print_exc()

        hide_loading(page, loading)
        show_snackbar(page, f"Błąd podczas wczytywania danych: {str(e)}", color=AppTheme.ERROR)
        return None

    header = create_header(
        f"Profil: {user.nickname}",
        with_back_button=True,
        page=page,
        with_profile=False
    )

    stats_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.EMOJI_EVENTS, size=28, color=AppTheme.PRIMARY),
                ft.Text(
                    f"Liczba odwiedzonych zabytków: {user.number_of_achievements}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                )
            ], spacing=10),
            ft.Text(
                "Odkryj więcej zabytków i zwiększ swój wynik!",
                size=14,
                color=AppTheme.TEXT_HINT,
                italic=True
            ) if user.number_of_achievements < 10 else ft.Text(
                "Gratulacje! Jesteś prawdziwym odkrywcą zabytków!",
                size=14,
                color=AppTheme.SUCCESS,
                italic=True,
                weight=ft.FontWeight.BOLD
            )
        ], spacing=5),
        padding=15,
        border_radius=10,
        bgcolor=ft.colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.colors.BLACK12,
            offset=ft.Offset(0, 2)
        ),
        margin=ft.margin.only(bottom=20)
    )

    visited_buildings_list = ft.ListView(
        spacing=10,
        padding=20,
        expand=True
    )

    if visited_buildings_data and len(visited_buildings_data) > 0:
        print("Przetwarzanie odwiedzonych zabytków...")
        for building_data in visited_buildings_data:
            try:
                building_id = building_data['building_id']
                building = BuildingRepository.get_by_id(building_id)

                if not building:
                    print(f"Nie znaleziono budynku o ID: {building_id}")
                    continue

                print(f"Dodawanie zabytku do listy: {building.name} (ID: {building.building_id})")

                has_user_photo = False
                image_src = building.image_path

                if 'user_photo_path' in building_data and building_data['user_photo_path'] is not None:
                    user_photo_path = building_data['user_photo_path']
                    print(f"Znaleziono ścieżkę do zdjęcia: {user_photo_path}")

                    if os.path.exists(user_photo_path):
                        print(f"Plik istnieje: {user_photo_path}")
                        image_src = user_photo_path
                        has_user_photo = True
                    else:
                        print(f"UWAGA: Plik nie istnieje: {user_photo_path}")

                # Funkcja obsługi kliknięcia dla każdej karty
                def on_card_click_factory(building_id):
                    def on_card_click(e):
                        try:
                            from views.monument_view import create_monument_detail_view
                            selected_building = BuildingRepository.get_by_id(building_id)
                            if selected_building:
                                loading = show_loading(page,
                                                       f"Wczytywanie szczegółów zabytku {selected_building.name}...")
                                import time
                                time.sleep(0.5)

                                detail_view = create_monument_detail_view(page, selected_building)
                                hide_loading(page, loading)

                                if detail_view:
                                    apply_route_change_animation(page, detail_view)
                                else:
                                    show_snackbar(page, "Nie udało się wczytać szczegółów zabytku",
                                                  color=AppTheme.ERROR)
                            else:
                                show_snackbar(page, "Nie znaleziono zabytku", color=AppTheme.ERROR)
                        except Exception as ex:
                            print(f"Błąd podczas przejścia do szczegółów zabytku: {ex}")
                            show_snackbar(page, f"Wystąpił błąd: {str(ex)}", color=AppTheme.ERROR)

                    return on_card_click

                card_content = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Image(
                                src=image_src,
                                width=100,
                                height=100,
                                fit=ft.ImageFit.COVER,
                                border_radius=ft.border_radius.all(10),
                            ),
                            margin=ft.margin.only(right=15),
                            border_radius=ft.border_radius.all(10),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=4,
                                color=ft.colors.BLACK12,
                                offset=ft.Offset(0, 2)
                            ),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        ),
                        ft.Column([
                            ft.Row([
                                ft.Text(
                                    building.name,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=AppTheme.TEXT_PRIMARY
                                ),
                                ft.Container(
                                    content=ft.Icon(
                                        ft.icons.VERIFIED,
                                        size=16,
                                        color=AppTheme.SUCCESS
                                    ),
                                    visible=has_user_photo,
                                    tooltip="Zweryfikowano własnym zdjęciem"
                                )
                            ], spacing=5),
                            ft.Text(
                                f"Odwiedzono: {building_data['visit_date']}",
                                size=14,
                                color=AppTheme.TEXT_SECONDARY
                            ),
                            ft.Container(
                                content=ft.Text(
                                    building.description if building.description else "Brak opisu",
                                    size=12,
                                    color=ft.colors.GREY_700,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                margin=ft.margin.only(top=5, bottom=5)
                            ),
                            ft.Row([
                                ft.Text(
                                    "✓ Własne zdjęcie",
                                    size=12,
                                    color=AppTheme.SUCCESS,
                                    italic=True,
                                    weight=ft.FontWeight.BOLD
                                ) if has_user_photo else ft.Text(
                                    "",
                                    size=0
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        "Zobacz szczegóły →",
                                        size=12,
                                        color=AppTheme.PRIMARY,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    margin=ft.margin.only(left=5 if has_user_photo else 0)
                                )
                            ], alignment=ft.MainAxisAlignment.END, spacing=5)
                        ], spacing=2, expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=15,
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
                )

                # Tworzenie karty bez on_click
                card = ft.Card(
                    content=card_content,
                    elevation=2,
                    margin=5
                )

                # Zamiast tego używamy GestureDetector do owinięcia karty
                gesture_detector = ft.GestureDetector(
                    content=card,
                    on_tap=on_card_click_factory(building.building_id)
                )

                def create_hover_handler(card_widget):
                    def hover_handler(e):
                        try:
                            if e.data == "true":
                                card_widget.elevation = 6
                                card_widget.content.bgcolor = ft.colors.BLUE_50
                                card_widget.content.scale = 1.02
                            else:
                                card_widget.elevation = 2
                                card_widget.content.bgcolor = ft.colors.WHITE
                                card_widget.content.scale = 1.0
                            card_widget.update()
                        except Exception as err:
                            print(f"Błąd w obsłudze hover: {err}")

                    return hover_handler

                card.on_hover = create_hover_handler(card)
                visited_buildings_list.controls.append(gesture_detector)
            except Exception as ex:
                print(f"Błąd podczas przetwarzania zabytku: {ex}")
                import traceback
                traceback.print_exc()
                continue
    else:
        print("Brak odwiedzonych zabytków")
        empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.TRAVEL_EXPLORE, size=64, color=AppTheme.PRIMARY),
                ft.Text(
                    "Nie odwiedziłeś jeszcze żadnych zabytków",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Rozpocznij swoją przygodę odkrywania zabytków!",
                    size=14,
                    color=AppTheme.TEXT_HINT,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                create_action_button(
                    "Odkryj zabytki",
                    icon=ft.icons.EXPLORE,
                    on_click=lambda e: go_to_continents(e),
                    color=AppTheme.PRIMARY
                )
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10),
            alignment=ft.alignment.center,
            padding=30,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.BLACK12,
                offset=ft.Offset(0, 2)
            )
        )

        visited_buildings_list.controls.append(empty_state)

    def go_back(e):
        print("Powrót z profilu do widoku kontynentów")
        try:
            from views.continent_view import create_continent_view
            continent_view = create_continent_view(page)

            # Przejdź do widoku kontynentów
            if continent_view:
                apply_route_change_animation(page, continent_view, direction="backward")
                # Usuń bieżący widok po przejściu
                if len(page.views) > 1:
                    page.views.pop(0)
                page.update()
            else:
                raise Exception("Nie udało się utworzyć widoku kontynentów")
        except Exception as ex:
            print(f"Błąd podczas powrotu: {ex}")
            import traceback
            traceback.print_exc()

            # Awaryjny powrót
            page.views.clear()
            from views.continent_view import create_continent_view
            page.views.append(create_continent_view(page))
            page.update()

    def go_to_continents(e):
        print("Przejście do widoku kontynentów")
        try:
            from views.continent_view import create_continent_view
            continent_view = create_continent_view(page)

            if continent_view:
                page.views.clear()
                page.views.append(continent_view)
                page.update()
            else:
                raise Exception("Nie udało się utworzyć widoku kontynentów")
        except Exception as ex:
            print(f"Błąd podczas przejścia do kontynentów: {ex}")
            page.views.clear()
            from views.welcome_view import create_welcome_view
            page.views.append(create_welcome_view(page))
            page.update()

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

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY
    )

    # Zmodyfikowany przycisk mapy z bezpośrednim wywołaniem
    map_button = create_action_button(
        "Pokaż mapę odwiedzonych zabytków",
        icon=ft.icons.MAP,
        on_click=lambda e: show_visited_monuments_map(e, current_user_id, page),
        color=AppTheme.PRIMARY
    )

    logout_button = create_action_button(
        "Wyloguj",
        icon=ft.icons.LOGOUT,
        on_click=logout,
        color=AppTheme.ERROR
    )

    footer_text = ft.Text(
        "Zabytkownik - Odkryj, dokumentuj i dziel się swoimi podróżami",
        size=12,
        color=AppTheme.TEXT_HINT,
        text_align=ft.TextAlign.CENTER,
        italic=True
    )

    # Układ przycisków
    buttons_row = ft.Row(
        [back_button, map_button, logout_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        wrap=True
    )

    return ft.View(
        "/profile",
        [
            header,
            ft.Container(
                content=ft.Column([
                    stats_container,

                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PLACE, color=AppTheme.PRIMARY),
                            ft.Text(
                                "Odwiedzone zabytki",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY
                            )
                        ], spacing=10),
                        margin=ft.margin.only(bottom=10)
                    ),

                    ft.Container(
                        content=visited_buildings_list,
                        height=350,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=10,
                        padding=0,
                        margin=ft.margin.only(bottom=20),
                        bgcolor=ft.colors.GREY_50
                    ),

                    buttons_row,

                    ft.Container(
                        content=footer_text,
                        margin=ft.margin.only(top=20)
                    )
                ]),
                padding=20
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )