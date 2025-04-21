import flet as ft
import time


class AppTheme:
    PRIMARY = ft.colors.BLUE_700
    SECONDARY = ft.colors.INDIGO_500
    BACKGROUND = ft.colors.BLUE_50
    SUCCESS = ft.colors.GREEN_600
    ERROR = ft.colors.RED_600
    WARNING = ft.colors.ORANGE_600
    INFO = ft.colors.BLUE_400

    TEXT_PRIMARY = ft.colors.BLUE_900
    TEXT_SECONDARY = ft.colors.GREY_800
    TEXT_HINT = ft.colors.GREY_600

    DARK_PRIMARY = ft.colors.BLUE_300
    DARK_SECONDARY = ft.colors.INDIGO_300
    DARK_BACKGROUND = ft.colors.GREY_900
    DARK_SUCCESS = ft.colors.GREEN_400
    DARK_ERROR = ft.colors.RED_400
    DARK_WARNING = ft.colors.ORANGE_400
    DARK_INFO = ft.colors.BLUE_300

    DARK_TEXT_PRIMARY = ft.colors.WHITE
    DARK_TEXT_SECONDARY = ft.colors.GREY_300
    DARK_TEXT_HINT = ft.colors.GREY_400

    BORDER_RADIUS_SM = 5
    BORDER_RADIUS_MD = 10
    BORDER_RADIUS_LG = 15

    PADDING_SM = 5
    PADDING_MD = 10
    PADDING_LG = 20

    ANIMATION_DURATION_MS = 300

    _DARK_MODE = False

    @classmethod
    def toggle_dark_mode(cls):
        cls._DARK_MODE = not cls._DARK_MODE
        return cls._DARK_MODE

    @classmethod
    def is_dark_mode(cls):
        return cls._DARK_MODE

    @classmethod
    def get_primary(cls):
        return cls.DARK_PRIMARY if cls._DARK_MODE else cls.PRIMARY

    @classmethod
    def get_secondary(cls):
        return cls.DARK_SECONDARY if cls._DARK_MODE else cls.SECONDARY

    @classmethod
    def get_background(cls):
        return cls.DARK_BACKGROUND if cls._DARK_MODE else cls.BACKGROUND

    @classmethod
    def get_success(cls):
        return cls.DARK_SUCCESS if cls._DARK_MODE else cls.SUCCESS

    @classmethod
    def get_error(cls):
        return cls.DARK_ERROR if cls._DARK_MODE else cls.ERROR

    @classmethod
    def get_warning(cls):
        return cls.DARK_WARNING if cls._DARK_MODE else cls.WARNING

    @classmethod
    def get_info(cls):
        return cls.DARK_INFO if cls._DARK_MODE else cls.INFO

    @classmethod
    def get_text_primary(cls):
        return cls.DARK_TEXT_PRIMARY if cls._DARK_MODE else cls.TEXT_PRIMARY

    @classmethod
    def get_text_secondary(cls):
        return cls.DARK_TEXT_SECONDARY if cls._DARK_MODE else cls.TEXT_SECONDARY

    @classmethod
    def get_text_hint(cls):
        return cls.DARK_TEXT_HINT if cls._DARK_MODE else cls.TEXT_HINT

    @staticmethod
    def create_theme():
        dark_mode = AppTheme._DARK_MODE
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=AppTheme.DARK_PRIMARY if dark_mode else AppTheme.PRIMARY,
                on_primary=ft.colors.BLACK if dark_mode else ft.colors.WHITE,
                secondary=AppTheme.DARK_SECONDARY if dark_mode else AppTheme.SECONDARY,
                on_secondary=ft.colors.BLACK if dark_mode else ft.colors.WHITE,
                surface=ft.colors.GREY_900 if dark_mode else ft.colors.WHITE,
                on_surface=ft.colors.WHITE if dark_mode else ft.colors.BLACK,
                background=AppTheme.DARK_BACKGROUND if dark_mode else AppTheme.BACKGROUND,
                on_background=ft.colors.WHITE if dark_mode else ft.colors.BLACK,
                error=AppTheme.DARK_ERROR if dark_mode else AppTheme.ERROR,
                on_error=ft.colors.BLACK if dark_mode else ft.colors.WHITE,
            ),
            visual_density=ft.VisualDensity.COMFORTABLE,
            use_material3=True
        )


