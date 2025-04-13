import flet as ft
from database.repositories.user_repository import UserRepository
from database.repositories.user_building_repository import UserBuildingRepository
from database.repositories.building_repository import BuildingRepository
import os


def create_profile_view(page):
    current_user_id = page.session_get("current_user_id")
    if not current_user_id:
        page.views.clear()
        from views.welcome_view import create_welcome_view
        page.views.append(create_welcome_view(page))
        page.snack_bar = ft.SnackBar(ft.Text("Musisz być zalogowany, aby zobaczyć profil"))
        page.snack_bar.open = True
        page.update()
        return

    user = UserRepository.get_by_id(current_user_id)

    visited_buildings_data = UserBuildingRepository.get_user_buildings(current_user_id)
    print(f"Znaleziono {len(visited_buildings_data)} odwiedzonych zabytków dla użytkownika {current_user_id}")

    header = ft.Text(f"Profil: {user.nickname}", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900)
    stats = ft.Text(f"Liczba odwiedzonych zabytków: {user.number_of_achievements}", size=18, color=ft.colors.BLUE_700)

    visited_buildings_list = ft.ListView(
        spacing=10,
        padding=20,
        expand=True
    )

    for building_data in visited_buildings_data:
        building = BuildingRepository.get_by_id(building_data['building_id'])

        # Wypisz wszystkie dane dla tego budynku
        print(f"Dane dla budynku {building.name}:")
        for key, value in dict(building_data).items():
            print(f"  {key}: {value}")

        # Sprawdzenie czy zdjęcie użytkownika istnieje
        has_user_photo = False
        image_src = building.image_path

        # Sprawdź czy user_photo_path istnieje i nie jest None
        if building_data['user_photo_path'] is not None:
            user_photo_path = building_data['user_photo_path']
            print(f"Znaleziono ścieżkę do zdjęcia: {user_photo_path}")

            # Sprawdź czy plik rzeczywiście istnieje - użyj ścieżki bezpośrednio z bazy danych
            if os.path.exists(user_photo_path):
                print(f"Plik istnieje: {user_photo_path}")
                image_src = user_photo_path
                has_user_photo = True
            else:
                print(f"UWAGA: Plik nie istnieje: {user_photo_path}")

        print(f"Używanie obrazu: {image_src} dla zabytku {building.name}")

        card_content = ft.Container(
            content=ft.Row([
                ft.Image(
                    src=image_src,
                    width=100,
                    height=100,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(10),
                ),
                ft.Column([
                    ft.Text(building.name, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Odwiedzono: {building_data['visit_date']}", size=14),
                    ft.Text(building.description, size=12, color=ft.colors.GREY_700, max_lines=2),
                    ft.Text("✓ Własne zdjęcie" if has_user_photo else "",
                            size=12, color=ft.colors.GREEN, italic=True)
                ], spacing=5, expand=True),
            ], alignment=ft.MainAxisAlignment.START),
            padding=10,
        )

        visited_buildings_list.controls.append(
            ft.Card(
                content=card_content,
                elevation=2,
                margin=5,
            )
        )

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

    def logout(e):
        page.session_clear()
        page.views.clear()
        from views.welcome_view import create_welcome_view
        page.views.append(create_welcome_view(page))
        page.snack_bar = ft.SnackBar(ft.Text("Zostałeś wylogowany"))
        page.snack_bar.open = True
        page.update()

    logout_button = ft.ElevatedButton(
        "Wyloguj",
        on_click=logout,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_500,
        )
    )

    button_row = ft.Row(
        [back_button, logout_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    if not visited_buildings_data:
        visited_buildings_list.controls.append(
            ft.Container(
                content=ft.Text(
                    "Nie odwiedziłeś jeszcze żadnych zabytków. Rozpocznij swoją przygodę!",
                    size=16,
                    color=ft.colors.GREY_700,
                    text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.alignment.center,
                padding=20
            )
        )

    return ft.View(
        "/profile",
        [
            header,
            stats,
            ft.Divider(height=1),
            ft.Text("Odwiedzone zabytki:", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=visited_buildings_list,
                height=300,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                padding=10,
                margin=ft.margin.symmetric(vertical=10),
            ),
            button_row,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=ft.padding.all(20),
    )