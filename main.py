import flet as ft
import asyncio
import base64

# --- CONFIGURAZIONE ---
# Metti la tua chiave qui (inizia con AIza...)
MY_KEY = "AQ.Ab8RN6LE982d9nnz62nIfIwmvCiySMUaBwfa7BtoDDkpOqnfgg" 

async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Questo deve apparire per forza se l'app funziona
    title = ft.Text("GSSA PRO - SISTEMA ATTIVO", size=25, weight="bold", color="blue")
    status = ft.Text("Pronto per l'analisi", color="white")
    result = ft.Markdown("")
    
    targa = ft.TextField(label="Inserisci Targa")

    async def avvia_perizia(e):
        if not targa.value:
            status.value = "⚠️ Inserisci la targa!"
            page.update()
            return
        
        status.value = "⏳ Caricamento video..."
        status.color = "yellow"
        page.update()

        # Carichiamo httpx solo qui per evitare crash all'avvio
        import httpx
        
        try:
            # Qui carichiamo il file scelto
            if not file_picker.result or not file_picker.result.files:
                status.value = "⚠️ Nessun video selezionato"
                page.update()
                return

            video_path = file_picker.result.files[0].path
            with open(video_path, "rb") as f:
                encoded_video = base64.b64encode(f.read()).decode("utf-8")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={MY_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"Analizza danni targa {targa.value}"},
                        {"inline_data": {"mime_type": "video/mp4", "data": encoded_video}}
                    ]
                }]
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(url, json=payload)
            
            if res.status_code == 200:
                result.value = res.json()['candidates'][0]['content']['parts'][0]['text']
                status.value = "✅ Analisi completata"
                status.color = "green"
            else:
                status.value = f"❌ Errore API: {res.status_code}"
                result.value = res.text
        
        except Exception as err:
            status.value = "❌ Errore critico"
            result.value = str(err)
        
        page.update()

    file_picker = ft.FilePicker(on_result=lambda _: None) # Gestione semplificata
    page.overlay.append(file_picker)

    page.add(
        title,
        ft.Divider(),
        targa,
        ft.ElevatedButton(
            "CARICA VIDEO", 
            icon=ft.icons.VIDEO_FILE,
            on_click=lambda _: file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO)
        ),
        ft.ElevatedButton("AVVIA ANALISI AI", on_click=avvia_perizia),
        status,
        ft.Container(result, padding=10, bgcolor="#1A1A1A", border_radius=10)
    )

if __name__ == "__main__":
    ft.app(target=main)