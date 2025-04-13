import flet as ft
import unicodedata
import re
from database.repositories.building_repository import BuildingRepository
from database.repositories.user_building_repository import UserBuildingRepository
import os
import time
from datetime import datetime


def create_monument_view(page, city):
    all_buildings = BuildingRepository.get_all()

    city_monuments = {
        "Wrocław": [1, 2, 3]
    }

    monument_ids = city_monuments.get(city, [])
    monuments = [building for building in all_buildings if building.building_id in monument_ids]
    if not monuments:
        monuments = [building for building in all_buildings if city.lower() in building.description.lower()]

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
                        ft.Text(monument.name, size=16),
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

    def go_back(e):
        page.views.pop()
        page.update()

    def mark_as_visited(e):
        current_user_id = page.session_get("current_user_id")
        if current_user_id:
            print(f"Dodawanie wizyty dla użytkownika {current_user_id} do zabytku {monument.building_id}")
            try:
                UserBuildingRepository.add_visit(current_user_id, monument.building_id)
                visit_button.text = "✓ Zabytek odwiedzony!"
                visit_button.bgcolor = ft.Colors.GREEN_900
                visit_button.disabled = True
                unvisit_button.visible = True
                page.snack_bar = ft.SnackBar(ft.Text("Zabytek został oznaczony jako odwiedzony!"))
                page.snack_bar.open = True
                page.update()
            except Exception as e:
                print(f"Błąd podczas oznaczania zabytku jako odwiedzonego: {e}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Błąd podczas oznaczania zabytku: {str(e)}"))
                page.snack_bar.open = True
                page.update()
        else:
            print("Brak current_user_id w sesji")
            page.snack_bar = ft.SnackBar(ft.Text("Musisz być zalogowany, aby oznaczać zabytki jako odwiedzone"))
            page.snack_bar.open = True
            page.update()

    def unmark_as_visited(e):
        current_user_id = page.session_get("current_user_id")
        if current_user_id:
            success = UserBuildingRepository.remove_visit(current_user_id, monument.building_id)
            if success:
                visit_button.text = "Oznacz jako odwiedzony"
                visit_button.bgcolor = ft.Colors.GREEN_700
                visit_button.disabled = False
                unvisit_button.visible = False
                page.snack_bar = ft.SnackBar(ft.Text("Usunięto oznaczenie zabytku jako odwiedzonego"))
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Wystąpił błąd podczas usuwania oznaczenia"))
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Musisz być zalogowany, aby modyfikować odwiedzone zabytki"))
            page.snack_bar.open = True
            page.update()

    def on_capture_photo(e):
        if not current_user_id:
            page.snack_bar = ft.SnackBar(ft.Text("Musisz być zalogowany, aby weryfikować zabytki"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            from views.photo_capture_view import create_photo_capture_view
            page.views.append(create_photo_capture_view(page, monument))
            page.update()
        except ImportError:
            page.snack_bar = ft.SnackBar(ft.Text("Funkcja weryfikacji przez zdjęcie jest w trakcie implementacji"))
            page.snack_bar.open = True
            page.update()

    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        )
    )

    visit_button = ft.ElevatedButton(
        text="✓ Zabytek odwiedzony!" if has_visited else "Oznacz jako odwiedzony",
        on_click=mark_as_visited if not has_visited else None,
        disabled=has_visited,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_900 if has_visited else ft.Colors.GREEN_700,
        )
    )

    unvisit_button = ft.ElevatedButton(
        text="Cofnij oznaczenie",
        on_click=unmark_as_visited,
        visible=has_visited,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_400,
        )
    )

    verify_button = ft.ElevatedButton(
        text="Zweryfikuj przez zdjęcie",
        on_click=on_capture_photo,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PURPLE_700,
        ),
        icon=ft.icons.CAMERA_ALT,
    )

    map_url = f"https://www.google.com/maps/search/?api=1&query={monument.name.replace(' ', '+')}"

    normalized_name = normalize_filename(monument.name)
    map_files = {
        1: "hala_stulecia_map.jpg",
        2: "katedra_map.jpg",
        3: "sky_tower_map.jpg"
    }
    monument_addresses = {
        1: "ul. Wystawowa 1, 51-618 Wrocław",
        2: "pl. Katedralny 18, 50-329 Wrocław",
        3: "ul. Powstańców Śląskich 95, 53-332 Wrocław"
    }
    monument_address = monument_addresses.get(monument.building_id, "")
    map_filename = map_files.get(monument.building_id, f"{normalized_name}_map.jpg")
    map_image_path = f"assets/{map_filename}"
    print(f"Próba załadowania mapy z: {map_image_path}")

    map_button = ft.ElevatedButton(
        "Zobacz na Google Maps",
        on_click=lambda e: page.launch_url(map_url),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
        )
    )

    address_text = ft.Text(
        monument_address,
        size=14,
        color=ft.colors.GREY_700,
        text_align=ft.TextAlign.CENTER,
    )

    action_buttons = ft.Row(
        [
            visit_button,
            unvisit_button,
            verify_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    return ft.View(
        f"/monuments/{monument.building_id}",
        [
            ft.Text(monument.name, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Image(
                                    src=monument.image_path,
                                    width=400,
                                    height=300,
                                    fit=ft.ImageFit.COVER,
                                ),
                                border_radius=10,
                                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=5,
                                    color=ft.colors.BLACK38,
                                ),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    monument.description,
                                    size=16,
                                    text_align=ft.TextAlign.JUSTIFY,
                                ),
                                margin=ft.margin.only(top=15),
                                padding=10,
                            ),
                        ],
                        width=400,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),

                    ft.VerticalDivider(width=40),
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Image(
                                    src=map_image_path,
                                    width=400,
                                    height=300,
                                    fit=ft.ImageFit.COVER,
                                ),
                                border_radius=10,
                                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=5,
                                    color=ft.colors.BLACK38,
                                ),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        map_button,
                                        address_text,
                                    ],
                                    spacing=5,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                margin=ft.margin.only(top=15),
                            ),
                        ],
                        width=400,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),

            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            action_buttons,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            back_button,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
    )