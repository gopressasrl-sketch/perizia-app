import flet as ft
import httpx
import base64

# --- CONFIGURAZIONE ---
API_KEY = "AQ.Ab8RN6LE982d9nnz62nIfIwmvCiySMUaBwfa7BtoDDkpOqnfgg" 
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

async def main(page: ft.Page):
    page.title = "GSSA PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE # Aggiunto per scorrere i risultati lunghi

    targa = ft.TextField(label="Targa Veicolo", border_color="blue", width=300)
    status = ft.Text("", color=ft.colors.AMBER)
    risultato = ft.Markdown("", selectable=True)
    loading = ft.ProgressRing(visible=False)

    async def al_risultato_file(e):
        if not e.files:
            return
        
        loading.visible = True
        status.value = "⏳ Elaborazione video in corso con Gemini 2.0..."
        page.update()

        try:
            # Su Web i byte sono contenuti in e.files[0].content
            video_bytes = e.files[0].content
            video_64 = base64.b64encode(video_bytes).decode("utf-8")

            corpo = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza danni carrozzeria veicolo targa {targa.value}"},
                        {"inline_data": {"mime_type": "video/mp4", "data": video_64}}
                    ]
                }]
            }

            async with httpx.AsyncClient(timeout=300.0) as client:
                res = await client.post(URL, json=corpo)
            
            if res.status_code == 200:
                dati = res.json()
                risultato.value = dati['candidates'][0]['content']['parts'][0]['text']
                status.value = "✅ Analisi Completata"
            else:
                status.value = f"❌ Errore API Google: {res.status_code}"
                risultato.value = res.text

        except Exception as err:
            status.value = "❌ Errore tecnico"
            risultato.value = str(err)
        
        loading.visible = False
        page.update()

    # --- RISOLUZIONE ERRORE "UNKNOWN CONTROL" ---
    # Creiamo il selettore e assegniamo l'evento in modo pulito
    selettore = ft.FilePicker(on_result=al_risultato_file)
    page.overlay.append(selettore)

    # --- RISOLUZIONE ERRORE "NEVER AWAITED" ---
    # Questa funzione deve essere ASYNC per funzionare nel web worker
    async def apri_selettore(e):
        await selettore.pick_files(file_type=ft.FilePickerFileType.VIDEO)

    page.add(
        ft.Text("GSSA PRO", size=40, weight="bold", color="blue"),
        ft.Text("Intelligenza Artificiale per Perizie Video", size=14, italic=True),
        ft.Divider(),
        targa,
        ft.ElevatedButton(
            "CARICA VIDEO PERIZIA", 
            icon=ft.icons.VIDEOCAM,
            on_click=apri_selettore # Usiamo la funzione async invece di lambda
        ),
        loading,
        status,
        ft.Container(
            content=risultato, 
            padding=20, 
            bgcolor="#1e1e1e", 
            border_radius=10,
            width=700
        )
    )
    # Update finale per forzare il caricamento dell'overlay
    page.update()

if __name__ == "__main__":
    ft.app(main)
