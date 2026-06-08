import flet as ft
import httpx
import base64
import asyncio

# --- CONFIGURAZIONE ---
# Metti qui la tua chiave API (quella che inizia con AIza...)
API_KEY = "INSERISCI_QUI_LA_TUA_CHIAVE" 
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    targa = ft.TextField(label="Targa Veicolo", border_color="blue")
    status = ft.Text("")
    risultato = ft.Markdown("")
    loading = ft.ProgressRing(visible=False)

    # Gestore del caricamento video (SENZA TIPI DI EVENTO PER EVITARE CRASH)
    async def al_risultato_file(e):
        if not e.files:
            return
        
        loading.visible = True
        status.value = "⏳ Analisi Gemini 2.0 in corso..."
        page.update()

        try:
            # Lettura video
            video_bytes = e.files[0].content
            video_64 = base64.b64encode(video_bytes).decode("utf-8")

            corpo_richiesta = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza danni targa {targa.value}"},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_64}}
                    ]
                }]
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(URL, json=corpo_richiesta)
            
            if res.status_code == 200:
                dati = res.json()
                risultato.value = dati['candidates'][0]['content']['parts'][0]['text']
                status.value = "✅ Analisi Completata"
            else:
                status.value = f"❌ Errore API: {res.status_code}"
                risultato.value = res.text

        except Exception as err:
            status.value = "❌ Errore critico"
            risultato.value = str(err)
        
        loading.visible = False
        page.update()

    # Creazione FilePicker
    selettore = ft.FilePicker(on_result=al_risultato_file)
    page.overlay.append(selettore)

    # UI dell'app
    page.add(
        ft.Text("GSSA PRO", size=35, weight="bold", color="blue"),
        ft.Text("Ispezione Veicoli AI", size=15, italic=True),
        ft.Divider(),
        targa,
        ft.ElevatedButton(
            "CARICA VIDEO PERIZIA", 
            icon=ft.icons.VIDEO_CAMERA_FRONT,
            on_click=lambda _: selettore.pick_files(file_type=ft.FilePickerFileType.VIDEO)
        ),
        loading,
        status,
        ft.Container(risultato, padding=10, bgcolor="#1A1A1A", border_radius=10)
    )

# Avvio corretto per il Web
if __name__ == "__main__":
    ft.app(main)
