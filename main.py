import flet as ft
import time

def main(page: ft.Page):
    # Configurazioni base
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Se vedi questo, l'app Python è ufficialmente VIVA
    messaggio = ft.Text("GSSA PRO CARICATO", size=30, weight="bold", color="green")
    bottone_test = ft.ElevatedButton("CLICCA QUI PER TEST", on_click=lambda _: print("OK"))

    page.add(
        ft.Icon(ft.icons.BOLT, color="yellow", size=100),
        messaggio,
        bottone_test,
        ft.Text("Se vedi questa schermata, l'errore nero è sparito.", size=12, color="grey")
    )
    page.update()

# Avvio senza 'async' per massima compatibilità
if __name__ == "__main__":
    ft.app(target=main)
