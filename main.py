import flet as ft

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Se vedi questo, il problema delle architetture è risolto!
    page.add(
        ft.Icon(ft.icons.CHEVRON_RIGHT, color="blue", size=100),
        ft.Text("SISTEMA OPERATIVO", size=30, weight="bold"),
        ft.Text("Connessione con Gemini 2.0 pronta.", color="grey"),
        ft.ElevatedButton("TEST CONNESSIONE", on_click=lambda _: print("Click"))
    )
    page.update()

if __name__ == "__main__":
    # Avvio standard per mobile
    ft.app(target=main)
