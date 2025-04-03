import flet as ft

def create_add_photo_dialog():
    return ft.AlertDialog(
        title=ft.Text("Dodaj zdjęcie zabytku"),
        content=ft.Column(
            [
                ft.Text("Wybierz zabytek:"),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option("BaseCamp"),
                        ft.dropdown.Option("Ogród Uwr"),
                        ft.dropdown.Option("Katedra"),
                    ],
                    width=300,
                ),
                ft.Text("Wybierz zdjęcie"),
                ft.ElevatedButton("Wybierz plik", on_click=lambda e: print("Wybierz plik")),
            ],
            tight=True,
        ),
        actions=[
            ft.TextButton("Anuluj", on_click=lambda e: close_add_photo_dialog(e)),
            ft.TextButton("Dodaj", on_click=lambda e: close_add_photo_dialog(e)),
        ]
    )

def close_add_photo_dialog(e):
    e.control.page.dialog.open = False
    e.control.page.update()