def create_header(title, with_back_button=False, page=None, with_profile=False, with_logout=False):
    controls = []

    if with_back_button and page:
        controls.append(
            ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=lambda e: page.views.pop() or page.update(),
                icon_color=AppTheme.get_primary()
            )
        )

    controls.append(
        ft.Text(
            title,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.get_text_primary(),
            text_align=ft.TextAlign.CENTER,
            expand=True
        )
    )

    if with_profile:
        controls.append(
            ft.IconButton(
                icon=ft.icons.PERSON,
                on_click=lambda e: show_profile(e, page),
                icon_color=AppTheme.get_primary(),
                tooltip="Mój profil"
            )
        )

    if with_logout:
        controls.append(
            ft.IconButton(
                icon=ft.icons.LOGOUT,
                on_click=lambda e: logout(e, page),
                icon_color=AppTheme.get_error(),
                tooltip="Wyloguj"
            )
        )

    controls.append(
        ft.IconButton(
            icon=ft.icons.DARK_MODE if not AppTheme.is_dark_mode() else ft.icons.LIGHT_MODE,
            on_click=lambda e: toggle_theme(e, page),
            icon_color=AppTheme.get_primary(),
            tooltip="Zmień motyw"
        )
    )

    background_color = ft.colors.GREY_800 if AppTheme.is_dark_mode() else ft.colors.WHITE
    gradient_colors = [ft.colors.GREY_800, ft.colors.GREY_900] if AppTheme.is_dark_mode() else [ft.colors.BLUE_100,
                                                                                                ft.colors.WHITE]

    return ft.Container(
        content=ft.Row(controls, alignment=ft.MainAxisAlignment.CENTER),
        padding=AppTheme.PADDING_MD,
        margin=ft.margin.only(bottom=20),
        border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=gradient_colors
        ),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.colors.BLACK38,
            offset=ft.Offset(0, 2)
        )
    )


def toggle_theme(e, page):
    dark_mode = AppTheme.toggle_dark_mode()
    page.theme = AppTheme.create_theme()
    page.theme_mode = ft.ThemeMode.DARK if dark_mode else ft.ThemeMode.LIGHT

    e.control.icon = ft.icons.LIGHT_MODE if dark_mode else ft.icons.DARK_MODE
    page.update()


