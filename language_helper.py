import flet as ft
from translations import TranslationManager, get_text
from ui_helpers import AppTheme


def create_language_selector(page, on_language_change=None, compact=False):
    language_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(lang_code, text=lang_name)
            for lang_code, lang_name in TranslationManager.LANGUAGES.items()
        ],
        value=TranslationManager.get_current_language(),
        label=get_text("change_language") if not compact else None,
        hint_text=get_text("select") if not compact else None,
        icon=ft.icons.LANGUAGE,
        width=150 if compact else 300,
        text_size=14,
        border_color=AppTheme.get_primary(),
        focused_border_color=AppTheme.get_primary(),
        bgcolor=ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE,
        color=AppTheme.get_text_primary(),
    )

    def on_dropdown_change(e):
        selected_lang = language_dropdown.value
        if selected_lang != TranslationManager.get_current_language():
            TranslationManager.set_language(selected_lang)
            page.session_set("language", selected_lang)

            if on_language_change:
                on_language_change(selected_lang)

    language_dropdown.on_change = on_dropdown_change

    return language_dropdown


def refresh_view_after_language_change(page, view_creator_function):
    new_view = view_creator_function(page)
    page.views.pop()
    page.views.append(new_view)
    page.update()


def show_language_picker(page, on_language_change=None):
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

        if on_language_change:
            on_language_change(lang_code)

    page.overlay.append(language_sheet)
    page.update()

    return language_sheet