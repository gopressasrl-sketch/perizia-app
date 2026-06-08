import flet as ft
import httpx
import base64
import asyncio
import os

# --- CONFIGURAZIONE ---
# Inserisci qui la tua chiave API corretta (deve iniziare con AIza...)
GEMINI_KEY = "AQ.Ab8RN6KQaP84VAzm3m1kcEwFRKRxAy6fo8YSdolx9mHb_Rbu3Q" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 20

    # UI Elements
    targa_input = ft.TextField(label="Targa Veicolo", border_color="blue", text_align="center")
    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", text_align="center", weight="bold")
    result_text = ft.Markdown("", selectable=True)

    async def elabora_video(e: ft.FilePickerResultEvent):
        if not e.files or not targa_input.value:
            status_text.value = "⚠️ Inserisci la targa e seleziona un video"
            page.update()
            return

        video_path = e.files[0].path
        progress_ring.visible = True
        status_text.value = "⏳ Lettura video e analisi in corso..."
        status_text.color = "white"
        page.update()

        try:
            # 1. Leggiamo il file video e convertiamolo in Base64
            with open(video_path, "rb") as video_file:
                video_data = base64.b64encode(video_file.read()).decode("utf-8")

            # 2. Prepariamo il payload per l'API di Google
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza questo video del veicolo targa {targa_input.value}. Elenca eventuali danni visivi sulla carrozzeria."},
                        {
                            "inline_data": {
                                "mime_type": "video/mp4",
                                "data": video_data
                            }
                        }
                    ]
                }]
            }

            # 3. Chiamata API usando httpx (più leggero per Android)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(API_URL, json=payload)
                
            if response.status_code == 200:
                data = response.json()
                testo_risposta = data['candidates'][0]['content']['parts'][0]['text']
                result_text.value = testo_risposta
                status_text.value = "✅ Analisi Completata"
                status_text.color = "green"
            else:
                status_text.value = f"❌ Errore API: {response.status_code}"
                status_text.color = "red"
                result_text.value = response.text

        except Exception as ex:
            status_text.value = "❌ Errore critico"
            status_text.color = "red"
            result_text.value = str(ex)
        
        progress_ring.visible = False
        page.update()

    # Setup File Picker
    file_picker = ft.FilePicker(on_result=elabora_video)
    page.overlay.append(file_picker)

    # Layout
    page.add(
        ft.Column([
            ft.Text("GSSA PRO", size=30, weight="bold", color="blue"),
            ft.Divider(),
            targa_input,
            ft.ElevatedButton(
                "CARICA VIDEO E ANALIZZA", 
                icon=ft.icons.VIDEOCAM,
                on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
            ),
            progress_ring,
            status_text,
            ft.Container(
                result_text, 
                padding=15, 
                bgcolor="#1A1A1A", 
                border_radius=10,
                expand=True
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Avvio dell'app
if __name__ == "__main__":
    ft.app(target=main)