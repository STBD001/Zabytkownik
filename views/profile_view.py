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
    try:
        loading = show_loading(page, "Wczytywanie mapy zabytków...")

        import time
        time.sleep(0.5)

        from views.map_view import create_map_view
        map_view = create_map_view(page, None)

        hide_loading(page, loading)

        if map_view:
            apply_route_change_animation(page, map_view)
        else:
            show_snackbar(page, "Nie udało się utworzyć widoku mapy", color=AppTheme.ERROR)
    except Exception as ex:
        hide_loading(page, loading)
        show_snackbar(page, f"Wystąpił błąd: {str(ex)}", color=AppTheme.ERROR)


def create_profile_view(page):
    current_user_id = page.session_get("current_user_id")
    if not current_user_id:
        page.views.clear()
        from views.welcome_view import create_welcome_view
        page.views.append(create_welcome_view(page))
        show_snackbar(page, "Musisz być zalogowany, aby zobaczyć profil", color=AppTheme.WARNING)
        page.update()
        return

    loading = show_loading(page, "Wczytywanie profilu...")

    try:
        user = UserRepository.get_by_id(current_user_id)
        visited_buildings_data = UserBuildingRepository.get_user_buildings(current_user_id)

        hide_loading(page, loading)

        print(f"Znaleziono {len(visited_buildings_data)} odwiedzonych zabytków dla użytkownika {current_user_id}")
    except Exception as e:
        hide_loading(page, loading)
        show_snackbar(page, f"Błąd podczas wczytywania danych: {str(e)}", color=AppTheme.ERROR)
        return

    header = create_header(
        f"Profil: {user.nickname}",
        with_back_button=True,
        page=page
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

    if visited_buildings_data:
        for building_data in visited_buildings_data:
            building = BuildingRepository.get_by_id(building_data['building_id'])

            print(f"Dane dla budynku {building.name}:")
            for key, value in dict(building_data).items():
                print(f"  {key}: {value}")

            has_user_photo = False
            image_src = building.image_path

            if building_data['user_photo_path'] is not None:
                user_photo_path = building_data['user_photo_path']
                print(f"Znaleziono ścieżkę do zdjęcia: {user_photo_path}")

                if os.path.exists(user_photo_path):
                    print(f"Plik istnieje: {user_photo_path}")
                    image_src = user_photo_path
                    has_user_photo = True
                else:
                    print(f"UWAGA: Plik nie istnieje: {user_photo_path}")

            print(f"Używanie obrazu: {image_src} dla zabytku {building.name}")

            def on_card_click_factory(building_id):
                def on_card_click(e):
                    try:
                        from views.monument_view import create_monument_detail_view
                        selected_building = BuildingRepository.get_by_id(building_id)
                        if selected_building:
                            loading = show_loading(page, f"Wczytywanie szczegółów zabytku {selected_building.name}...")
                            import time
                            time.sleep(0.5)

                            detail_view = create_monument_detail_view(page, selected_building)
                            hide_loading(page, loading)

                            if detail_view:
                                apply_route_change_animation(page, detail_view)
                            else:
                                show_snackbar(page, "Nie udało się wczytać szczegółów zabytku", color=AppTheme.ERROR)
                        else:
                            show_snackbar(page, "Nie znaleziono zabytku", color=AppTheme.ERROR)
                    except Exception as ex:
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
                                building.description,
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

            card = ft.Card(
                content=card_content,
                elevation=2,
                margin=5,
                on_click=on_card_click_factory(building.building_id)
            )

            def on_hover(e):
                if e.data == "true":
                    e.control.elevation = 6
                    e.control.content.bgcolor = ft.colors.BLUE_50
                    e.control.content.scale = 1.02
                else:
                    e.control.elevation = 2
                    e.control.content.bgcolor = ft.colors.WHITE
                    e.control.content.scale = 1.0
                e.control.update()

            card.on_hover = on_hover

            visited_buildings_list.controls.append(card)
    else:
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
        from views.continent_view import create_continent_view
        page.views.clear()
        page.views.append(create_continent_view(page))
        page.update()

    def go_to_continents(e):
        from views.continent_view import create_continent_view
        page.views.clear()
        page.views.append(create_continent_view(page))
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