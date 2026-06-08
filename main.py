import flet as ft
import httpx
import base64
import asyncio
import os

# --- CONFIGURAZIONE ---
# Inserisci qui la tua chiave API (deve iniziare con AIza...)
GEMINI_KEY = "AQ.Ab8RN6KQaP84VAzm3m1kcEwFRKRxAy6fo8YSdolx9mHb_Rbu3Q" 

# URL aggiornato per usare il modello Gemini 2.0 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

async def main(page: ft.Page):
    # Protezione anti-schermo bianco: tutto dentro un try/except
    try:
        page.title = "GSSA PRO - Gemini 2.0 Flash"
        page.theme_mode = ft.ThemeMode.DARK
        page.scroll = ft.ScrollMode.ADAPTIVE
        page.padding = 20

        # Elementi dell'interfaccia
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
            status_text.value = "🚀 Analisi con Gemini 2.0 Flash in corso..."
            status_text.color = "blue"
            page.update()

            try:
                # 1. Lettura video e conversione in Base64
                with open(video_path, "rb") as video_file:
                    video_data = base64.b64encode(video_file.read()).decode("utf-8")

                # 2. Payload per Gemini 2.0 Flash
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"Agisci come un perito assicurativo esperto. Analizza questo video del veicolo targa {targa_input.value}. Elenca dettagliatamente ogni danno visibile sulla carrozzeria, graffi, ammaccature o parti mancanti."},
                            {
                                "inline_data": {
                                    "mime_type": "video/mp4",
                                    "data": video_data
                                }
                            }
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.2, # Più basso è, più è preciso l'esito
                        "topP": 0.8,
                        "topK": 40
                    }
                }

                # 3. Chiamata API (timeout aumentato a 120 secondi per video pesanti)
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(API_URL, json=payload)
                    
                if response.status_code == 200:
                    data = response.json()
                    # Estraiamo il testo della risposta
                    testo_risposta = data['candidates'][0]['content']['parts'][0]['text']
                    result_text.value = testo_risposta
                    status_text.value = "✅ Analisi Professionale Completata"
                    status_text.color = "green"
                else:
                    status_text.value = f"❌ Errore API Google: {response.status_code}"
                    status_text.color = "red"
                    result_text.value = response.text

            except Exception as ex:
                status_text.value = "❌ Errore durante l'analisi"
                status_text.color = "red"
                result_text.value = f"Dettaglio errore: {str(ex)}"
            
            progress_ring.visible = False
            page.update()

        # Configurazione del selettore file
        file_picker = ft.FilePicker(on_result=elabora_video)
        page.overlay.append(file_picker)

        # Costruzione della pagina
        page.add(
            ft.Column([
                ft.Text("GSSA PRO", size=30, weight="bold", color="blue"),
                ft.Text("Powered by Gemini 2.0 Flash", size=12, italic=True),
                ft.Divider(),
                targa_input,
                ft.ElevatedButton(
                    "CARICA VIDEO PERIZIA", 
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

    except Exception as fatal_error:
        # Se l'app crasha all'avvio, mostra l'errore invece del bianco
        page.add(ft.Text(f"ERRORE CRITICO AVVIO: {str(fatal_error)}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
