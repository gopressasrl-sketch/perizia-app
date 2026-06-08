import flet as ft
import httpx
import base64

# --- CONFIGURAZIONE ---
# NOTA: Fai attenzione a non condividere la chiave API pubblicamente
API_KEY = "AQ.Ab8RN6LE982d9nnz62nIfIwmvCiySMUaBwfa7BtoDDkpOqnfgg" 
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    targa = ft.TextField(label="Targa Veicolo", border_color="blue", text_align=ft.TextAlign.CENTER)
    status = ft.Text("")
    risultato = ft.Markdown("", selectable=True)
    loading = ft.ProgressRing(visible=False)

    async def al_risultato_file(e: ft.FilePickerResultEvent):
        if not e.files or len(e.files) == 0:
            return
        
        loading.visible = True
        status.value = "⏳ Analisi Gemini 2.0 in corso... Attendi."
        status.color = ft.colors.BLUE_200
        page.update()

        try:
            # Lettura video dai bytes (funziona su Flet Web/Pyodide)
            video_bytes = e.files[0].content
            if video_bytes is None:
                status.value = "❌ Errore: Impossibile leggere il file (bytes vuoti)"
                loading.visible = False
                page.update()
                return

            video_64 = base64.b64encode(video_bytes).decode("utf-8")

            corpo_richiesta = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza dettagliatamente i danni alla carrozzeria del veicolo con targa {targa.value}. Elenca i componenti danneggiati e stima l'entità."},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_64}}
                    ]
                }]
            }

            # Timeout lungo perché i video richiedono tempo per l'elaborazione lato server
            async with httpx.AsyncClient(timeout=180.0) as client:
                res = await client.post(URL, json=corpo_richiesta)
            
            if res.status_code == 200:
                dati = res.json()
                testo_risposta = dati['candidates'][0]['content']['parts'][0]['text']
                risultato.value = testo_risposta
                status.value = "✅ Analisi Completata"
                status.color = ft.colors.GREEN
            else:
                status.value = f"❌ Errore API Google: {res.status_code}"
                status.color = ft.colors.RED
                risultato.value = res.text

        except Exception as err:
            status.value = "❌ Errore critico durante l'invio"
            status.color = ft.colors.RED
            risultato.value = str(err)
        
        loading.visible = False
        page.update()

    # --- CORREZIONE ERRORI ---
    
    # 1. Inizializzazione FilePicker correttamente nell'overlay
    selettore = ft.FilePicker(on_result=al_risultato_file)
    page.overlay.append(selettore)

    page.add(
        ft.Text("GSSA PRO", size=35, weight="bold", color="blue"),
        ft.Text("Powered by Gemini 2.0 Flash", size=12, italic=True),
        ft.Divider(),
        targa,
        ft.ElevatedButton(
            "CARICA VIDEO PERIZIA", 
            # 2. Correzione Icona: VIDEO_CAMERA_FRONT non esiste in tutte le versioni, uso VIDEOCAM
            icon=ft.icons.VIDEOCAM,
            on_click=lambda _: selettore.pick_files(
                file_type=ft.FilePickerFileType.VIDEO,
                allow_multiple=False
            ),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        ),
        ft.VerticalDivider(height=10, color=ft.colors.TRANSPARENT),
        loading,
        status,
        ft.Container(
            content=risultato,
            padding=15,
            bgcolor="#1A1A1A",
            border_radius=10,
            expand=True,
            width=600
        )
    )
    page.update()

# 3. Avvio corretto (senza target= per evitare DeprecationWarning)
if __name__ == "__main__":
    ft.app(main)
