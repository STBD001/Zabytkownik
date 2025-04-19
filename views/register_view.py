import flet as ft
from database.repositories.user_repository import UserRepository
from database.models.user import User
from ui_helpers import (
    AppTheme, create_header, create_action_button,
    show_loading, hide_loading, show_snackbar,
    apply_route_change_animation
)


def create_register_view(page):
    username_field = ft.TextField(
        label="Nazwa użytkownika",
        width=300,
        border_color=AppTheme.PRIMARY,
        focused_border_color=AppTheme.PRIMARY,
        prefix_icon=ft.icons.PERSON,
        bgcolor=ft.colors.WHITE,
        helper_text="Będzie używana do logowania"
    )

    password_field = ft.TextField(
        label="Hasło",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=AppTheme.PRIMARY,
        focused_border_color=AppTheme.PRIMARY,
        prefix_icon=ft.icons.LOCK,
        bgcolor=ft.colors.WHITE,
        helper_text="Minimum 6 znaków"
    )

    confirm_password_field = ft.TextField(
        label="Potwierdź hasło",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=AppTheme.PRIMARY,
        focused_border_color=AppTheme.PRIMARY,
        prefix_icon=ft.icons.LOCK_OUTLINE,
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

    def register(e):
        if not username_field.value:
            username_field.error_text = "Podaj nazwę użytkownika"
            page.update()
            return

        if not password_field.value:
            password_field.error_text = "Podaj hasło"
            page.update()
            return

        if len(password_field.value) < 6:
            password_field.error_text = "Hasło musi mieć minimum 6 znaków"
            page.update()
            return

        if not confirm_password_field.value:
            confirm_password_field.error_text = "Potwierdź hasło"
            page.update()
            return

        if password_field.value != confirm_password_field.value:
            confirm_password_field.error_text = "Hasła nie są identyczne"
            page.update()
            return

        username_field.error_text = None
        password_field.error_text = None
        confirm_password_field.error_text = None
        error_text.value = ""

        progress_ring.visible = True
        register_button.disabled = True
        back_button.disabled = True
        page.update()

        try:
            import time
            time.sleep(0.8)

            existing_user = UserRepository.get_by_nickname(username_field.value)

            if existing_user:
                progress_ring.visible = False
                register_button.disabled = False
                back_button.disabled = False

                username_field.error_text = "Użytkownik o takiej nazwie już istnieje"
                page.update()
                return

            password_hash = User.hash_password(password_field.value)
            new_user = User(
                nickname=username_field.value,
                password_hash=password_hash,
                number_of_achievements=0
            )

            created_user = UserRepository.create(new_user)

            if created_user:
                progress_ring.visible = False
                register_button.disabled = False
                back_button.disabled = False

                loading = show_loading(page, "Pomyślnie zarejestrowano!")
                time.sleep(0.8)

                from views.login_view import create_login_view
                login_view = create_login_view(page)

                hide_loading(page, loading)

                # Zamiana przejścia z pop() na czysty navigationz animacją
                apply_route_change_animation(page, login_view)
                # Usuń poprzedni widok (rejestracji)
                if len(page.views) > 1:
                    page.views.pop(0)
                page.update()

                show_snackbar(page, "Rejestracja zakończona pomyślnie! Możesz się teraz zalogować.",
                              color=AppTheme.SUCCESS)
            else:
                progress_ring.visible = False
                register_button.disabled = False
                back_button.disabled = False

                error_text.value = "Błąd podczas rejestracji. Spróbuj ponownie."
                page.update()
        except Exception as e:
            progress_ring.visible = False
            register_button.disabled = False
            back_button.disabled = False

            error_text.value = f"Wystąpił błąd: {str(e)}"
            page.update()
            print(f"Błąd rejestracji: {e}")
            import traceback
            traceback.print_exc()

    register_button = create_action_button(
        text="Zarejestruj się",
        icon=ft.icons.PERSON_ADD,
        on_click=register,
        color=AppTheme.SUCCESS,
        width=300
    )

    register_button_container = ft.Container(
        content=ft.Row(
            [register_button, progress_ring],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        width=300
    )

    # Poprawiona funkcja powrotu
    def go_back(e):
        print("Kliknięto przycisk powrotu")
        try:
            from views.welcome_view import create_welcome_view
            welcome_view = create_welcome_view(page)

            # Zastosuj animację i dodaj widok
            apply_route_change_animation(page, welcome_view, direction="backward")

            # Usuń bieżący widok (rejestracji) po przekierowaniu
            if len(page.views) > 1:
                page.views.pop(0)
            page.update()
        except Exception as e:
            print(f"Błąd podczas powrotu: {e}")
            import traceback
            traceback.print_exc()

            # Awaryjne wyjście
            page.views.clear()
            from views.welcome_view import create_welcome_view
            page.views.append(create_welcome_view(page))
            page.update()

    back_button = create_action_button(
        "Powrót",
        icon=ft.icons.ARROW_BACK,
        on_click=go_back,
        color=AppTheme.SECONDARY,
        width=300
    )

    def go_to_login(e):
        from views.login_view import create_login_view

        loading = show_loading(page, "Wczytywanie formularza logowania...")

        import time
        time.sleep(0.5)

        hide_loading(page, loading)

        # Podobna poprawka jak dla przycisku powrotu
        login_view = create_login_view(page)
        apply_route_change_animation(page, login_view)
        if len(page.views) > 1:
            page.views.pop(0)
        page.update()

    login_button = ft.TextButton(
        content=ft.Row(
            [
                ft.Text("Masz już konto?"),
                ft.Text(
                    "Zaloguj się",
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.PRIMARY
                )
            ],
            spacing=5
        ),
        on_click=go_to_login
    )

    header = create_header(
        "Rejestracja",
        with_back_button=False,  # Zmiana - usuwamy strzałkę powrotu w nagłówku
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

    register_form = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text(
                    "Dołącz do społeczności",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Stwórz konto, aby odkrywać i dokumentować swoje podróże",
                    size=14,
                    color=AppTheme.TEXT_HINT,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                username_field,
                ft.Container(height=10),
                password_field,
                ft.Container(height=10),
                confirm_password_field,
                ft.Container(height=5),
                error_text,
                ft.Container(height=20),
                register_button_container,
                ft.Container(height=10),
                login_button,
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
        "/register",
        [
            header,
            ft.Container(
                content=register_form,
                alignment=ft.alignment.center,
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[AppTheme.BACKGROUND, ft.colors.WHITE]
                )
            )
        ],
        padding=0
    )