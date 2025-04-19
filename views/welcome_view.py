import flet as ft
from ui_helpers import AppTheme, create_action_button, show_snackbar


def create_welcome_view(page):
    def go_to_register(e):
        from views.register_view import create_register_view
        from ui_helpers import apply_route_change_animation, show_loading, hide_loading

        loading = show_loading(page, "Wczytywanie formularza rejestracji...")

        import time
        time.sleep(0.5)

        hide_loading(page, loading)

        apply_route_change_animation(page, create_register_view(page))
        page.update()

    def go_to_login(e):
        from views.login_view import create_login_view
        from ui_helpers import apply_route_change_animation, show_loading, hide_loading

        loading = show_loading(page, "Wczytywanie formularza logowania...")

        import time
        time.sleep(0.5)

        hide_loading(page, loading)

        apply_route_change_animation(page, create_login_view(page))
        page.update()

    def show_about(e):
        print("Kliknięto O aplikacji")

        # Zamiast dialogu, użyjmy bottomsheet
        about_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "O aplikacji",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.PRIMARY
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Zabytkownik to aplikacja, która pomoże Ci odkrywać, dokumentować i dzielić się swoimi wizytami w zabytkach. "
                        "Zarejestruj się, aby rozpocząć swoją przygodę z historią architektury!",
                        size=16,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.ElevatedButton(
                        "Zamknij",
                        on_click=lambda e: close_sheet(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=AppTheme.PRIMARY
                        )
                    )
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                padding=20,
                width=page.width
            ),
            open=True
        )

        def close_sheet():
            page.overlay.remove(about_sheet)
            page.update()

        page.overlay.append(about_sheet)
        page.update()

    register_button = create_action_button(
        text="Zarejestruj się",
        icon=ft.icons.PERSON_ADD,
        on_click=go_to_register,
        color=AppTheme.PRIMARY,
        width=300
    )

    login_button = create_action_button(
        text="Zaloguj się",
        icon=ft.icons.LOGIN,
        on_click=go_to_login,
        color=AppTheme.SUCCESS,
        width=300
    )

    about_button = create_action_button(
        text="O aplikacji",
        icon=ft.icons.INFO,
        on_click=show_about,
        color=AppTheme.SECONDARY,
        width=300
    )

    header = ft.Container(
        content=ft.Column([
            ft.Text(
                "Witaj w Zabytkowniku!",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.WHITE,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Odkrywaj, zwiedzaj i dokumentuj swoje przygody",
                size=16,
                color=ft.colors.WHITE,
                text_align=ft.TextAlign.CENTER,
                italic=True
            )
        ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=page.width,
        padding=ft.padding.symmetric(horizontal=20, vertical=40),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[AppTheme.PRIMARY, AppTheme.SECONDARY]
        ),
        border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
        animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        animate_opacity=ft.animation.Animation(800, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.colors.BLACK38,
            offset=ft.Offset(0, 4)
        ),
        opacity=1
    )

    banner_image = ft.Container(
        content=ft.Image(
            src="assets/logo.jpg",
            width=500,
            height=300,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(15),
        ),
        margin=ft.margin.only(bottom=20),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.colors.BLACK38,
            offset=ft.Offset(0, 4)
        ),
    )

    content = ft.Column(
        [
            header,
            ft.Container(height=20),
            banner_image,
            ft.Container(
                content=ft.Column(
                    [
                        register_button,
                        ft.Container(height=10),
                        login_button,
                        ft.Container(height=20),
                        about_button
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.BLACK12,
                    offset=ft.Offset(0, 2)
                ),
                width=400
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
    )

    return ft.View(
        "/welcome",
        [content],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )