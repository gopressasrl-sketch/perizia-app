import flet as ft
import httpx
import base64
import asyncio

# --- CONFIGURAZIONE ---
GEMINI_KEY = "AQ.Ab8RN6KQaP84VAzm3m1kcEwFRKRxAy6fo8YSdolx9mHb_Rbu3Q" # Assicurati che inizi con AIza...
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO - Gemini 2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    # UI Elements
    targa_input = ft.TextField(label="Targa Veicolo", border_color="blue")
    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", text_align="center")
    result_text = ft.Markdown("")

    # RIMOSSO 'ft.FilePickerResultEvent' che causava l'errore
    async def elabora_video(e): 
        if not e.files or not targa_input.value:
            return

        progress_ring.visible = True
        status_text.value = "⏳ Analisi Gemini 2.0 Flash in corso..."
        page.update()

        try:
            video_path = e.files[0].path
            
            with open(video_path, "rb") as f:
                video_data = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza il video del veicolo targa {targa_input.value}. Elenca i danni alla carrozzeria."},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_data}}
                    ]
                }]
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(API_URL, json=payload)
            
            if response.status_code == 200:
                res = response.json()
                result_text.value = res['candidates'][0]['content']['parts'][0]['text']
                status_text.value = "✅ Completato"
            else:
                status_text.value = f"❌ Errore API: {response.status_code}"
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
            targa_input,
            ft.ElevatedButton(
                "CARICA VIDEO E ANALIZZA", 
                icon=ft.icons.VIDEOCAM,
                on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
            ),
            progress_ring,
            status_text,
            ft.Container(result_text, padding=10, bgcolor="#222222", border_radius=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)