def create_monument_card(monument, on_click=None, show_map_button=True, show_details_button=True):
    buttons = []

    primary_color = AppTheme.get_primary()
    secondary_color = AppTheme.get_secondary()
    text_color = ft.colors.WHITE if AppTheme.is_dark_mode() else ft.colors.WHITE

    if show_details_button:
        details_button = ft.ElevatedButton(
            text="Szczegóły",
            on_click=on_click,
            data=monument.building_id,
            style=ft.ButtonStyle(
                color=text_color,
                bgcolor=primary_color,
                shape=ft.RoundedRectangleBorder(radius=AppTheme.BORDER_RADIUS_SM)
            ),
            width=120
        )
        buttons.append(details_button)

    if show_map_button:
        def on_map_click(e):
            building_id = e.control.data

            from views.map_view import create_map_view

            city = None
            if monument.description and "Wrocław" in monument.description:
                city = "Wrocław"

            loading = show_loading(e.page, "Wczytywanie mapy...")

            try:
                import time
                time.sleep(0.5)

                map_view = create_map_view(e.page, city)

                if map_view:
                    hide_loading(e.page, loading)
                    apply_route_change_animation(e.page, map_view)
                else:
                    hide_loading(e.page, loading)
                    show_snackbar(e.page, "Nie udało się utworzyć widoku mapy", color=AppTheme.get_error())
            except Exception as ex:
                print(f"Błąd podczas tworzenia widoku mapy: {ex}")
                import traceback
                traceback.print_exc()

                hide_loading(e.page, loading)
                show_snackbar(e.page, f"Wystąpił błąd: {str(ex)}", color=AppTheme.get_error())

        map_button = ft.ElevatedButton(
            text="Na mapie",
            icon=ft.icons.PLACE,
            on_click=on_map_click,
            data=monument.building_id,
            style=ft.ButtonStyle(
                color=text_color,
                bgcolor=secondary_color,
                shape=ft.RoundedRectangleBorder(radius=AppTheme.BORDER_RADIUS_SM)
            ),
            width=120
        )
        buttons.append(map_button)

    buttons_container = ft.Container(
        content=ft.Column(
            buttons,
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.only(top=8)
    )

    bg_color = ft.colors.GREY_800 if AppTheme.is_dark_mode() else ft.colors.WHITE
    text_color = AppTheme.get_text_primary()

    card_content = ft.Container(
        content=ft.Column([
            ft.Text(
                monument.name,
                size=16,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color=text_color
            ),
            ft.Container(
                content=ft.Image(
                    src=monument.image_path or "assets/placeholder.jpg",
                    width=160,
                    height=120,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(8)
                ),
                border_radius=ft.border_radius.all(8),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=2,
                    color=ft.colors.BLACK26,
                    offset=ft.Offset(0, 1)
                )
            ),
            buttons_container
        ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=AppTheme.PADDING_MD,
        width=200,
        bgcolor=bg_color,
        animate=ft.animation.Animation(
            duration=AppTheme.ANIMATION_DURATION_MS,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )
    )

    card = ft.Card(
        content=card_content,
        elevation=4,
        margin=AppTheme.PADDING_SM
    )

    def on_hover(e):
        if e.data == "true":
            card.elevation = 8
            card.content.scale = 1.03
            card.content.bgcolor = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.BLUE_50
            e.control.update()
        else:
            card.elevation = 4
            card.content.scale = 1.0
            card.content.bgcolor = bg_color
            e.control.update()

    card.on_hover = on_hover
    return card


def create_action_button(text, icon=None, on_click=None, color=None, width=None):
    if color is None:
        color = AppTheme.get_primary()

    text_color = ft.colors.WHITE
    if AppTheme.is_dark_mode() and color == AppTheme.get_primary():
        text_color = ft.colors.BLACK

    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=text_color,
            bgcolor=color,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=AppTheme.BORDER_RADIUS_MD),
            elevation=5,
            animation_duration=AppTheme.ANIMATION_DURATION_MS,
        ),
        width=width
    )


def create_monument_carousel(monuments, on_monument_click):
    carousel = ft.Row(
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        animate_size=ft.animation.Animation(
            duration=AppTheme.ANIMATION_DURATION_MS,
            curve=ft.AnimationCurve.EASE_OUT
        )
    )

    for monument in monuments:
        card = create_monument_card(monument, on_monument_click)
        carousel.controls.append(card)

    return ft.Container(
        content=carousel,
        padding=10,
        border_radius=10,
        height=270,
    )


def show_loading(page, message="Ładowanie..."):
    bg_color = ft.colors.with_opacity(0.8, ft.colors.BLACK) if AppTheme.is_dark_mode() else ft.colors.with_opacity(0.7,
                                                                                                                   ft.colors.BLACK)

    loading = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(width=40, height=40, stroke_width=3),
                ft.Text(message, size=14, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        width=page.width,
        height=page.height,
        alignment=ft.alignment.center,
        bgcolor=bg_color,
    )

    page.overlay.append(loading)
    page.update()
    return loading


def hide_loading(page, loading_overlay):
    if loading_overlay in page.overlay:
        page.overlay.remove(loading_overlay)
        page.update()


def show_snackbar(page, message, color=None, action=None):
    if color is None:
        color = AppTheme.get_primary()

    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.colors.WHITE),
        bgcolor=color,
        action=action,
        action_color=ft.colors.WHITE,
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


