import flet as ft
import httpx
import base64
import asyncio

# --- CONFIGURAZIONE ---
# Incolla qui la tua chiave API (AIza...)
GEMINI_KEY = "INSERISCI_QUI_LA_TUA_CHIAVE" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO - Gemini 2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 20

    targa_input = ft.TextField(label="Targa Veicolo", border_color="blue", text_align="center")
    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", text_align="center")
    result_text = ft.Markdown("")

    # HO RIMOSSO 'ft.FilePickerResultEvent' -> ora non crasha più!
    async def elabora_video(e):
        if not e.files:
            return
        
        progress_ring.visible = True
        status_text.value = "⏳ Analisi Gemini 2.0 Flash in corso..."
        page.update()

        try:
            # Per il web leggiamo il file direttamente dai bytes
            video_bytes = e.files[0].content
            video_data = base64.b64encode(video_bytes).decode("utf-8")

            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza il video della targa {targa_input.value} e descrivi ogni danno alla carrozzeria."},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_data}}
                    ]
                }]
            }

            async with httpx.AsyncClient(timeout=150.0) as client:
                response = await client.post(API_URL, json=payload)
                
            if response.status_code == 200:
                res = response.json()
                result_text.value = res['candidates'][0]['content']['parts'][0]['text']
                status_text.value = "✅ Analisi Completata"
            else:
                status_text.value = f"❌ Errore Google: {response.status_code}"
                result_text.value = response.text

        except Exception as ex:
            status_text.value = "❌ Errore"
            result_text.value = str(ex)
        
        progress_ring.visible = False
        page.update()

    file_picker = ft.FilePicker(on_result=elabora_video)
    page.overlay.append(file_picker)

    page.add(
        ft.Column([
            ft.Text("GSSA PRO", size=30, weight="bold", color="blue"),
            ft.Text("Powered by Gemini 2.0 Flash", size=12, italic=True),
            ft.Divider(),
            targa_input,
            ft.ElevatedButton(
                "CARICA VIDEO PERIZIA", 
                icon=ft.icons.UPLOAD_FILE,
                on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
            ),
            progress_ring,
            status_text,
            ft.Container(result_text, padding=15, bgcolor="#1A1A1A", border_radius=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Avviamo l'app
if __name__ == "__main__":
    ft.app(target=main)
