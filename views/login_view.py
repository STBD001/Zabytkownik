import flet as ft
from database.repositories.user_repository import UserRepository
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    apply_route_change_animation
)


def create_login_view(page):
    username_field = ft.TextField(
        label="Nazwa użytkownika",
        width=300,
        border_color=AppTheme.PRIMARY,
        focused_border_color=AppTheme.PRIMARY,
        prefix_icon=ft.icons.PERSON,
        bgcolor=ft.colors.WHITE
    )

    password_field = ft.TextField(
        label="Hasło",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=AppTheme.PRIMARY,
        focused_border_color=AppTheme.PRIMARY,
        prefix_icon=ft.icons.LOCK,
        bgcolor=ft.colors.WHITE
    )

    error_text = ft.Text(
        "",
        color=AppTheme.ERROR,
        size=14,
        width=300,
        text_align=ft.TextAlign.CENTER
    )

    progress_ring = ft.ProgressRing(
        width=16,
        height=16,
        stroke_width=2,
        color=ft.colors.WHITE,
        visible=False
    )

    def login(e):
        if not username_field.value:
            username_field.error_text = "Podaj nazwę użytkownika"
            page.update()
            return

        if not password_field.value:
            password_field.error_text = "Podaj hasło"
            page.update()
            return

        username_field.error_text = None
        password_field.error_text = None
        error_text.value = ""

        progress_ring.visible = True
        login_button.disabled = True
        back_button.disabled = True
        page.update()

        try:
            import time
            time.sleep(0.8)

            user = UserRepository.authenticate(username_field.value, password_field.value)

            if user:
                progress_ring.visible = False
                login_button.disabled = False
                back_button.disabled = False

                page.session_set("current_user", user)
                page.session_set("current_user_id", user.user_id)

                loading = show_loading(page, "Ładowanie aplikacji...")

                try:
                    print("Logowanie powiodło się, przechodzę do widoku kontynentu")

                    # Bezpośrednio import i nawigacja do widoku kontynentu
                    import time
                    time.sleep(0.5)  # Krótkie opóźnienie

                    # Ważne - najpierw zaimportuj moduł
                    from views.continent_view import create_continent_view

                    # Wyczyść historię nawigacji
                    page.views.clear()

                    # Utwórz widok kontynentu
                    print("Tworzenie widoku kontynentu")
                    continent_view = create_continent_view(page)

                    # Dodaj widok do stosu widoków
                    print("Dodawanie widoku do stosu")
                    page.views.append(continent_view)

                    # Ważne - wykonaj aktualizację strony
                    print("Aktualizacja strony")
                    page.update()

                    # Na końcu ukryj ładowanie i pokaż komunikat
                    print("Logowanie zakończone sukcesem")
                    show_snackbar(page, f"Witaj, {user.nickname}!", color=AppTheme.SUCCESS)
                except Exception as view_error:
                    print(f"Błąd podczas ładowania widoku kontynentu: {view_error}")
                    import traceback
                    traceback.print_exc()

                    page.views.clear()
                    from views.welcome_view import create_welcome_view
                    page.views.append(create_welcome_view(page))
                    page.update()
                    show_snackbar(page, f"Błąd podczas ładowania aplikacji: {str(view_error)}", color=AppTheme.ERROR)
                finally:
                    # Upewnij się, że overlay ładowania jest usunięty
                    hide_loading(page, loading)
            else:
                progress_ring.visible = False
                login_button.disabled = False
                back_button.disabled = False

                error_text.value = "Nieprawidłowa nazwa użytkownika lub hasło"
                page.update()

                username_field.opacity = 0.8
                password_field.opacity = 0.8
                page.update()

                time.sleep(0.1)
                username_field.opacity = 1.0
                password_field.opacity = 1.0
                page.update()
        except Exception as e:
            progress_ring.visible = False
            login_button.disabled = False
            back_button.disabled = False

            error_text.value = f"Wystąpił błąd: {str(e)}"
            page.update()

    login_button = create_action_button(
        text="Zaloguj się",
        icon=ft.icons.LOGIN,
        on_click=login,
        color=AppTheme.PRIMARY,
        width=300
    )

    login_button_container = ft.Container(
        content=ft.Row(
            [login_button, progress_ring],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        width=300
    )

    def go_back(e):
        apply_route_change_animation(page, page.views[-2], direction="backward")
        page.views.pop()
        page.update()

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY,
        width=300
    )

    def go_to_register(e):
        from views.register_view import create_register_view

        loading = show_loading(page, "Wczytywanie formularza rejestracji...")

        import time
        time.sleep(0.5)

        hide_loading(page, loading)

        register_view = create_register_view(page)
        apply_route_change_animation(page, register_view)

    register_button = ft.TextButton(
        content=ft.Row(
            [
                ft.Text("Nie masz konta?"),
                ft.Text(
                    "Zarejestruj się",
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.PRIMARY
                )
            ],
            spacing=5
        ),
        on_click=go_to_register
    )

    header = create_header(
        "Logowanie",
        with_back_button=True,
        page=page
    )

    logo = ft.Container(
        content=ft.Image(
            src="assets/Hala.jpeg",
            width=120,
            height=120,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(60)
        ),
        margin=ft.margin.only(bottom=20),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.colors.BLACK38,
            offset=ft.Offset(0, 4)
        ),
        border_radius=ft.border_radius.all(60),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS
    )

    login_form = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text(
                    "Witaj ponownie!",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Zaloguj się, aby kontynuować swoją przygodę z zabytkami",
                    size=14,
                    color=AppTheme.TEXT_HINT,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                username_field,
                ft.Container(height=10),
                password_field,
                ft.Container(height=5),
                error_text,
                ft.Container(height=20),
                login_button_container,
                ft.Container(height=10),
                register_button,
                ft.Container(height=20),
                back_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        ),
        width=400,
        padding=30,
        margin=20,
        border_radius=15,
        bgcolor=ft.colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.BLACK12,
            offset=ft.Offset(0, 5)
        ),
        animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_opacity=ft.animation.Animation(400, ft.AnimationCurve.EASE_OUT),
        opacity=1
    )

    return ft.View(
        "/login",
        [
            header,
            ft.Container(
                content=login_form,
                alignment=ft.alignment.center,
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[AppTheme.BACKGROUND, ft.colors.WHITE]
                ),
            )
        ],
        padding=0
    )