def show_info_dialog(page, title, content):
    print(f"Pokazuję dialog: {title}")

    bg_color = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE
    text_color = AppTheme.get_text_primary()
    primary_color = AppTheme.get_primary()

    info_sheet = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=primary_color
                ),
                ft.Divider(),
                ft.Text(
                    content,
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=text_color
                ),
                ft.ElevatedButton(
                    "OK",
                    on_click=lambda e: close_sheet(),
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE if not AppTheme.is_dark_mode() else ft.colors.BLACK,
                        bgcolor=primary_color
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
        page.overlay.remove(info_sheet)
        page.update()

    page.overlay.append(info_sheet)
    page.update()


def show_confirmation_dialog(page, title, content, on_confirm, on_cancel=None):
    print(f"Pokazuję dialog potwierdzenia: {title}")

    bg_color = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE
    text_color = AppTheme.get_text_primary()
    primary_color = AppTheme.get_primary()
    secondary_color = AppTheme.get_secondary()

    confirmation_sheet = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=primary_color
                ),
                ft.Divider(),
                ft.Text(
                    content,
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=text_color
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Anuluj",
                        on_click=lambda e: cancel_action(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=secondary_color
                        )
                    ),
                    ft.ElevatedButton(
                        "Potwierdź",
                        on_click=lambda e: confirm_action(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE if not AppTheme.is_dark_mode() else ft.colors.BLACK,
                            bgcolor=primary_color
                        )
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
            padding=20,
            width=page.width,
            bgcolor=bg_color
        ),
        open=True
    )

    def cancel_action():
        page.overlay.remove(confirmation_sheet)
        page.update()
        if on_cancel:
            on_cancel()

    def confirm_action():
        page.overlay.remove(confirmation_sheet)
        page.update()
        on_confirm()

    page.overlay.append(confirmation_sheet)
    page.update()


def apply_route_change_animation(page, new_view, direction="forward"):
    try:
        print(f"Animowanie przejścia widoku, kierunek: {direction}")
        start_offset = 1.0 if direction == "forward" else -1.0

        new_view.offset = ft.transform.Offset(start_offset, 0)
        new_view.animate_offset = ft.animation.Animation(
            duration=AppTheme.ANIMATION_DURATION_MS,
            curve=ft.AnimationCurve.EASE_OUT
        )

        if len(page.views) > 0:
            try:
                old_view = page.views[-1]
                old_view.offset = ft.transform.Offset(0, 0)
                old_view.animate_offset = ft.animation.Animation(
                    duration=AppTheme.ANIMATION_DURATION_MS,
                    curve=ft.AnimationCurve.EASE_IN
                )
                old_view.offset = ft.transform.Offset(-start_offset, 0)
            except Exception as e:
                print(f"Błąd podczas animowania poprzedniego widoku: {e}")

        page.views.append(new_view)
        new_view.offset = ft.transform.Offset(0, 0)
        page.update()
        print("Zakończono animację przejścia")
    except Exception as e:
        print(f"Błąd podczas animacji przejścia: {e}")
        page.views.append(new_view)
        page.update()


def create_responsive_grid(controls, columns=3):
    rows = []
    current_row = []

    for i, control in enumerate(controls):
        current_row.append(control)

        if len(current_row) >= columns or i == len(controls) - 1:
            rows.append(
                ft.Row(
                    controls=current_row,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            )
            current_row = []

    return ft.Column(
        rows,
        spacing=10,
        scroll=ft.ScrollMode.AUTO
    )


def show_profile(e, page):
    from views.profile_view import create_profile_view
    loading = show_loading(page, "Wczytywanie profilu...")
    time.sleep(0.5)
    hide_loading(page, loading)
    apply_route_change_animation(page, create_profile_view(page))


def logout(e, page):
    bg_color = ft.colors.GREY_900 if AppTheme.is_dark_mode() else ft.colors.WHITE
    text_color = AppTheme.get_text_primary()
    primary_color = AppTheme.get_primary()
    error_color = AppTheme.get_error()

    logout_sheet = ft.BottomSheet(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "Wylogowanie",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=primary_color
                ),
                ft.Divider(),
                ft.Text(
                    "Czy na pewno chcesz się wylogować?",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=text_color
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Anuluj",
                        on_click=lambda e: close_sheet(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=AppTheme.get_secondary()
                        )
                    ),
                    ft.ElevatedButton(
                        "Wyloguj",
                        on_click=lambda e: perform_logout(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=error_color
                        )
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
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
        page.overlay.remove(logout_sheet)
        page.update()

    def perform_logout():
        close_sheet()
        page.session_clear()
        page.views.clear()
        from views.welcome_view import create_welcome_view
        page.views.append(create_welcome_view(page))
        show_snackbar(page, "Zostałeś wylogowany", color=AppTheme.get_success())

    page.overlay.append(logout_sheet)
    page.update()