import flet as ft
from ui_helpers import AppTheme, create_action_button, show_snackbar


def create_welcome_view(page):
    def go_to_register(e):
        from views.register_view import create_register_view
        from ui_helpers import apply_route_change_animation, show_loading, hide_loading

        # Pokaż animację ładowania
        loading = show_loading(page, "Wczytywanie formularza rejestracji...")

        # Symulacja krótkiego opóźnienia dla efektu
        import time
        time.sleep(0.5)

        # Ukrycie ładowania
        hide_loading(page, loading)

        # Przejście z animacją
        apply_route_change_animation(page, create_register_view(page))
        page.update()

    def go_to_login(e):
        from views.login_view import create_login_view
        from ui_helpers import apply_route_change_animation, show_loading, hide_loading

        # Pokaż animację ładowania
        loading = show_loading(page, "Wczytywanie formularza logowania...")

        # Symulacja krótkiego opóźnienia dla efektu
        import time
        time.sleep(0.5)

        # Ukrycie ładowania
        hide_loading(page, loading)

        # Przejście z animacją
        apply_route_change_animation(page, create_login_view(page))
        page.update()

    def show_about(e):
        # Wyświetlenie informacji o aplikacji
        from ui_helpers import show_confirmation_dialog
        show_confirmation_dialog(
            page,
            "O aplikacji",
            "Zabytkownik to aplikacja, która pomoże Ci odkrywać, dokumentować i dzielić się swoimi wizytami w zabytkach. " +
            "Zarejestruj się, aby rozpocząć swoją przygodę z historią architektury!",
            lambda: None
        )

    # Ładne przyciski z animacjami
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

    # Efektowny baner górny
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
        opacity=1  # Ustawione na 1 zamiast 0, żeby element był widoczny od razu
    )

    # Dodajemy atrakcyjną grafikę
    banner_image = ft.Container(
        content=ft.Image(
            src="assets/Hala.jpeg",  # Wykorzystujemy istniejący obraz jako banner
            width=400,
            height=200,
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

    # Układamy elementy w atrakcyjny sposób
    content = ft.Column(
        [
            header,
            ft.Container(height=20),  # Odstęp
            banner_image,
            ft.Container(
                content=ft.Column(
                    [
                        register_button,
                        ft.Container(height=10),  # Odstęp
                        login_button,
                        ft.Container(height=20),  # Większy odstęp
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

    # Tworzymy widok z możliwością przewijania na mniejszych ekranach
    return ft.View(
        "/welcome",
        [content],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0
    )