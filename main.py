import flet as ft
import os, cv2, json, asyncio
import google.generativeai as genai
from datetime import datetime
from fpdf import FPDF

# Inizializzazione AI
GEMINI_KEY = "LA_TUA_CHIAVE_QUI" # Oppure usa os.getenv se configurato
genai.configure(api_key=GEMINI_KEY, transport='rest')

def estrai_frames(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, total // 20) # 20 frame sono sufficienti e più leggeri per l'app
    for i in range(20):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = cap.read()
        if not ret: break
        _, buff = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frames.append({"mime_type": "image/jpeg", "data": buff.tobytes()})
    cap.release()
    return frames

async def main(page: ft.Page):
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # UI Elements
    targa_input = ft.TextField(label="Targa Veicolo", border_color="blue", text_align="center")
    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", text_align="center")
    result_text = ft.Markdown("")

    async def elabora_video(e: ft.FilePickerResultEvent):
        if not e.files or not targa_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Inserisci targa e seleziona un video!"))
            page.snack_bar.open = True
            page.update()
            return

        progress_ring.visible = True
        status_text.value = "Analisi in corso... attendi."
        page.update()

        try:
            video_path = e.files[0].path
            immagini = await asyncio.to_thread(estrai_frames, video_path)
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Analizza danni veicolo targa {targa_input.value}. Sii professionale e sintetico."
            
            response = await asyncio.to_thread(model.generate_content, [prompt] + immagini)
            
            result_text.value = response.text
            status_text.value = "✅ Analisi Completata"
        except Exception as ex:
            status_text.value = f"❌ Errore: {str(ex)}"
        
        progress_ring.visible = False
        page.update()

    file_picker = ft.FilePicker(on_result=elabora_video)
    page.overlay.append(file_picker)

    # Layout Home
    page.add(
        ft.Column([
            ft.Text("GSSA PRO", size=30, weight="bold", color="blue"),
            ft.Text("Ispezione AI Veicoli", size=16),
            ft.Divider(),
            targa_input,
            ft.ElevatedButton(
                "SELEZIONA VIDEO", 
                icon=ft.icons.VIDEO_FILE,
                on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
            ),
            progress_ring,
            status_text,
            ft.Container(result_text, padding=10, bgcolor="#222222", border_radius=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)