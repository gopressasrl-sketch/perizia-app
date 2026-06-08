import flet as ft
import os, json, asyncio
import google.generativeai as genai
from datetime import datetime

# CONFIGURAZIONE (Metti la tua chiave qui)
GEMINI_KEY = "AQ.Ab8RN6KQaP84VAzm3m1kcEwFRKRxAy6fo8YSdolx9mHb_Rbu3Q"
genai.configure(api_key=GEMINI_KEY)

async def main(page: ft.Page):
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    targa_input = ft.TextField(label="Targa Veicolo", border_color="blue", text_align="center")
    progress_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("", text_align="center")
    result_text = ft.Markdown("")

    async def elabora_video(e: ft.FilePickerResultEvent):
        if not e.files or not targa_input.value:
            return

        progress_ring.visible = True
        status_text.value = "Caricamento e analisi video in corso..."
        page.update()

        try:
            video_path = e.files[0].path
            
            # Carichiamo il video direttamente su Google Gemini
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Caricamento del file (Gemini estrae i frame dai suoi server)
            video_file = await asyncio.to_thread(genai.upload_file, path=video_path)
            
            prompt = f"Analizza questo video del veicolo targa {targa_input.value}. Elenca eventuali danni visivi sulla carrozzeria."
            
            # Aspettiamo l'analisi
            response = await asyncio.to_thread(model.generate_content, [prompt, video_file])
            
            result_text.value = response.text
            status_text.value = "✅ Analisi Completata"
            
            # Pulizia: eliminiamo il file dai server Google dopo l'uso
            genai.delete_file(video_file.name)

        except Exception as ex:
            status_text.value = f"❌ Errore: {str(ex)}"
        
        progress_ring.visible = False
        page.update()

    file_picker = ft.FilePicker(on_result=elabora_video)
    page.overlay.append(file_picker)

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
            ft.Container(result_text, padding=10, bgcolor="#222222", border_radius=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)