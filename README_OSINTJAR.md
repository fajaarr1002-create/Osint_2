# OSINTJAR v1.0
**Developer:** Pajar | **Platform:** Termux / Linux | **Language:** Python 3.12

---

## Instalasi di Termux

```bash
# 1. Update & install dependencies
pkg update && pkg upgrade -y
pkg install python -y
pkg install git -y

# 2. Install library Python
pip install rich requests phonenumbers

# 3. Jalankan
python osintjar.py
```

---

## Struktur File

```
/folder-kamu/
├── osintjar.py     ← File utama (wajib)
├── dork.py         ← Tambahkan sendiri (opsional, untuk menu 07)
└── dos.py          ← Tambahkan sendiri (opsional, untuk menu 08)
```

> **Catatan:** `dork.py` dan `dos.py` harus berada di folder yang **sama** dengan `osintjar.py`.

---

## Menu

| No | Fitur | Keterangan |
|----|-------|------------|
| 01 | Phone OSINT | Analisis nomor telepon |
| 02 | IP OSINT | Info detail IP address |
| 03 | My IP | Deteksi IP publik sendiri |
| 04 | Username Finder | Cek 14 platform |
| 05 | Social Media Finder | Cek 20 platform sosmed |
| 06 | Email OSINT | Analisis email & domain |
| 07 | UltraDork | Launcher dork.py |
| 08 | UltraDOS | Launcher dos.py |
| 09 | About | Info tools |

---

## Dependencies

- `rich` — tampilan terminal modern
- `requests` — HTTP requests
- `phonenumbers` — analisis nomor telepon
- `socket`, `os`, `json`, `time` — stdlib Python (sudah built-in)

> Auto-install dijalankan saat program pertama kali dibuka.
