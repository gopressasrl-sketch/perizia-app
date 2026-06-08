import flet as ft

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Se vedi questo, abbiamo vinto contro lo schermo nero!
    page.add(
        ft.Icon(ft.icons.CHECK_CIRCLE, color="green", size=100),
        ft.Text("FUNZIONA!", size=40, weight="bold"),
        ft.Text("L'app Python è stata avviata correttamente.", size=16),
        ft.ElevatedButton("CHIUDI", on_click=lambda _: page.window_destroy())
    )

ft.app(target=main)
