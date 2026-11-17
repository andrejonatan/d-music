import os
import uuid
import yt_dlp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Izinkan semua frontend (termasuk Vercel nanti) mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def hapus_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/")
def cek_server():
    return {"status": "Server d-music aktif!"}

@app.get("/download")
def download_mp3(url: str, background_tasks: BackgroundTasks):
    if not url:
        raise HTTPException(status_code=400, detail="URL YouTube wajib diisi!")

    # Bikin nama file acak biar nggak bentrok kalau ada banyak user
    file_id = str(uuid.uuid4())
    output_template = f"/tmp/{file_id}.%(ext)s"
    final_mp3_path = f"/tmp/{file_id}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            judul = info.get('title', 'audio')
            # Bersihin karakter aneh dari judul lagu biar aman buat nama file
            judul_aman = "".join([c for c in judul if c.isalnum() or c in (' ', '-', '_')]).rstrip()

        if not os.path.exists(final_mp3_path):
            raise HTTPException(status_code=500, detail="Gagal mengonversi ke MP3.")

        # Jadwalkan penghapusan file segera setelah selesai dikirim ke user
        background_tasks.add_task(hapus_file, final_mp3_path)

        return FileResponse(
            path=final_mp3_path,
            media_type="audio/mpeg",
            filename=f"{judul_aman}.mp3"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")