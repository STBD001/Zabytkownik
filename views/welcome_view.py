import flet as ft
from ui_helpers import AppTheme, create_action_button, show_snackbar
from translations import TranslationManager, get_text


def create_welcome_view(page):
    def go_to_register(e):
        from views.register_view import create_register_view
        from ui_helpers import apply_route_change_animation, show_loading, hide_loading

        loading = show_loading(page, get_text("loading"))

        import time
        time.sleep(0.5)

        hide_loading(page, loading)

        apply_route_change_animation(page, create_register_view(page))
        page.update()

    def go_to_login(e):
        from views.login_view import create_login_view
        from ui_helpers import apply_route_change_animation, show_loading, hide_loading

        loading = show_loading(page, get_text("loading"))

        import time
        time.sleep(0.5)

        hide_loading(page, loading)

        apply_route_change_animation(page, create_login_view(page))
        page.update()

    def show_about(e):
        bg_color = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE
        text_color = AppTheme.get_text_primary()

        about_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        get_text("about_app_title"),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.get_primary()
                    ),
                    ft.Divider(),
                    ft.Text(
                        get_text("about_app_content"),
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=text_color
                    ),
                    ft.ElevatedButton(
                        get_text("close"),
                        on_click=lambda e: close_sheet(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE if not AppTheme.is_dark_mode() else ft.colors.BLACK,
                            bgcolor=AppTheme.get_primary()
                        )
                    )
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                padding=20,
                width=page.width,
                bgcolor=bg_color
            ),
            open=True
        )

        def close_sheet():
            page.overlay.remove(about_sheet)
            page.update()

        page.overlay.append(about_sheet)
        page.update()

    def toggle_theme(e):
        dark_mode = AppTheme.toggle_dark_mode()
        page.theme = AppTheme.create_theme()
        page.theme_mode = ft.ThemeMode.DARK if dark_mode else ft.ThemeMode.LIGHT
        page.session_set("dark_mode", dark_mode)

        page.update()

        new_view = create_welcome_view(page)
        page.views.clear()
        page.views.append(new_view)
        page.update()

    def show_language_picker(e):
        bg_color = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE
        text_color = AppTheme.get_text_primary()

        language_buttons = []
        for lang_code, lang_name in TranslationManager.LANGUAGES.items():
            is_current = lang_code == TranslationManager.get_current_language()
            language_buttons.append(
                ft.ElevatedButton(
                    lang_name,
                    on_click=lambda e, code=lang_code: change_language(code),
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE if not AppTheme.is_dark_mode() else ft.colors.BLACK,
                        bgcolor=AppTheme.get_primary() if is_current else ft.colors.GREY_500,
                        padding=10,
                    ),
                    disabled=is_current
                )
            )

        language_sheet = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        get_text("change_language"),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.get_primary()
                    ),
                    ft.Divider(),
                    ft.Row(
                        language_buttons,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    ft.ElevatedButton(
                        get_text("close"),
                        on_click=lambda e: close_language_sheet(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=AppTheme.get_secondary()
                        )
                    )
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                padding=20,
                width=page.width,
                bgcolor=bg_color
            ),
            open=True
        )

        def close_language_sheet():
            page.overlay.remove(language_sheet)
            page.update()

        def change_language(lang_code):
            TranslationManager.set_language(lang_code)
            page.session_set("language", lang_code)
            close_language_sheet()

            new_view = create_welcome_view(page)
            page.views.clear()
            page.views.append(new_view)
            page.update()

        page.overlay.append(language_sheet)
        page.update()

    register_button = create_action_button(
        text=get_text("register"),
        icon=ft.icons.PERSON_ADD,
        on_click=go_to_register,
        color=AppTheme.get_primary(),
        width=300
    )

    login_button = create_action_button(
        text=get_text("login"),
        icon=ft.icons.LOGIN,
        on_click=go_to_login,
        color=AppTheme.get_success(),
        width=300
    )

    about_button = create_action_button(
        text=get_text("about_app"),
        icon=ft.icons.INFO,
        on_click=show_about,
        color=AppTheme.get_secondary(),
        width=300
    )

    theme_button = create_action_button(
        text=get_text("change_theme"),
        icon=ft.icons.DARK_MODE if not AppTheme.is_dark_mode() else ft.icons.LIGHT_MODE,
        on_click=toggle_theme,
        color=ft.colors.GREY_700,
        width=300
    )

    language_button = create_action_button(
        text=get_text("change_language"),
        icon=ft.icons.LANGUAGE,
        on_click=show_language_picker,
        color=ft.colors.TEAL_700,
        width=300
    )

    primary = AppTheme.get_primary()
    secondary = AppTheme.get_secondary()
    text_color = ft.colors.WHITE
    background_color = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE

    header = ft.Container(
        content=ft.Column([
            ft.Text(
                get_text("welcome_title"),
                size=32,
                weight=ft.FontWeight.BOLD,
                color=text_color,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                get_text("welcome_subtitle"),
                size=16,
                color=text_color,
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
            colors=[primary, secondary]
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
                        about_button,
                        ft.Container(height=10),
                        theme_button,
                        ft.Container(height=10),
                        language_button
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                padding=20,
                border_radius=10,
                bgcolor=background_color,
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

    page_bgcolor = AppTheme.get_background()

    return ft.View(
        "/welcome",
        [content],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=0,
        bgcolor=page_bgcolor
    )