import flet as ft
import os
import time
from datetime import datetime
import tempfile
from database.repositories.user_building_repository import UserBuildingRepository
from ai.ImageAnalyzer import ImageAnalyzer


def analyze_image_with_ai(image_path, monument_id):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Plik {image_path} nie istnieje")

        print(f"Rozpoczynam analizę obrazu: {image_path} dla zabytku ID: {monument_id}")
        analyzer = ImageAnalyzer(
            model_name='resnet50',
            similarity_threshold=0.8,
            reference_dir='assets/references'
        )

        result = analyzer.verify_monument(image_path, monument_id)

        print(f"Wynik analizy: {result}")

        return result
    except Exception as e:
        print(f"Błąd podczas analizy obrazu: {e}")
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "confidence": 0,
            "message": f"Wystąpił błąd podczas analizy: {str(e)}"
        }


def create_photo_capture_view(page, monument):
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

    def show_processing_ui():
        progress_ring.visible = True
        progress_text.value = "Analizowanie zdjęcia..."
        progress_text.visible = True
        result_container.visible = False
        upload_button.disabled = True
        camera_button.disabled = True
        page.update()

    def show_result(result, photo_path=None):
        success = result.get("success", False)
        message = result.get("message", "Nieznany wynik analizy")
        confidence = result.get("confidence", 0)

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

        upload_button.disabled = False
        camera_button.disabled = False

        if success and page.session_get("current_user_id") and photo_path:
            user_id = page.session_get("current_user_id")
            print(f"Zapisywanie zdjęcia dla użytkownika {user_id} i zabytku {monument.building_id}")

            saved_photo_path = UserBuildingRepository.save_user_photo(
                user_id,
                monument.building_id,
                photo_path
            )

            if saved_photo_path:
                print(f"Zdjęcie zapisane pod ścieżką: {saved_photo_path}")

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
                    "Zabytek został dodany do Twojego profilu!",
                    color=ft.colors.GREEN_800,
                    weight=ft.FontWeight.BOLD,
                    size=16
                )

                success_row.controls = [success_prompt, success_button]
                success_row.visible = True
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Nie udało się zapisać zdjęcia. Spróbuj ponownie."))
                page.snack_bar.open = True

        page.update()

    def _get_confidence_color(confidence):
        if confidence > 0.6:
            return ft.colors.GREEN
        elif confidence > 0.4:
            return ft.colors.ORANGE
        else:
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
                    page.snack_bar = ft.SnackBar(ft.Text("Wybierz plik obrazu (JPG, JPEG lub PNG)"))
                    page.snack_bar.open = True
                    page.update()
                    return

                image_preview.src = file_path
                image_preview.visible = True
                image_path_container.data = file_path

                result_container.visible = False
                success_row.visible = False

                page.update()

                show_processing_ui()

                time.sleep(0.5)

                result = analyze_image_with_ai(file_path, monument.building_id)

                show_result(result, file_path)

            except Exception as ex:
                print(f"Błąd przetwarzania pliku: {str(ex)}")
                import traceback
                traceback.print_exc()

                progress_ring.visible = False
                progress_text.visible = False

                page.snack_bar = ft.SnackBar(ft.Text(f"Błąd przetwarzania: {str(ex)}"))
                page.snack_bar.open = True

                upload_button.disabled = False
                camera_button.disabled = False

                page.update()

    def go_back(e):
        page.views.pop()
        page.update()

    def show_camera_message(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Funkcja robienia zdjęcia bezpośrednio w aplikacji będzie dostępna wkrótce!")
        )
        page.snack_bar.open = True
        page.update()

    file_picker.on_result = on_file_picked

    upload_button = ft.ElevatedButton(
        "Wybierz zdjęcie z galerii",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            dialog_title="Wybierz zdjęcie zabytku",
            allowed_extensions=["jpg", "jpeg", "png"],
            allow_multiple=False
        ),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )
    )

    camera_button = ft.ElevatedButton(
        "Zrób zdjęcie",
        icon=ft.icons.CAMERA_ALT,
        on_click=show_camera_message,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )
    )

    back_button = ft.ElevatedButton(
        "Powrót",
        on_click=go_back,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_GREY_700,
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

    return ft.View(
        f"/monument-verify/{monument.building_id}",
        [
            ft.Container(
                content=ft.Text(
                    f"Weryfikacja zabytku: {monument.name}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900
                ),
                margin=ft.margin.only(bottom=10)
            ),

            ft.Container(
                content=ft.Text(
                    "Zrób zdjęcie zabytku lub wybierz istniejące zdjęcie z galerii, "
                    "aby zweryfikować swoją obecność w tym miejscu.",
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

            action_buttons,

            processing_ui,

            result_container,

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