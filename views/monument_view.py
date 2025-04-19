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
            time.sleep(0.5)

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
        on_click=None if has_visited else lambda e: mark_as_visited(e)
    )

    visit_button.disabled = has_visited

    unvisit_button = create_action_button(
        text="Cofnij oznaczenie",
        icon=ft.icons.REMOVE_CIRCLE,
        color=AppTheme.ERROR,
        on_click=lambda e: unmark_as_visited(e)
    )

    unvisit_button.visible = has_visited

    def go_back(e):
        try:
            if len(page.views) >= 2:
                previous_view = page.views[-2]
                page.views.pop()
                if previous_view:
                    apply_route_change_animation(page, previous_view, direction="backward")
                    page.update()
                else:
                    from views.continent_view import create_continent_view
                    page.views.clear()
                    page.views.append(create_continent_view(page))
                    page.update()
            else:
                from views.continent_view import create_continent_view
                page.views.clear()
                page.views.append(create_continent_view(page))
                page.update()
        except Exception as ex:
            print(f"Błąd podczas powrotu: {ex}")
            import traceback
            traceback.print_exc()
            from views.continent_view import create_continent_view
            page.views.clear()
            page.views.append(create_continent_view(page))
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

    def on_file_selected(e):
        nonlocal has_visited

        if e.files and len(e.files) > 0:
            selected_file = e.files[0]
            file_path = selected_file.path

            loading = show_loading(page, "Weryfikowanie zdjęcia...")

            try:
                if not file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    hide_loading(page, loading)
                    show_snackbar(page, "Proszę wybrać plik obrazu (JPG, JPEG lub PNG)", color=AppTheme.WARNING)
                    return

                print(f"Wybrane zdjęcie: {file_path}")

                try:
                    from ai.ImageAnalyzer import ImageAnalyzer

                    analyzer = ImageAnalyzer(
                        model_name='resnet50',
                        similarity_threshold=0.5,
                        reference_dir='assets/references'
                    )

                    print(f"Weryfikacja zdjęcia dla zabytku ID: {monument.building_id}")
                    verification_result = analyzer.verify_monument(file_path, monument.building_id)
                    print(f"Wynik weryfikacji: {verification_result}")

                    if verification_result['success']:
                        confidence = int(verification_result['confidence'] * 100)

                        result = UserBuildingRepository.save_user_photo(current_user_id, monument.building_id,
                                                                        file_path)

                        if result:
                            if not has_visited:
                                UserBuildingRepository.add_visit(current_user_id, monument.building_id)
                                has_visited = True
                                visit_button.text = "✓ Zabytek odwiedzony!"
                                visit_button.icon = ft.icons.CHECK_CIRCLE
                                visit_button.disabled = True
                                unvisit_button.visible = True

                            hide_loading(page, loading)
                            show_snackbar(page, f"Zabytek zweryfikowany pomyślnie! Pewność: {confidence}%",
                                          color=AppTheme.SUCCESS)

                            def go_to_profile():
                                from views.profile_view import create_profile_view
                                profile_view = create_profile_view(page)
                                apply_route_change_animation(page, profile_view)

                            show_confirmation_dialog(
                                page,
                                "Weryfikacja zakończona pomyślnie",
                                f"Zdjęcie zostało zweryfikowane (pewność: {confidence}%) i zapisane. Czy chcesz przejść do profilu, aby zobaczyć swoje zdjęcie zabytku?",
                                go_to_profile
                            )
                        else:
                            hide_loading(page, loading)
                            show_snackbar(page, "Wystąpił błąd podczas zapisywania zdjęcia", color=AppTheme.ERROR)
                    else:
                        confidence = int(verification_result['confidence'] * 100)
                        hide_loading(page, loading)
                        show_snackbar(
                            page,
                            f"Zdjęcie nie przedstawia tego zabytku (pewność: {confidence}%). Spróbuj innego zdjęcia.",
                            color=AppTheme.ERROR
                        )
                except ImportError:
                    print("ImageAnalyzer niedostępny. Zapisuję zdjęcie bez weryfikacji.")
                    result = UserBuildingRepository.save_user_photo(current_user_id, monument.building_id, file_path)

                    if result:
                        if not has_visited:
                            UserBuildingRepository.add_visit(current_user_id, monument.building_id)
                            has_visited = True
                            visit_button.text = "✓ Zabytek odwiedzony!"
                            visit_button.icon = ft.icons.CHECK_CIRCLE
                            visit_button.disabled = True
                            unvisit_button.visible = True

                        hide_loading(page, loading)
                        show_snackbar(page, "Zabytek oznaczony jako odwiedzony!", color=AppTheme.SUCCESS)

                        def go_to_profile():
                            from views.profile_view import create_profile_view
                            profile_view = create_profile_view(page)
                            apply_route_change_animation(page, profile_view)

                        show_confirmation_dialog(
                            page,
                            "Zdjęcie zapisane",
                            "Zdjęcie zostało zapisane bez weryfikacji. Czy chcesz przejść do profilu, aby zobaczyć swoje zdjęcie zabytku?",
                            go_to_profile
                        )
                    else:
                        hide_loading(page, loading)
                        show_snackbar(page, "Wystąpił błąd podczas zapisywania zdjęcia", color=AppTheme.ERROR)

            except Exception as ex:
                hide_loading(page, loading)
                print(f"Błąd podczas weryfikacji zdjęcia: {ex}")
                import traceback
                traceback.print_exc()
                show_snackbar(page, f"Błąd: {str(ex)}", color=AppTheme.ERROR)
        else:
            pass

    def on_capture_photo(e):
        if not current_user_id:
            show_snackbar(page, "Musisz być zalogowany, aby weryfikować zabytki", color=AppTheme.WARNING)
            return

        file_picker = ft.FilePicker(on_result=on_file_selected)
        page.overlay.append(file_picker)
        page.update()

        file_picker.pick_files(
            dialog_title="Wybierz zdjęcie zabytku",
            allowed_extensions=["jpg", "jpeg", "png"],
            allow_multiple=False
        )

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY
    )

    verify_button = create_action_button(
        text="Weryfikuj przez zdjęcie",
        icon=ft.icons.PHOTO_LIBRARY,
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

    monument_descriptions = {
        1: "Hala Stulecia (dawniej Hala Ludowa) to historyczny obiekt widowiskowo-sportowy położony we Wrocławiu. Została zaprojektowana przez Maksa Berga i wybudowana w latach 1911-1913. W 2006 roku została wpisana na listę światowego dziedzictwa UNESCO jako jedno z największych dzieł architektury XX wieku.",
        2: "Archikatedra św. Jana Chrzciciela we Wrocławiu - gotycka katedra, jeden z najważniejszych zabytków architektury gotyckiej w Polsce. Zbudowana w latach 1244-1341 jako trójnawowa bazylika z bazylikowym transeptem. Jest to druga pod względem wysokości świątynia w Polsce.",
        3: "Sky Tower - najwyższy budynek we Wrocławiu i jeden z najwyższych w Polsce. Ten wieżowiec ma 212 metrów wysokości i 50 pięter. Został zaprojektowany przez pracownię architektoniczną FOLD i oddany do użytku w 2012 roku."
    }

    monument_address = monument_addresses.get(monument.building_id, "Adres niedostępny")

    if not monument.description or monument.description.strip() == "":
        monument.description = monument_descriptions.get(monument.building_id, "Brak opisu zabytku.")

    map_url = f"https://www.google.com/maps/search/?api=1&query={monument_address.replace(' ', '+')}"

    map_button = create_action_button(
        "Zobacz na Google Maps",
        icon=ft.icons.MAP,
        on_click=lambda e: page.launch_url(map_url),
        color=AppTheme.PRIMARY
    )

    address_text = ft.Text(
        monument_address,
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.GREY_800,
        text_align=ft.TextAlign.CENTER,
    )

    header = create_header(
        monument.name,
        with_back_button=True,
        page=page,
        with_profile=True
    )

    description_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.DESCRIPTION, size=24, color=AppTheme.PRIMARY),
                ft.Text(
                    "Opis",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                )
            ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10),
            ft.Container(
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
                margin=ft.margin.only(top=10),
                width=500
            )
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        margin=ft.margin.only(bottom=20),
        alignment=ft.alignment.center,
        width=page.width
    )

    location_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.PLACE, size=24, color=AppTheme.PRIMARY),
                ft.Text(
                    "Lokalizacja",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                )
            ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10),
            ft.Container(
                content=ft.Column([
                    address_text,
                    map_button
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=ft.padding.symmetric(vertical=15, horizontal=10),
                margin=ft.margin.only(top=5),
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(0, 2)
                ),
                alignment=ft.alignment.center,
                width=500
            )
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),
        margin=ft.margin.only(bottom=20),
        alignment=ft.alignment.center,
        width=page.width
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
        margin=ft.margin.symmetric(vertical=15),
        width=page.width,
        alignment=ft.alignment.center
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
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.alignment.center
            ),

            description_section,
            location_section,

            action_buttons,
            ft.Container(
                content=back_button,
                alignment=ft.alignment.center,
                width=page.width
            )
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=ft.padding.only(left=20, right=20, bottom=20),
        alignment=ft.alignment.center
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