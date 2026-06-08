import flet as ft
import httpx
import base64

# --- CONFIGURAZIONE ---
API_KEY = "AQ.Ab8RN6LE982d9nnz62nIfIwmvCiySMUaBwfa7BtoDDkpOqnfgg" 
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

    async def al_risultato_file(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        loading.visible = True
        status.value = "⏳ Analisi Gemini 2.0 in corso..."
        page.update()

        try:
            # Lettura video dai bytes (per il Web)
            video_bytes = e.files[0].content
            video_64 = base64.b64encode(video_bytes).decode("utf-8")

            corpo_richiesta = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza danni carrozzeria targa {targa.value}"},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_64}}
                    ]
                }]
            }

            async with httpx.AsyncClient(timeout=180.0) as client:
                res = await client.post(URL, json=corpo_richiesta)
            
            if res.status_code == 200:
                dati = res.json()
                risultato.value = dati['candidates'][0]['content']['parts'][0]['text']
                status.value = "✅ Analisi Completata"
            else:
                status.value = f"❌ Errore API Google: {res.status_code}"
                risultato.value = res.text

        except Exception as err:
            status.value = "❌ Errore critico"
            risultato.value = str(err)
        
        loading.visible = False
        page.update()

    # --- CORREZIONE FILEPICKER ---
    # Definiamo il selettore e lo aggiungiamo all'overlay PRIMA di usarlo
    selettore = ft.FilePicker(on_result=al_risultato_file)
    page.overlay.append(selettore)

    page.add(
        ft.Text("GSSA PRO", size=35, weight="bold", color="blue"),
        ft.Text("Powered by Gemini 2.0 Flash", size=12, italic=True),
        ft.Divider(),
        targa,
        ft.ElevatedButton(
            "CARICA VIDEO PERIZIA", 
            # --- CORREZIONE ERRORE ICONA ---
            # VIDEO_CAMERA_FRONT non esiste, usiamo VIDEOCAM
            icon=ft.icons.VIDEOCAM, 
            on_click=lambda _: selettore.pick_files(file_type=ft.FilePickerFileType.VIDEO)
        ),
        loading,
        status,
        ft.Container(risultato, padding=15, bgcolor="#1A1A1A", border_radius=10)
    )

# --- CORREZIONE DEPRECATION WARNING ---
if __name__ == "__main__":
    ft.app(main) # Rimosso target= per seguire le nuove linee guida
