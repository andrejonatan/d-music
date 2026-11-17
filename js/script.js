// GANTI URL DI BAWAH INI DENGAN URL RENDER LU NANTI (tanpa garis miring di akhir)
const BACKEND_URL = "http://localhost:8000"; 

async function downloadLagu() {
  const urlInput = document.getElementById("ytUrl").value.trim();
  const btn = document.getElementById("btnDownload");
  const statusText = document.getElementById("statusText");

  if (!urlInput) {
    statusText.className = "status error";
    statusText.innerText = "Masukkan link YouTube-nya dulu, bre!";
    return;
  }

  // Kunci tombol & kasih info proses
  btn.disabled = true;
  btn.innerText = "Memproses...";
  statusText.className = "status loading";
  statusText.innerText = "Sedang mengonversi audio... (bisa makan waktu 15-40 detik)";

  try {
    const response = await fetch(`${BACKEND_URL}/download?url=${encodeURIComponent(urlInput)}`);

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || "Gagal memproses video.");
    }

    // Ambil nama file dari header backend
    const disposition = response.headers.get('Content-Disposition');
    let filename = "lagu.mp3";
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/["']/g, '');
    }

    // Ubah response jadi file download di browser
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(downloadUrl);

    statusText.className = "status success";
    statusText.innerText = "Berhasil! Lagu sedang diunduh.";
  } catch (error) {
    statusText.className = "status error";
    statusText.innerText = `Error: ${error.message}`;
  } finally {
    btn.disabled = false;
    btn.innerText = "Download MP3";
  }
}