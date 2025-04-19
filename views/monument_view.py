import flet as ft
import unicodedata
import re
from database.repositories.building_repository import BuildingRepository
from database.repositories.user_building_repository import UserBuildingRepository
import os
import time
from datetime import datetime
from ui_helpers import (
    AppTheme, create_header, create_monument_card, create_action_button,
    show_loading, hide_loading, show_snackbar, show_confirmation_dialog,
    apply_route_change_animation, create_responsive_grid
)


def create_monument_view(page, city):
    loading = show_loading(page, f"Wczytywanie zabytków miasta {city}...")

    all_buildings = BuildingRepository.get_all()

    print(f"Wszystkie dostępne zabytki w bazie ({len(all_buildings)}):")
    for b in all_buildings:
        print(f" - ID: {b.building_id}, Nazwa: {b.name}")

    city_monuments = {
        "Wrocław": [1, 2, 3]
    }

    monument_ids = city_monuments.get(city, [])
    print(f"Identyfikatory zabytków dla miasta {city}: {monument_ids}")

    monuments = []
    for building in all_buildings:
        if building.building_id in monument_ids:
            monuments.append(building)
            print(f"Dodano zabytek {building.name} (ID: {building.building_id})")

    if not monuments:
        print(f"Nie znaleziono zabytków po ID, próba znalezienia po opisie...")
        monuments = [building for building in all_buildings if city.lower() in building.description.lower()]

    print(f"Znalezione zabytki dla miasta {city} ({len(monuments)}):")
    for monument in monuments:
        print(f" - ID: {monument.building_id}, Nazwa: {monument.name}")

    hide_loading(page, loading)

    def on_monuments_click(e):
        selected_monument = e.control.data
        for monument in monuments:
            if monument.building_id == selected_monument:
                loading = show_loading(page, f"Wczytywanie szczegółów zabytku {monument.name}...")
                time.sleep(0.5)
                hide_loading(page, loading)

                detail_view = create_monument_detail_view(page, monument)
                apply_route_change_animation(page, detail_view)
                break

    def go_back(e):
        apply_route_change_animation(page, page.views[-2], direction="backward")
        page.views.pop()
        page.update()

    def on_show_map(e):
        try:
            loading = show_loading(page, "Wczytywanie mapy zabytków...")
            time.sleep(0.5)  # Krótkie opóźnienie dla efektu

            from views.map_view import create_map_view
            map_view = create_map_view(page, city)

            if map_view:
                hide_loading(page, loading)
                apply_route_change_animation(page, map_view)
            else:
                hide_loading(page, loading)
                show_snackbar(page, "Nie udało się utworzyć widoku mapy", color=AppTheme.ERROR)
        except Exception as ex:
            print(f"Błąd podczas tworzenia widoku mapy: {ex}")
            hide_loading(page, loading)
            show_snackbar(page, f"Błąd: {str(ex)}", color=AppTheme.ERROR)

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY
    )

    map_button = create_action_button(
        "Pokaż mapę zabytków",
        icon=ft.icons.MAP,
        on_click=on_show_map,
        color=AppTheme.PRIMARY
    )

    monument_cards = []
    for monument in monuments:
        def on_click_factory(monument_id):
            return lambda e: on_monuments_click(
                type('obj', (object,), {'control': type('obj', (object,), {'data': monument_id})}))

        card = create_monument_card(
            monument,
            on_click=on_click_factory(monument.building_id)
        )
        monument_cards.append(card)

    if not monument_cards:
        monument_cards.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.INFO, size=48, color=AppTheme.PRIMARY),
                    ft.Text(
                        "Nie znaleziono zabytków dla tego miasta",
                        size=16,
                        color=AppTheme.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(0, 2)
                )
            )
        )

    monument_grid = create_responsive_grid(monument_cards, columns=3)
    header = create_header(
        f"Zabytki w {city}",
        with_back_button=True,
        page=page,
        with_profile=True
    )

    action_buttons = ft.Container(
        content=ft.Row(
            [map_button, back_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        padding=ft.padding.symmetric(vertical=20)
    )

    return ft.View(
        "/monuments",
        [
            header,
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            f"Odkryj zabytki {city}",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        margin=ft.margin.only(bottom=10)
                    ),
                    ft.Container(
                        content=monument_grid,
                        padding=10,
                        height=400,
                        border_radius=10,
                        bgcolor=ft.colors.WHITE,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=5,
                            color=ft.colors.BLACK12,
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    action_buttons
                ]),
                padding=20
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )


def normalize_filename(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = re.sub(r'[^a-zA-Z0-9_]', '', text.replace(' ', '_'))
    return text.lower()


def create_monument_detail_view(page, monument):
    current_user_id = page.session_get("current_user_id")
    has_visited = False
    if current_user_id:
        visit = UserBuildingRepository.check_visit(current_user_id, monument.building_id)
        has_visited = visit is not None

    visit_button = create_action_button(
        text="✓ Zabytek odwiedzony!" if has_visited else "Oznacz jako odwiedzony",
        icon=ft.icons.CHECK_CIRCLE if has_visited else ft.icons.ADD_CIRCLE,
        color=AppTheme.SUCCESS,
        on_click=None
    )

    visit_button.disabled = has_visited

    unvisit_button = create_action_button(
        text="Cofnij oznaczenie",
        icon=ft.icons.REMOVE_CIRCLE,
        color=AppTheme.ERROR,
        on_click=None
    )

    unvisit_button.visible = has_visited

    def go_back(e):
        apply_route_change_animation(page, page.views[-2], direction="backward")
        page.views.pop()
        page.update()

    def mark_as_visited(e):
        nonlocal has_visited
        current_user_id = page.session_get("current_user_id")
        if current_user_id:
            loading = show_loading(page, "Oznaczanie zabytku jako odwiedzony...")

            try:
                time.sleep(0.5)
                UserBuildingRepository.add_visit(current_user_id, monument.building_id)

                hide_loading(page, loading)

                visit_button.text = "✓ Zabytek odwiedzony!"
                visit_button.icon = ft.icons.CHECK_CIRCLE
                visit_button.disabled = True
                unvisit_button.visible = True

                show_snackbar(page, "Zabytek został oznaczony jako odwiedzony!", color=AppTheme.SUCCESS)
                has_visited = True
                page.update()
            except Exception as e:
                hide_loading(page, loading)
                print(f"Błąd podczas oznaczania zabytku jako odwiedzonego: {e}")
                show_snackbar(page, f"Błąd podczas oznaczania zabytku: {str(e)}", color=AppTheme.ERROR)
        else:
            show_snackbar(page, "Musisz być zalogowany, aby oznaczać zabytki jako odwiedzone", color=AppTheme.WARNING)

    visit_button.on_click = mark_as_visited if not has_visited else None

    def unmark_as_visited(e):
        nonlocal has_visited
        current_user_id = page.session_get("current_user_id")
        if current_user_id:
            def confirm_unmark():
                loading = show_loading(page, "Usuwanie oznaczenia...")

                try:
                    time.sleep(0.5)
                    success = UserBuildingRepository.remove_visit(current_user_id, monument.building_id)

                    hide_loading(page, loading)

                    if success:
                        visit_button.text = "Oznacz jako odwiedzony"
                        visit_button.icon = ft.icons.ADD_CIRCLE
                        visit_button.disabled = False
                        visit_button.on_click = mark_as_visited
                        unvisit_button.visible = False

                        show_snackbar(page, "Usunięto oznaczenie zabytku jako odwiedzonego", color=AppTheme.SUCCESS)
                        has_visited = False
                        page.update()
                    else:
                        show_snackbar(page, "Wystąpił błąd podczas usuwania oznaczenia", color=AppTheme.ERROR)
                except Exception as e:
                    hide_loading(page, loading)
                    show_snackbar(page, f"Błąd: {str(e)}", color=AppTheme.ERROR)

            show_confirmation_dialog(
                page,
                "Usuwanie oznaczenia",
                "Czy na pewno chcesz usunąć oznaczenie zabytku jako odwiedzonego?",
                confirm_unmark
            )
        else:
            show_snackbar(page, "Musisz być zalogowany, aby modyfikować odwiedzone zabytki", color=AppTheme.WARNING)

    unvisit_button.on_click = unmark_as_visited

    def on_capture_photo(e):
        if not current_user_id:
            show_snackbar(page, "Musisz być zalogowany, aby weryfikować zabytki", color=AppTheme.WARNING)
            return

        try:
            loading = show_loading(page, "Przygotowywanie aparatu...")
            time.sleep(0.5)  # Opóźnienie dla efektu

            from views.photo_capture_view import create_photo_capture_view
            photo_view = create_photo_capture_view(page, monument)

            if photo_view:
                hide_loading(page, loading)
                apply_route_change_animation(page, photo_view)
            else:
                hide_loading(page, loading)
                raise ImportError("Nie udało się utworzyć widoku zdjęcia")
        except ImportError as ex:
            hide_loading(page, loading)
            show_snackbar(page, f"Funkcja weryfikacji przez zdjęcie jest w trakcie implementacji: {str(ex)}",
                          color=AppTheme.WARNING)
        except Exception as ex:
            hide_loading(page, loading)
            show_snackbar(page, f"Wystąpił błąd: {str(ex)}", color=AppTheme.ERROR)

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY
    )

    verify_button = create_action_button(
        text="Zweryfikuj przez zdjęcie",
        icon=ft.icons.CAMERA_ALT,
        on_click=on_capture_photo,
        color=AppTheme.PRIMARY
    )

    def on_show_map(e):
        try:
            loading = show_loading(page, "Wczytywanie mapy...")
            time.sleep(0.5)

            from views.map_view import create_map_view

            city = None
            if "Wrocław" in monument.description:
                city = "Wrocław"

            map_view = create_map_view(page, city)

            if map_view:
                hide_loading(page, loading)
                apply_route_change_animation(page, map_view)
            else:
                hide_loading(page, loading)
                show_snackbar(page, "Nie udało się utworzyć widoku mapy", color=AppTheme.ERROR)
        except Exception as ex:
            hide_loading(page, loading)
            print(f"Błąd podczas tworzenia widoku mapy: {ex}")
            show_snackbar(page, f"Błąd: {str(ex)}", color=AppTheme.ERROR)

    show_on_map_button = create_action_button(
        "Pokaż na mapie",
        icon=ft.icons.PLACE,
        on_click=on_show_map,
        color=AppTheme.SECONDARY
    )

    monument_addresses = {
        1: "ul. Wystawowa 1, 51-618 Wrocław",
        2: "pl. Katedralny 18, 50-329 Wrocław",
        3: "ul. Powstańców Śląskich 95, 53-332 Wrocław"
    }
    monument_address = monument_addresses.get(monument.building_id, "")

    # Google Maps URL
    map_url = f"https://www.google.com/maps/search/?api=1&query={monument.name.replace(' ', '+')}"

    map_button = create_action_button(
        "Zobacz na Google Maps",
        icon=ft.icons.MAP,
        on_click=lambda e: page.launch_url(map_url),
        color=AppTheme.PRIMARY
    )

    address_text = ft.Text(
        monument_address,
        size=14,
        color=ft.colors.GREY_700,
        text_align=ft.TextAlign.CENTER,
    )

    header = create_header(
        monument.name,
        with_back_button=True,
        page=page,
        with_profile=True
    )

    description_container = ft.Container(
        content=ft.Text(
            monument.description,
            size=16,
            text_align=ft.TextAlign.JUSTIFY,
        ),
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

    action_buttons = ft.Container(
        content=ft.Row(
            [
                visit_button,
                unvisit_button,
                verify_button,
                show_on_map_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            wrap=True
        ),
        margin=ft.margin.symmetric(vertical=20)
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Opis",
                icon=ft.icons.DESCRIPTION,
                content=description_container
            ),
            ft.Tab(
                text="Lokalizacja",
                icon=ft.icons.PLACE,
                content=ft.Container(
                    content=ft.Column([
                        ft.Image(
                            src=f"assets/{monument.building_id}_map.jpg",
                            width=400,
                            height=300,
                            fit=ft.ImageFit.COVER,
                            border_radius=ft.border_radius.all(10)
                        ),
                        ft.Container(
                            content=address_text,
                            margin=ft.margin.only(top=10, bottom=10)
                        ),
                        map_button
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5
                    ),
                    padding=15,
                    margin=ft.margin.only(top=10),
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=5,
                        color=ft.colors.BLACK12,
                        offset=ft.Offset(0, 2)
                    )
                )
            )
        ],
        expand=1
    )

    content = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Image(
                    src=monument.image_path,
                    width=500,
                    height=300,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(10)
                ),
                margin=ft.margin.only(bottom=20),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.colors.BLACK38,
                    offset=ft.Offset(0, 4)
                ),
                border_radius=ft.border_radius.all(10),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS
            ),

            tabs,
            action_buttons,
            back_button
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        ),
        padding=20,
        width=600
    )

    return ft.View(
        f"/monuments/{monument.building_id}",
        [
            header,
            content
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )