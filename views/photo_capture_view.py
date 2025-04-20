import flet as ft
import os
import time
from datetime import datetime
from database.repositories.user_building_repository import UserBuildingRepository
from ai.ImageAnalyzer import ImageAnalyzer
from setup_reference_dirs import setup_reference_directories

def analyze_image_with_ai(image_path, monument_id):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Plik {image_path} nie istnieje")

        print(f"Analiza obrazu: {image_path} dla ID: {monument_id}")
        setup_reference_directories()
        analyzer = ImageAnalyzer(
            model_name='efficientnet_b0',
            similarity_threshold=0.7,
            reference_dir='assets/references'
        )
        result = analyzer.verify_monument(image_path, monument_id)
        print(f"Wynik analizy z ImageAnalyzer: {result}")
        return result
    except Exception as e:
        print(f"Błąd analizy: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "confidence": 0,
            "message": f"Błąd analizy: {str(e)}"
        }

def create_photo_capture_view(page, monument):
    # Inicjalizacja snack_bar
    page.snack_bar = ft.SnackBar(content=ft.Text(""), open=False)

    image_path_container = ft.Container(height=0, width=0, visible=False)
    image_preview = ft.Image(
        src=None,
        width=400,
        height=300,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10,
        visible=False,
    )
    progress_ring = ft.ProgressRing(width=40, height=40, stroke_width=4, visible=False)
    progress_text = ft.Text("", visible=False)

    # Fallbackowy komunikat w GUI dla nieudanych weryfikacji
    fallback_message = ft.Text(
        "",
        size=14,
        color=ft.colors.RED_700,
        visible=False,
        text_align=ft.TextAlign.CENTER
    )

    result_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [ft.Icon(ft.icons.CHECK_CIRCLE, size=40, visible=False),
                     ft.Text("", size=18, visible=False)],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("", size=14, visible=False),
                ft.ProgressBar(width=400, visible=False)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        ),
        padding=10,
        border_radius=10,
        visible=False
    )

    result_icon = result_container.content.controls[0].controls[0]
    result_text = result_container.content.controls[0].controls[1]
    confidence_text = result_container.content.controls[2]
    confidence_bar = result_container.content.controls[3]

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    photo_status = ft.Container(
        content=ft.Text(
            "Wybierz lub zrób zdjęcie, aby zweryfikować zabytek",
            size=14,
            color=ft.colors.BLUE_700,
            italic=True,
            text_align=ft.TextAlign.CENTER
        ),
        padding=10,
        visible=True
    )

    def show_processing_ui():
        progress_ring.visible = True
        progress_text.value = "Analizowanie zdjęcia..."
        progress_text.visible = True
        result_container.visible = False
        fallback_message.visible = False
        upload_button.disabled = True
        camera_button.disabled = True
        photo_status.visible = False
        page.update()

    def show_result(result, photo_path=None):
        print(f"Wejście do show_result z wynikiem: {result}")
        success = result.get("success", False)
        message = result.get("message", "Nieznany wynik analizy")
        confidence = result.get("confidence", 0)

        print(f"Parametry w show_result: success={success}, message={message}, confidence={confidence}")

        progress_ring.visible = False
        progress_text.visible = False

        result_text.value = message
        result_text.color = ft.colors.GREEN_700 if success else ft.colors.RED_700
        result_text.visible = True

        result_icon.name = ft.icons.CHECK_CIRCLE if success else ft.icons.ERROR
        result_icon.color = ft.colors.GREEN_700 if success else ft.colors.RED_700
        result_icon.visible = True

        confidence_text.value = f"Pewność: {int(confidence * 100)}%"
        confidence_text.visible = True

        confidence_bar.value = confidence
        confidence_bar.color = _get_confidence_color(confidence)
        confidence_bar.visible = True

        result_container.visible = True
        result_container.bgcolor = ft.colors.GREEN_50 if success else ft.colors.RED_50
        result_container.border = ft.border.all(2, ft.colors.GREEN_200 if success else ft.colors.RED_200)

        upload_button.disabled = False
        camera_button.disabled = False

        override_button.visible = not success and confidence > 0.4

        if success and page.session_get("current_user_id") and photo_path:
            user_id = page.session_get("current_user_id")
            print(f"Zapisywanie zdjęcia dla użytkownika {user_id} i ID {monument.building_id}")
            saved_photo_path = UserBuildingRepository.save_user_photo(
                user_id,
                monument.building_id,
                photo_path
            )
            if saved_photo_path:
                print(f"Zdjęcie zapisane: {saved_photo_path}")
                success_button = ft.ElevatedButton(
                    "Zobacz swój profil",
                    icon=ft.icons.PERSON,
                    on_click=lambda e: show_profile_after_success(e),
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.GREEN_700,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    )
                )
                success_prompt = ft.Text(
                    "Zabytek dodany do Twojego profilu!",
                    color=ft.colors.GREEN_800,
                    weight=ft.FontWeight.BOLD,
                    size=16
                )
                success_row.controls = [success_prompt, success_button]
                success_row.visible = True
            else:
                print("Próba wyświetlenia SnackBar: Nie udało się zapisać zdjęcia")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Nie udało się zapisać zdjęcia."),
                    bgcolor=ft.colors.RED_700,
                    duration=3000,
                )
                page.snack_bar.open = True
        else:
            print(f"Nieudana weryfikacja lub brak użytkownika/zdjęcia. Success={success}, message={message}")
            # Wyświetl SnackBar dla nieudanej weryfikacji
            page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.RED_700,
                duration=3000,
            )
            page.snack_bar.open = True
            # Fallbackowy komunikat w GUI
            fallback_message.value = message
            fallback_message.visible = True

        # Podwójna aktualizacja z opóźnieniem
        page.update()
        time.sleep(0.2)
        page.update()

    def _get_confidence_color(confidence):
        if confidence > 0.7:
            return ft.colors.GREEN
        elif confidence > 0.4:
            return ft.colors.ORANGE
        return ft.colors.RED

    def show_profile_after_success(e):
        while len(page.views) > 2:
            page.views.pop()
        from views.profile_view import create_profile_view
        page.views.append(create_profile_view(page))
        page.update()

    def on_file_picked(e):
        if e.files and len(e.files) > 0:
            try:
                file_path = e.files[0].path
                print(f"Wybrano plik: {file_path}")

                valid_extensions = ['.jpg', '.jpeg', '.png']
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in valid_extensions:
                    print("Próba wyświetlenia SnackBar: Zły format pliku")
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Wybierz plik JPG, JPEG lub PNG"),
                        bgcolor=ft.colors.RED_700,
                        duration=3000,
                    )
                    page.snack_bar.open = True
                    page.update()
                    return

                image_preview.src = file_path
                image_preview.visible = True
                image_path_container.data = file_path

                photo_status.content.value = f"Zdjęcie załadowane: {os.path.basename(file_path)}"
                photo_status.content.color = ft.colors.BLUE_700
                photo_status.visible = True

                result_container.visible = False
                success_row.visible = False
                override_button.visible = False
                fallback_message.visible = False

                page.update()
                show_processing_ui()
                time.sleep(0.5)  # Lepszy UX

                result = analyze_image_with_ai(file_path, monument.building_id)
                print(f"Wywołanie show_result z wynikiem: {result}")
                show_result(result, file_path)

            except Exception as ex:
                print(f"Błąd przetwarzania pliku: {str(ex)}")
                import traceback
                traceback.print_exc()
                progress_ring.visible = False
                progress_text.visible = False
                print("Próba wyświetlenia SnackBar: Błąd przetwarzania pliku")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Błąd: {str(ex)}"),
                    bgcolor=ft.colors.RED_700,
                    duration=3000,
                )
                page.snack_bar.open = True
                upload_button.disabled = False
                camera_button.disabled = False
                page.update()

    def force_accept_image(e):
        file_path = image_path_container.data
        if not file_path or not os.path.exists(file_path):
            print("Próba wyświetlenia SnackBar: Brak zdjęcia do zaakceptowania")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Brak zdjęcia do zaakceptowania"),
                bgcolor=ft.colors.RED_700,
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
            return

        try:
            result = {
                "success": True,
                "confidence": 0.75,
                "message": "Zaakceptowano ręcznie: Zdjęcie zatwierdzone"
            }
            show_result(result, file_path)
            override_button.visible = False
            page.update()
        except Exception as ex:
            print(f"Błąd ręcznej akceptacji: {str(ex)}")
            print("Próba wyświetlenia SnackBar: Błąd ręcznej akceptacji")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Błąd: {str(ex)}"),
                bgcolor=ft.colors.RED_700,
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def go_back(e):
        page.views.pop()
        page.update()

    def show_camera_message(e):
        print("Próba wyświetlenia SnackBar: Funkcja aparatu")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Funkcja aparatu będzie dostępna wkrótce!"),
            bgcolor=ft.colors.BLUE_700,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    file_picker.on_result = on_file_picked

    upload_button = ft.ElevatedButton(
        "Wybierz zdjęcie",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            dialog_title="Wybierz zdjęcie zabytku",
            allowed_extensions=["jpg", "jpeg", "png"],
            allow_multiple=False
        ),
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_700,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )
    )

    camera_button = ft.ElevatedButton(
        "Zrób zdjęcie",
        icon=ft.icons.CAMERA_ALT,
        on_click=show_camera_message,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_700,
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )
    )

    override_button = ft.ElevatedButton(
        "Wymuś akceptację",
        icon=ft.icons.ADMIN_PANEL_SETTINGS,
        on_click=force_accept_image,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.ORANGE_700,
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        ),
        visible=False,
        tooltip="Użyj, jeśli zdjęcie na pewno przedstawia zabytek"
    )

    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_GREY_700,
        )
    )

    success_row = ft.Row(
        [],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        visible=False
    )

    action_buttons = ft.Row(
        [upload_button, camera_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    processing_ui = ft.Row(
        [progress_ring, progress_text],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    verification_info = ft.Container(
        content=ft.Column([
            ft.Text(
                "Jak działa weryfikacja?",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.BLUE_900
            ),
            ft.Text(
                "System analizuje zdjęcie i porównuje je z referencjami zabytku, używając zaawansowanego modelu AI. "
                "Wynik powyżej 70% przy niskim podobieństwie do innych zabytków oznacza sukces.",
                size=14,
                color=ft.colors.BLUE_GREY_700,
                text_align=ft.TextAlign.JUSTIFY
            ),
            ft.Row([
                ft.Icon(ft.icons.TIPS_AND_UPDATES, color=ft.colors.AMBER_700),
                ft.Column([
                    ft.Text(
                        "Porady dla najlepszych wyników:",
                        italic=True,
                        size=14,
                        color=ft.colors.AMBER_700,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        "• Upewnij się, że zabytek jest wyraźnie widoczny\n"
                        "• Fotografuj w dobrym oświetleniu\n"
                        "• Unikaj przeszkód zasłaniających zabytek",
                        italic=True,
                        size=13,
                        color=ft.colors.AMBER_700
                    )
                ])
            ], spacing=10)
        ], spacing=10),
        padding=15,
        border_radius=10,
        bgcolor=ft.colors.BLUE_50,
        border=ft.border.all(1, ft.colors.BLUE_200),
        margin=ft.margin.only(bottom=15)
    )

    return ft.View(
        f"/monument-verify/{monument.building_id}",
        [
            ft.Container(
                content=ft.Text(
                    f"Weryfikacja zabytku: {monument.name}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_900
                ),
                margin=ft.margin.only(bottom=10)
            ),
            verification_info,
            ft.Container(
                content=ft.Text(
                    "Zrób lub wybierz zdjęcie zabytku, aby zweryfikować swoją obecność.",
                    text_align=ft.TextAlign.CENTER,
                    size=16,
                ),
                padding=ft.padding.all(15),
                margin=ft.margin.only(bottom=20),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50,
                width=500,
            ),
            ft.Container(
                content=image_preview,
                alignment=ft.alignment.center,
                bgcolor=ft.colors.GREY_200,
                width=400,
                height=300,
                border_radius=10,
                padding=5,
                margin=ft.margin.only(bottom=15),
            ),
            photo_status,
            action_buttons,
            processing_ui,
            result_container,
            fallback_message,
            override_button,
            success_row,
            ft.Container(
                content=back_button,
                margin=ft.margin.only(top=20)
            ),
            image_path_container,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
        auto_scroll=True
    )