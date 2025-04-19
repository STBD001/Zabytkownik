import flet as ft
import os
import tempfile
import webbrowser
import platform
import subprocess
from database.repositories.building_repository import BuildingRepository
from database.repositories.user_building_repository import UserBuildingRepository
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    apply_route_change_animation
)


def create_map_view(page, city=None, user_id=None):
    title = "Wczytywanie danych do mapy..."
    if user_id:
        title = "Wczytywanie odwiedzonych zabytków..."
    if city:
        title = f"Wczytywanie zabytków w {city}..."

    loading = show_loading(page, title)

    all_buildings = BuildingRepository.get_all()

    filtered_buildings = all_buildings

    if user_id:
        try:
            visited_data = UserBuildingRepository.get_user_buildings(user_id)

            if visited_data and len(visited_data) > 0:
                visited_building_ids = [item['building_id'] for item in visited_data]

                filtered_buildings = []
                for b in all_buildings:
                    if b.building_id in visited_building_ids:
                        filtered_buildings.append(b)
            else:
                filtered_buildings = []
        except Exception as e:
            import traceback
            traceback.print_exc()
            filtered_buildings = all_buildings

    coords = {
        1: {"lat": 51.106993, "lng": 17.077128},
        2: {"lat": 51.114854, "lng": 17.046957},
        3: {"lat": 51.099731, "lng": 17.028114}
    }

    if city and not user_id:
        buildings_to_show = [building for building in filtered_buildings
                             if city and city.lower() in (building.description or "").lower()]
    else:
        buildings_to_show = filtered_buildings

    buildings_with_coords = []
    for building in buildings_to_show:
        if building.latitude and building.longitude:
            buildings_with_coords.append(building)
        elif building.building_id in coords:
            building.latitude = coords[building.building_id]["lat"]
            building.longitude = coords[building.building_id]["lng"]
            buildings_with_coords.append(building)

    if len(buildings_with_coords) == 0:
        expected_ids = {1, 2, 3}

        for expected_id in expected_ids:
            for b in all_buildings:
                if b.building_id == expected_id:
                    b.latitude = coords[expected_id]["lat"]
                    b.longitude = coords[expected_id]["lng"]
                    buildings_with_coords.append(b)

    hide_loading(page, loading)

    def create_interactive_map():
        loading = show_loading(page, "Generowanie interaktywnej mapy...")

        markers_js = ""
        for building in buildings_with_coords:
            popup_content = f"""
            '<div style="width: 200px; text-align: center;">'+
                '<h3>{building.name}</h3>'+
                '<img src="{building.image_path}" style="max-width: 180px; max-height: 120px; margin: 5px 0;" />'+
                '<p>ID: {building.building_id}</p>'+
                '<button onclick="openDetails({building.building_id})" style="background-color: #1976D2; color: white; border: none; padding: 8px 12px; border-radius: 8px; cursor: pointer;">Zobacz szczegóły</button>'+
            '</div>'
            """

            markers_js += f"""
            var marker{building.building_id} = L.marker([{building.latitude}, {building.longitude}], {{
                icon: buildingIcon
            }}).addTo(map);

            marker{building.building_id}.bindPopup({popup_content});
            markers.push(marker{building.building_id});
            """

        if buildings_with_coords:
            avg_lat = sum(b.latitude for b in buildings_with_coords) / len(buildings_with_coords)
            avg_lng = sum(b.longitude for b in buildings_with_coords) / len(buildings_with_coords)
        else:
            avg_lat = 51.107883
            avg_lng = 17.038538

        map_title = "zabytków"
        if city:
            map_title = f"zabytków w {city}"
        if user_id:
            map_title = "odwiedzonych zabytków"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mapa zabytków - Zabytkownik</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                body, html {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    font-family: 'Roboto', Arial, sans-serif;
                }}
                #map {{
                    height: 100%;
                    width: 100%;
                }}
                .header {{
                    position: absolute;
                    top: 10px;
                    left: 50px;
                    right: 50px;
                    z-index: 1000;
                    background-color: #1976D2;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    text-align: center;
                    transition: transform 0.3s ease;
                }}
                .header:hover {{
                    transform: translateY(-3px);
                }}
                .title {{
                    margin: 0;
                    color: white;
                    font-weight: 700;
                    font-size: 1.6em;
                }}
                .subtitle {{
                    margin: 5px 0 0 0;
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.9);
                    font-weight: 300;
                }}
                .back-button {{
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    z-index: 1000;
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 50px;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    font-weight: 500;
                    font-size: 14px;
                    display: flex;
                    align-items: center;
                    transition: all 0.3s ease;
                }}
                .back-button:hover {{
                    background-color: #3949AB;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
                }}
                .back-button svg {{
                    margin-right: 8px;
                }}
                .info-panel {{
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    background-color: white;
                    padding: 15px;
                    border-radius: 10px;
                    max-width: 250px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }}
                .info-panel:hover {{
                    transform: translateY(-3px);
                }}
                .info-title {{
                    margin: 0 0 10px 0;
                    color: #1976D2;
                    font-weight: 600;
                    font-size: 1.1em;
                    border-bottom: 2px solid #1976D2;
                    padding-bottom: 5px;
                }}
                .monument-list {{
                    margin: 0;
                    padding: 0 0 0 20px;
                    font-size: 14px;
                }}
                .monument-list li {{
                    margin-bottom: 5px;
                    color: #333;
                }}
                .monument-list li:hover {{
                    color: #1976D2;
                    font-weight: 500;
                }}
                .leaflet-popup-content-wrapper {{
                    border-radius: 10px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
                    overflow: hidden;
                }}
                .leaflet-popup-content {{
                    margin: 0;
                    padding: 0;
                }}
                .leaflet-popup-content h3 {{
                    background-color: #1976D2;
                    color: white;
                    margin: 0;
                    padding: 10px;
                    font-size: 16px;
                    text-align: center;
                }}
                .leaflet-popup-content p {{
                    margin: 5px 0;
                    font-size: 12px;
                    color: #555;
                }}
                .leaflet-popup-content button {{
                    transition: all 0.3s ease;
                }}
                .leaflet-popup-content button:hover {{
                    background-color: #3949AB !important;
                    transform: translateY(-2px);
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }}
                .leaflet-container a.leaflet-popup-close-button {{
                    padding: 4px 4px 0 0;
                    color: white;
                    z-index: 999;
                }}
                .leaflet-marker-icon {{
                    transition: transform 0.2s ease;
                }}
                .leaflet-marker-icon:hover {{
                    transform: scale(1.2);
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 class="title">Mapa {map_title}</h1>
                <p class="subtitle">Kliknij marker, aby zobaczyć szczegóły zabytku</p>
            </div>

            <button class="back-button" onclick="window.close()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 12H5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 19L5 12L12 5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Zamknij mapę
            </button>

            <div class="info-panel">
                <h3 class="info-title">Dostępne zabytki:</h3>
                <ul class="monument-list">
                    {''.join(f'<li>{b.name}</li>' for b in buildings_with_coords)}
                </ul>
            </div>

            <div id="map"></div>

            <script>
                var map = L.map('map').setView([{avg_lat}, {avg_lng}], 13);
                var markers = [];

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);

                var buildingIcon = L.icon({{
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }});

                function openDetails(buildingId) {{
                    alert('Przejście do szczegółów zabytku o ID: ' + buildingId + ' nie jest możliwe bezpośrednio z przeglądarki. Wróć do aplikacji, aby zobaczyć szczegóły.');
                }}

                {markers_js}

                markers.forEach(marker => {{
                    marker.on('mouseover', function() {{
                        this._icon.style.transform = 'scale(1.2) translate(-12px, -41px)'; 
                    }});

                    marker.on('mouseout', function() {{
                        this._icon.style.transform = 'scale(1) translate(-12px, -41px)';
                    }});
                }});

                if (markers.length > 0) {{
                    var group = new L.featureGroup(markers);
                    map.fitBounds(group.getBounds().pad(0.2));
                }}
            </script>
        </body>
        </html>
        """

        fd, path = tempfile.mkstemp(suffix='.html')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html_content)

        hide_loading(page, loading)

        return path

    def go_back(e):
        try:
            os.remove(interactive_map_path)
        except Exception as e:
            pass

        apply_route_change_animation(page, page.views[-2], direction="backward")
        page.views.pop()
        page.update()

    try:
        interactive_map_path = create_interactive_map()
    except Exception as e:
        import traceback
        traceback.print_exc()
        interactive_map_path = None
        show_snackbar(page, "Nie udało się utworzyć mapy interaktywnej", color=AppTheme.ERROR)

    def open_interactive_map(e):
        if not interactive_map_path:
            show_snackbar(page, "Brak pliku mapy interaktywnej", color=AppTheme.ERROR)
            return

        try:
            loading = show_loading(page, "Otwieranie mapy w przeglądarce...")
            file_url = f"file://{interactive_map_path}"

            try:
                if platform.system() == 'Windows':
                    os.startfile(interactive_map_path)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', file_url], check=True)
                else:
                    subprocess.run(['xdg-open', file_url], check=True)
            except Exception as e:
                webbrowser.open(file_url, new=2)

            hide_loading(page, loading)
            show_snackbar(page, "Otwieranie mapy w przeglądarce...", color=AppTheme.SUCCESS)
        except Exception as ex:
            import traceback
            traceback.print_exc()

            try:
                hide_loading(page, loading)
            except:
                pass

            show_snackbar(page, f"Nie udało się otworzyć mapy: {str(ex)}", color=AppTheme.ERROR)

    map_title = f"Mapa zabytków{' - ' + city if city else ''}"
    if user_id:
        map_title = "Mapa odwiedzonych zabytków"

    header = create_header(
        map_title,
        with_back_button=True,
        page=page,
        with_profile=True
    )

    map_button = create_action_button(
        "Otwórz pełną mapę interaktywną",
        icon=ft.icons.MAP,
        on_click=open_interactive_map,
        color=AppTheme.SUCCESS
    )

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY
    )

    # Zmodyfikowana funkcja obsługi kliknięcia na zabytek
    def on_building_click(e, building_id):
        try:
            selected_building = None
            for building in buildings_with_coords:
                if building.building_id == building_id:
                    selected_building = building
                    break

            if selected_building:
                try:
                    loading = show_loading(page, f"Wczytywanie szczegółów zabytku {selected_building.name}...")

                    from views.monument_view import create_monument_detail_view

                    import time
                    time.sleep(0.5)

                    detail_view = create_monument_detail_view(page, selected_building)

                    hide_loading(page, loading)

                    if detail_view:
                        apply_route_change_animation(page, detail_view)
                    else:
                        show_snackbar(page, "Nie udało się otworzyć szczegółów zabytku", color=AppTheme.ERROR)
                except Exception as ex:
                    import traceback
                    traceback.print_exc()

                    try:
                        hide_loading(page, loading)
                    except:
                        pass

                    show_snackbar(page, f"Błąd: {str(ex)}", color=AppTheme.ERROR)
        except Exception as ex:
            show_snackbar(page, f"Błąd: {str(ex)}", color=AppTheme.ERROR)

    # Zmodyfikowana funkcja otwierania mapy dla konkretnego budynku
    def open_building_on_map(e, building_id):
        try:
            selected_building = None

            for building in buildings_with_coords:
                if building.building_id == building_id:
                    selected_building = building
                    break

            if selected_building:
                loading = show_loading(page, f"Otwieranie mapy dla {selected_building.name}...")

                url = f"https://www.openstreetmap.org/?mlat={selected_building.latitude}&mlon={selected_building.longitude}#map=17/{selected_building.latitude}/{selected_building.longitude}"
                try:
                    if platform.system() == 'Windows':
                        os.startfile(url)
                    elif platform.system() == 'Darwin':
                        subprocess.run(['open', url])
                    else:
                        subprocess.run(['xdg-open', url])

                    hide_loading(page, loading)

                    show_snackbar(page, f"Otwieranie mapy dla: {selected_building.name}", color=AppTheme.SUCCESS)
                except Exception as e:
                    hide_loading(page, loading)

                    show_snackbar(page, f"Nie udało się otworzyć mapy: {str(e)}", color=AppTheme.ERROR)
        except Exception as ex:
            show_snackbar(page, f"Błąd: {str(ex)}", color=AppTheme.ERROR)

    building_cards = []

    for building in buildings_with_coords:
        lat = building.latitude
        lng = building.longitude

        # Zaktualizowane przyciski z domknięciem
        details_button = create_action_button(
            "Szczegóły",
            icon=ft.icons.INFO,
            on_click=lambda e, bid=building.building_id: on_building_click(e, bid),
            color=AppTheme.PRIMARY,
            width=120
        )

        map_button_individual = create_action_button(
            "Na mapie",
            icon=ft.icons.PLACE,
            on_click=lambda e, bid=building.building_id: open_building_on_map(e, bid),
            color=AppTheme.SECONDARY,
            width=120
        )

        buttons_container = ft.Container(
            content=ft.Column([
                details_button,
                ft.Container(height=8),
                map_button_individual
            ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(top=8)
        )

        card_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    building.name,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    f"Lokalizacja: {lat}, {lng}",
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                    color=AppTheme.TEXT_HINT
                ),
                ft.Container(
                    content=ft.Image(
                        src=building.image_path or "assets/placeholder.jpg",
                        width=160,
                        height=120,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(8)
                    ),
                    border_radius=ft.border_radius.all(8),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=4,
                        color=ft.colors.BLACK12,
                        offset=ft.Offset(0, 2)
                    ),
                    margin=ft.margin.all(5),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                ),
                buttons_container
            ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            width=200,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        card = ft.Card(
            content=card_content,
            elevation=3,
            margin=10
        )

        def on_hover(e):
            if e.data == "true":
                e.control.elevation = 8
                e.control.content.scale = 1.03
                e.control.content.bgcolor = ft.colors.BLUE_50
            else:
                e.control.elevation = 3
                e.control.content.scale = 1.0
                e.control.content.bgcolor = ft.colors.WHITE
            e.control.update()

        card.on_hover = on_hover

        building_cards.append(card)

    if not building_cards:
        empty_message = "Nie znaleziono zabytków z danymi lokalizacji."
        if user_id:
            empty_message = "Nie masz jeszcze odwiedzonych zabytków z danymi lokalizacji."

        building_cards.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.icons.MAP_OFF,
                        size=64,
                        color=AppTheme.PRIMARY
                    ),
                    ft.Text(
                        empty_message,
                        size=16,
                        color=AppTheme.TEXT_HINT,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                padding=20,
                alignment=ft.alignment.center
            )
        )

    building_grid = ft.GridView(
        runs_count=3,
        max_extent=250,
        child_aspect_ratio=0.65,
        spacing=15,
        run_spacing=15,
        padding=20,
        controls=building_cards
    )

    title_text = f"Zabytki - {city}" if city else "Wszystkie zabytki"
    if user_id:
        title_text = "Odwiedzone zabytki"

    map_info = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.MAP, size=40, color=AppTheme.PRIMARY),
                ft.Text(
                    "Interaktywna mapa zabytków",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                )
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            ft.Text(
                "Otwórz interaktywną mapę, aby zobaczyć wszystkie zabytki i ich lokalizacje.",
                size=14,
                color=AppTheme.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(
                content=map_button,
                margin=ft.margin.symmetric(vertical=15)
            ),
            ft.Text(
                "Możesz również otworzyć każdy zabytek osobno na mapie, używając przycisku 'Na mapie' przy każdym zabytku.",
                size=12,
                color=AppTheme.TEXT_HINT,
                text_align=ft.TextAlign.CENTER,
                italic=True
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        padding=20,
        border=ft.border.all(1, ft.colors.BLUE_300),
        border_radius=15,
        margin=ft.margin.only(bottom=20),
        bgcolor=ft.colors.BLUE_50,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.colors.BLACK12,
            offset=ft.Offset(0, 2)
        ),
        animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        animate_opacity=ft.animation.Animation(800, ft.AnimationCurve.EASE_OUT),
        opacity=1  # Ustawiam od razu na 1, usuwam run_task
    )

    action_buttons = ft.Row(
        [back_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    content = ft.Container(
        content=ft.Column([
            map_info,

            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.PLACE, color=AppTheme.PRIMARY),
                    ft.Text(
                        title_text,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY
                    )
                ], spacing=10),
                margin=ft.margin.only(bottom=10)
            ),

            ft.Container(
                content=building_grid,
                height=480,
                padding=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=15,
                margin=ft.margin.only(bottom=20),
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
        padding=20,
        expand=True
    )

    return ft.View(
        "/map",
        [
            header,
            content
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0
    )