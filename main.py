import flet as ft
import httpx
import base64
import asyncio
import os

# --- CONFIGURAZIONE ---
# Incolla qui la tua NUOVA chiave API generata su Google AI Studio
# IMPORTANTE: Se GitHub l'ha rilevata come segreta, cambiala su AI Studio!
GEMINI_KEY = "AQ.Ab8RN6LE982d9nnz62nIfIwmvCiySMUaBwfa7BtoDDkpOqnfgg" 

# Endpoint per Gemini 2.0 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO - Gemini 2.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 20

    # Elementi UI
    targa_input = ft.TextField(label="Targa Veicolo", border_color="blue", text_align="center")
    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", text_align="center", weight="bold")
    result_text = ft.Markdown("", selectable=True)

    async def elabora_video(e):
        # Controllo file e targa
        if not e.files or not targa_input.value:
            status_text.value = "⚠️ Inserisci la targa e seleziona un video"
            page.update()
            return

        video_path = e.files[0].path
        progress_ring.visible = True
        status_text.value = "⏳ Analisi professionale Gemini 2.0..."
        status_text.color = "blue"
        page.update()

        try:
            # 1. Lettura file e conversione Base64
            with open(video_path, "rb") as f:
                video_data = base64.b64encode(f.read()).decode("utf-8")

            # 2. Payload per Gemini 2.0 Flash
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"Agisci come perito. Analizza il video della targa {targa_input.value} e descrivi ogni danno, graffio o ammaccatura."},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_data}}
                    ]
                }]
            }

            # 3. Chiamata API
            async with httpx.AsyncClient(timeout=150.0) as client:
                response = await client.post(API_URL, json=payload)
                
            if response.status_code == 200:
                data = response.json()
                result_text.value = data['candidates'][0]['content']['parts'][0]['text']
                status_text.value = "✅ Perizia Completata"
                status_text.color = "green"
            else:
                status_text.value = f"❌ Errore Google: {response.status_code}"
                result_text.value = response.text

        except Exception as ex:
            status_text.value = "❌ Errore Critico"
            result_text.value = str(ex)
        
        progress_ring.visible = False
        page.update()

    # Selettore file (Rimosso il tipo di evento che causava l'errore)
    file_picker = ft.FilePicker(on_result=elabora_video)
    page.overlay.append(file_picker)

    # Layout finale
    page.add(
        ft.Column([
            ft.Text("GSSA PRO", size=30, weight="bold", color="blue"),
            ft.Text("Gemini 2.0 Flash Vision", size=12, italic=True),
            ft.Divider(),
            targa_input,
            ft.ElevatedButton(
                "SELEZIONA VIDEO PERIZIA", 
                icon=ft.icons.VIDEOCAM,
                on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
            ),
            progress_ring,
            status_text,
            ft.Container(result_text, padding=15, bgcolor="#1A1A1A", border_radius=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(target=main)