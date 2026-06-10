#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                        OSINTJAR v1.0                         ║
║              Professional OSINT Tool for Termux              ║
║                     Developer: Pajar                         ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─── Standard Library Imports ────────────────────────────────────────────────
import os
import sys
import json
import time
import socket
import platform
import subprocess
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ─── Dependency Check & Install ──────────────────────────────────────────────
def check_and_install(package_name, import_name=None):
    """Auto-install missing packages."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Installing {package_name}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name, "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

# Check semua dependencies sebelum import
check_and_install("rich")
check_and_install("requests")
check_and_install("phonenumbers")

# ─── Third Party Imports ──────────────────────────────────────────────────────
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone as pn_timezone

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt
from rich.align import Align
from rich import box
from rich.columns import Columns
from rich.live import Live
from rich.rule import Rule
from rich.markup import escape

# ─── Global Console ───────────────────────────────────────────────────────────
console = Console()

# ─── Warna Tema Merah & Hijau ─────────────────────────────────────────────────
RED       = "bold red"
GREEN     = "bold green"
YELLOW    = "bold yellow"
CYAN      = "bold cyan"
WHITE     = "bold white"
DIM       = "dim white"
RED_DIM   = "red"
GREEN_DIM = "green"

# ─── ASCII Banner ─────────────────────────────────────────────────────────────
BANNER = r"""

    ____  _____ _____   ________  _____    ____         
  / __ \/ ___//  _/ | / /_  __/ / /   |  / __ \        
 / / / /\__ \ / //  |/ / / /_  / / /| | / /_/ /        
/ /_/ /___/ // // /|  / / / /_/ / ___ |/ _, _/         
\____//____/___/_/ |_/ /_/\____/_/  |_/_/ |_|          
                                                          
"""

# ─── Utility Functions ────────────────────────────────────────────────────────

def clear_screen():
    """Bersihkan layar terminal."""
    os.system("clear" if os.name != "nt" else "cls")

def show_banner():
    """Tampilkan banner ASCII dengan warna tema merah-hijau."""
    clear_screen()
    # Banner merah menyala
    banner_text = Text(BANNER)
    banner_text.stylize("bold red")
    console.print(Align.center(banner_text))

    # Info baris bawah banner
    info_line = Text()
    info_line.append("  Version: ", style=DIM)
    info_line.append("1.0", style=GREEN)
    info_line.append("  |  Developer: ", style=DIM)
    info_line.append("Pajar", style=RED)
    info_line.append("  |  Platform: ", style=DIM)
    info_line.append("Termux / Linux", style=GREEN)
    console.print(Align.center(info_line))
    console.print()

def show_separator(color="red"):
    """Tampilkan garis pemisah berwarna."""
    console.print(Rule(style=color))

def show_menu():
    """Tampilkan menu utama."""
    show_banner()
    show_separator("red")

    # Tabel menu
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        expand=False
    )
    table.add_column("Num",  style="bold red",   no_wrap=True, width=6)
    table.add_column("Name", style="bold white",  no_wrap=True, width=30)
    table.add_column("Desc", style="dim green",   no_wrap=False)

    menu_items = [
        ("[ 01 ]", "OSINT Nomor Telepon / WhatsApp", "↳ Informasi detail nomor telepon"),
        ("[ 02 ]", "OSINT IP Address",               "↳ Informasi detail alamat IP"),
        ("[ 03 ]", "My IP Information",               "↳ Informasi IP publik sendiri"),
        ("[ 04 ]", "Username Finder",                 "↳ Pencarian username lintas platform"),
        ("[ 05 ]", "Multi Social Media Finder",       "↳ Cek username di berbagai sosial media"),
        ("[ 06 ]", "OSINT Gmail / Email",             "↳ Analisis email dan domain"),
        ("[ 07 ]", "UltraDork",                       "↳ Menjalankan modul dork.py"),
        ("[ 08 ]", "UltraDOS",                        "↳ Menjalankan modul dos.py"),
        ("[ 09 ]", "About",                            "↳ Informasi tools"),
        ("[ 00 ]", "Exit",                             "↳ Keluar dari program"),
    ]

    for num, name, desc in menu_items:
        table.add_row(num, name, desc)

    panel = Panel(
        Align.center(table),
        title="[bold red]  MENU UTAMA  [/bold red]",
        border_style="red",
        padding=(1, 4)
    )
    console.print(panel)
    show_separator("red")

def press_enter():
    """Tunggu user tekan Enter."""
    console.print()
    console.print("  [dim]Tekan [bold green]Enter[/bold green] untuk kembali ke menu...[/dim]")
    input()

def loading_spinner(message: str, seconds: float = 1.5):
    """Tampilkan spinner loading dengan pesan."""
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold red"),
        TextColumn(f"[bold green]{message}[/bold green]"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("", total=None)
        time.sleep(seconds)

def show_result_panel(title: str, content, border_color="green"):
    """Tampilkan panel hasil dengan border berwarna."""
    panel = Panel(
        content,
        title=f"[bold {border_color}]  {title}  [/bold {border_color}]",
        border_style=border_color,
        padding=(1, 2)
    )
    console.print(panel)

def safe_get(url: str, timeout: int = 10, headers: dict = None) -> dict | None:
    """HTTP GET request dengan error handling lengkap."""
    try:
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"
        }
        if headers:
            default_headers.update(headers)
        response = requests.get(url, timeout=timeout, headers=default_headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        console.print("  [bold red][!] Tidak ada koneksi internet.[/bold red]")
    except requests.exceptions.Timeout:
        console.print("  [bold red][!] Request timeout.[/bold red]")
    except Exception as e:
        console.print(f"  [bold red][!] Error: {escape(str(e))}[/bold red]")
    return None

def check_url_exists(url: str, timeout: int = 6) -> bool:
    """Cek apakah URL mengembalikan status 200."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)"}
        r = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        return r.status_code in [200, 301, 302]
    except Exception:
        return False

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 1 — OSINT NOMOR TELEPON
# ══════════════════════════════════════════════════════════════════════════════

def feature_phone_osint():
    """Analisis nomor telepon menggunakan library phonenumbers."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  OSINT NOMOR TELEPON / WHATSAPP  [/bold red]",
        border_style="red"
    ))
    console.print()

    nomor_input = Prompt.ask("  [bold green]Masukkan Nomor Telepon[/bold green] [dim](contoh: +6281234567890)[/dim]")
    console.print()
    loading_spinner("Menganalisis nomor telepon...", 1.8)

    try:
        # Parse nomor telepon
        parsed = phonenumbers.parse(nomor_input)
        is_valid   = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)

        negara    = geocoder.description_for_number(parsed, "id") or "Tidak diketahui"
        operator  = carrier.name_for_number(parsed, "id") or "Tidak diketahui"
        timezones = pn_timezone.time_zones_for_number(parsed)
        tz_str    = ", ".join(timezones) if timezones else "Tidak diketahui"

        fmt_nasional      = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        fmt_internasional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164          = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        # Jenis nomor
        num_type_raw = phonenumbers.number_type(parsed)
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE:       "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE:   "Fixed Line",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed/Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE:    "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.VOIP:         "VOIP",
            phonenumbers.PhoneNumberType.UNKNOWN:      "Unknown",
        }
        jenis_nomor = type_map.get(num_type_raw, "Unknown")

        # Kode negara
        kode_negara = f"+{parsed.country_code}"
        negara_code = phonenumbers.region_code_for_number(parsed)

        # Tabel hasil
        table = Table(
            show_header=True,
            header_style="bold red",
            box=box.SIMPLE_HEAVY,
            border_style="green",
            padding=(0, 2)
        )
        table.add_column("Field",  style="bold green", no_wrap=True, width=26)
        table.add_column("Value",  style="white",      no_wrap=False)

        status_str = "[bold green]✓ VALID[/bold green]" if is_valid else "[bold red]✗ TIDAK VALID[/bold red]"

        rows = [
            ("Nomor Input",           escape(nomor_input)),
            ("Format E.164",          escape(fmt_e164)),
            ("Format Nasional",       escape(fmt_nasional)),
            ("Format Internasional",  escape(fmt_internasional)),
            ("Kode Negara",           escape(kode_negara)),
            ("Kode Region",           escape(negara_code or "N/A")),
            ("Negara / Lokasi",       escape(negara)),
            ("Operator / Carrier",    escape(operator)),
            ("Jenis Nomor",           escape(jenis_nomor)),
            ("Timezone",              escape(tz_str)),
            ("Status Validitas",      status_str),
            ("Kemungkinan Valid",      "[green]Ya[/green]" if is_possible else "[red]Tidak[/red]"),
        ]

        for field, val in rows:
            table.add_row(field, val)

        # WhatsApp link
        nomor_wa = fmt_e164.replace("+", "")
        wa_link = f"https://wa.me/{nomor_wa}"
        table.add_row("WhatsApp Link", f"[bold cyan]{escape(wa_link)}[/bold cyan]")

        show_result_panel("HASIL ANALISIS NOMOR TELEPON", table, "green")

    except phonenumbers.NumberParseException as e:
        console.print(f"\n  [bold red][!] Gagal memparse nomor: {escape(str(e))}[/bold red]")
        console.print("  [dim]Pastikan nomor menggunakan kode negara, contoh: +6281234567890[/dim]")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 2 — OSINT IP ADDRESS
# ══════════════════════════════════════════════════════════════════════════════

def display_ip_info(data: dict, ip_input: str = ""):
    """Render tabel informasi IP dari data dict."""
    table = Table(
        show_header=True,
        header_style="bold red",
        box=box.SIMPLE_HEAVY,
        border_style="green",
        padding=(0, 2)
    )
    table.add_column("Field",  style="bold green", no_wrap=True, width=22)
    table.add_column("Value",  style="white",      no_wrap=False)

    ip       = data.get("query") or data.get("ip") or ip_input
    negara   = data.get("country") or data.get("country_name", "N/A")
    kota     = data.get("city", "N/A")
    region   = data.get("regionName") or data.get("region", "N/A")
    isp      = data.get("isp") or data.get("org", "N/A")
    asn      = data.get("as") or data.get("asn", "N/A")
    tz       = data.get("timezone", "N/A")
    lat      = data.get("lat") or data.get("latitude", "N/A")
    lon      = data.get("lon") or data.get("longitude", "N/A")
    postal   = data.get("zip") or data.get("postal", "N/A")
    org      = data.get("org", "N/A")

    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat != "N/A" else "N/A"

    rows = [
        ("IP Address",      escape(str(ip))),
        ("Negara",          escape(str(negara))),
        ("Kota",            escape(str(kota))),
        ("Region",          escape(str(region))),
        ("ISP",             escape(str(isp))),
        ("Organisasi",      escape(str(org))),
        ("ASN",             escape(str(asn))),
        ("Timezone",        escape(str(tz))),
        ("Latitude",        escape(str(lat))),
        ("Longitude",       escape(str(lon))),
        ("Kode Pos",        escape(str(postal))),
        ("Google Maps",     f"[bold cyan]{escape(str(maps_link))}[/bold cyan]"),
    ]

    for field, val in rows:
        table.add_row(field, val)

    show_result_panel(f"HASIL OSINT IP — {ip}", table, "green")

def feature_ip_osint():
    """OSINT IP Address menggunakan API publik ip-api.com."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  OSINT IP ADDRESS  [/bold red]",
        border_style="red"
    ))
    console.print()

    ip_input = Prompt.ask("  [bold green]Masukkan IP Address[/bold green] [dim](contoh: 8.8.8.8)[/dim]")
    ip_input = ip_input.strip()
    console.print()
    loading_spinner("Mengambil informasi IP...", 2.0)

    # Coba ip-api.com dulu, fallback ke ipapi.co
    url = f"http://ip-api.com/json/{ip_input}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    data = safe_get(url)

    if data and data.get("status") == "success":
        display_ip_info(data, ip_input)
    else:
        # Fallback
        url2 = f"https://ipapi.co/{ip_input}/json/"
        data2 = safe_get(url2)
        if data2 and not data2.get("error"):
            display_ip_info(data2, ip_input)
        else:
            console.print(f"  [bold red][!] Gagal mendapatkan info untuk IP: {escape(ip_input)}[/bold red]")
            console.print("  [dim]Pastikan IP valid dan koneksi internet aktif.[/dim]")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 3 — MY IP INFORMATION
# ══════════════════════════════════════════════════════════════════════════════

def feature_my_ip():
    """Deteksi dan tampilkan informasi IP publik pengguna."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  MY IP INFORMATION  [/bold red]",
        border_style="red"
    ))
    console.print()
    loading_spinner("Mendeteksi IP publik Anda...", 2.0)

    url = "http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    data = safe_get(url)

    if data and data.get("status") == "success":
        display_ip_info(data)
    else:
        url2 = "https://ipapi.co/json/"
        data2 = safe_get(url2)
        if data2 and not data2.get("error"):
            display_ip_info(data2)
        else:
            console.print("  [bold red][!] Gagal mendeteksi IP publik.[/bold red]")
            console.print("  [dim]Periksa koneksi internet Anda.[/dim]")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 4 — USERNAME FINDER
# ══════════════════════════════════════════════════════════════════════════════

# Daftar platform untuk Username Finder
USERNAME_PLATFORMS = {
    "GitHub":      "https://github.com/{}",
    "GitLab":      "https://gitlab.com/{}",
    "Reddit":      "https://www.reddit.com/user/{}",
    "Medium":      "https://medium.com/@{}",
    "Pinterest":   "https://www.pinterest.com/{}/",
    "Twitch":      "https://www.twitch.tv/{}",
    "Steam":       "https://steamcommunity.com/id/{}",
    "Tumblr":      "https://{}.tumblr.com",
    "Flickr":      "https://www.flickr.com/people/{}/",
    "VK":          "https://vk.com/{}",
    "SoundCloud":  "https://soundcloud.com/{}",
    "DeviantArt":  "https://www.deviantart.com/{}",
    "Replit":      "https://replit.com/@{}",
    "ProductHunt": "https://www.producthunt.com/@{}",
}

def feature_username_finder():
    """Cek ketersediaan username di berbagai platform."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  USERNAME FINDER  [/bold red]",
        border_style="red"
    ))
    console.print()

    username = Prompt.ask("  [bold green]Masukkan Username[/bold green]")
    username = username.strip()
    console.print()

    found_list = []
    not_found_list = []

    table = Table(
        show_header=True,
        header_style="bold red",
        box=box.SIMPLE_HEAVY,
        border_style="green",
        padding=(0, 1)
    )
    table.add_column("Status",   style="bold",   no_wrap=True, width=6)
    table.add_column("Platform", style="bold white", no_wrap=True, width=14)
    table.add_column("URL",      style="cyan",   no_wrap=False)

    total = len(USERNAME_PLATFORMS)

    with Progress(
        SpinnerColumn(spinner_name="dots2", style="bold red"),
        TextColumn("[bold green]Memeriksa platform... [/bold green]"),
        BarColumn(bar_width=30, style="red", complete_style="green"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("", total=total)

        for platform, url_template in USERNAME_PLATFORMS.items():
            url = url_template.format(username)
            exists = check_url_exists(url)

            if exists:
                status = "[bold green]  ✓[/bold green]"
                found_list.append((platform, url))
                table.add_row(status, platform, url)
            else:
                status = "[bold red]  ✗[/bold red]"
                not_found_list.append(platform)
                table.add_row(status, platform, "[dim]Tidak ditemukan[/dim]")

            progress.update(task, advance=1)
            time.sleep(0.3)  # hindari rate limit

    show_result_panel(f"HASIL USERNAME FINDER — {escape(username)}", table, "green")

    # Ringkasan
    console.print()
    console.print(f"  [bold green]✓ Ditemukan   : {len(found_list)} platform[/bold green]")
    console.print(f"  [bold red]✗ Tidak Ditemukan: {len(not_found_list)} platform[/bold red]")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 5 — MULTI SOCIAL MEDIA FINDER
# ══════════════════════════════════════════════════════════════════════════════

# Daftar platform sosial media (lebih luas dari username finder)
SOCIAL_PLATFORMS = {
    "TikTok":     "https://www.tiktok.com/@{}",
    "Instagram":  "https://www.instagram.com/{}/",
    "Facebook":   "https://www.facebook.com/{}/",
    "X/Twitter":  "https://twitter.com/{}",
    "YouTube":    "https://www.youtube.com/@{}",
    "Telegram":   "https://t.me/{}",
    "Snapchat":   "https://www.snapchat.com/add/{}",
    "Threads":    "https://www.threads.net/@{}",
    "LinkedIn":   "https://www.linkedin.com/in/{}/",
    "Pinterest":  "https://www.pinterest.com/{}/",
    "GitHub":     "https://github.com/{}",
    "Reddit":     "https://www.reddit.com/user/{}",
    "Twitch":     "https://www.twitch.tv/{}",
    "Steam":      "https://steamcommunity.com/id/{}",
    "Tumblr":     "https://{}.tumblr.com",
    "SoundCloud": "https://soundcloud.com/{}",
    "VK":         "https://vk.com/{}",
    "Medium":     "https://medium.com/@{}",
    "Flickr":     "https://www.flickr.com/people/{}/",
    "DeviantArt": "https://www.deviantart.com/{}",
}

def feature_social_finder():
    """Cek username di berbagai platform sosial media."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  MULTI SOCIAL MEDIA FINDER  [/bold red]",
        border_style="red"
    ))
    console.print()

    username = Prompt.ask("  [bold green]Masukkan Username[/bold green]")
    username = username.strip()
    console.print()

    found_list = []
    not_found_list = []
    total = len(SOCIAL_PLATFORMS)

    results = []  # Simpan sementara untuk tampilan setelah selesai

    with Progress(
        SpinnerColumn(spinner_name="dots12", style="bold red"),
        TextColumn("[bold green]Mencari akun... [/bold green]"),
        BarColumn(bar_width=28, style="red", complete_style="green"),
        TextColumn("[bold white]{task.completed}/{task.total}[/bold white]"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("", total=total)

        for platform, url_template in SOCIAL_PLATFORMS.items():
            url = url_template.format(username)
            exists = check_url_exists(url)

            results.append((platform, url, exists))
            if exists:
                found_list.append((platform, url))
            else:
                not_found_list.append(platform)

            progress.update(task, advance=1)
            time.sleep(0.3)

    # Tabel hasil
    table = Table(
        show_header=True,
        header_style="bold red",
        box=box.SIMPLE_HEAVY,
        border_style="green",
        padding=(0, 1)
    )
    table.add_column("Status",   style="bold",      no_wrap=True, width=6)
    table.add_column("Platform", style="bold white", no_wrap=True, width=14)
    table.add_column("URL",      style="cyan",      no_wrap=False)

    for platform, url, exists in results:
        if exists:
            table.add_row("[bold green]  ✓[/bold green]", platform, url)
        else:
            table.add_row("[bold red]  ✗[/bold red]", platform, "[dim]Tidak ditemukan[/dim]")

    show_result_panel(f"HASIL SOCIAL MEDIA FINDER — {escape(username)}", table, "green")

    # Ringkasan statistik
    console.print()
    ringkasan = Table(show_header=False, box=None, padding=(0, 4))
    ringkasan.add_column("k", style="bold")
    ringkasan.add_column("v", style="bold")
    ringkasan.add_row("[bold green]✓ Akun Ditemukan   :[/bold green]",
                      f"[bold green]{len(found_list)} / {total}[/bold green]")
    ringkasan.add_row("[bold red]✗ Tidak Ditemukan  :[/bold red]",
                      f"[bold red]{len(not_found_list)} / {total}[/bold red]")
    console.print(Align.center(ringkasan))

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 6 — OSINT GMAIL / EMAIL
# ══════════════════════════════════════════════════════════════════════════════

def validate_email_basic(email: str) -> bool:
    """Validasi format email sederhana."""
    if "@" not in email or "." not in email.split("@")[-1]:
        return False
    parts = email.split("@")
    return len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 3

def check_mx_record(domain: str) -> str:
    """Cek MX record domain menggunakan socket / DNS lookup dasar."""
    try:
        socket.getaddrinfo(domain, None)
        return "Aktif (Domain dapat di-resolve)"
    except socket.gaierror:
        return "Tidak Aktif / Domain tidak ditemukan"

def check_gravatar(email: str) -> str:
    """Cek keberadaan Gravatar untuk email."""
    import hashlib
    email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
    try:
        r = requests.head(url, timeout=6)
        return "✓ Ditemukan" if r.status_code == 200 else "✗ Tidak ditemukan"
    except Exception:
        return "Tidak dapat dicek"

def get_email_provider(domain: str) -> str:
    """Identifikasi provider email dari domain."""
    providers = {
        "gmail.com":     "Google Gmail",
        "yahoo.com":     "Yahoo Mail",
        "outlook.com":   "Microsoft Outlook",
        "hotmail.com":   "Microsoft Hotmail",
        "live.com":      "Microsoft Live",
        "icloud.com":    "Apple iCloud",
        "protonmail.com":"ProtonMail",
        "proton.me":     "ProtonMail",
        "zoho.com":      "Zoho Mail",
        "yandex.com":    "Yandex Mail",
        "mail.com":      "Mail.com",
    }
    return providers.get(domain.lower(), f"Custom / Unknown ({domain})")

def feature_email_osint():
    """Analisis dan OSINT email/Gmail."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  OSINT GMAIL / EMAIL  [/bold red]",
        border_style="red"
    ))
    console.print()

    email_input = Prompt.ask("  [bold green]Masukkan Email[/bold green] [dim](contoh: user@gmail.com)[/dim]")
    email_input = email_input.strip().lower()
    console.print()
    loading_spinner("Menganalisis email...", 2.0)

    # Validasi dasar
    is_valid = validate_email_basic(email_input)

    if not is_valid:
        console.print(f"  [bold red][!] Format email tidak valid: {escape(email_input)}[/bold red]")
        press_enter()
        return

    username_email = email_input.split("@")[0]
    domain = email_input.split("@")[1]
    provider = get_email_provider(domain)

    # Cek domain status
    domain_status = check_mx_record(domain)

    # Cek Gravatar
    loading_spinner("Memeriksa Gravatar...", 1.0)
    gravatar_status = check_gravatar(email_input)

    # Cek GitHub (public API)
    loading_spinner("Memeriksa GitHub...", 1.0)
    github_status = "✗ Tidak ditemukan"
    github_url = ""
    try:
        gh_data = safe_get(f"https://api.github.com/search/users?q={email_input}+in:email", timeout=8)
        if gh_data and gh_data.get("total_count", 0) > 0:
            gh_user = gh_data["items"][0]["login"]
            github_url = f"https://github.com/{gh_user}"
            github_status = f"✓ Ditemukan — {github_url}"
    except Exception:
        github_status = "Tidak dapat dicek"

    # Cek Reddit
    loading_spinner("Memeriksa Reddit...", 1.0)
    reddit_status = "✗ Tidak ditemukan"
    try:
        rd_url = f"https://www.reddit.com/user/{username_email}/about.json"
        rd_data = safe_get(rd_url, timeout=8)
        if rd_data and rd_data.get("kind") == "t2":
            reddit_status = f"✓ Ditemukan — https://reddit.com/u/{username_email}"
    except Exception:
        reddit_status = "Tidak dapat dicek"

    # Tabel hasil utama
    table_info = Table(
        show_header=True,
        header_style="bold red",
        box=box.SIMPLE_HEAVY,
        border_style="green",
        padding=(0, 2)
    )
    table_info.add_column("Field",  style="bold green", no_wrap=True, width=22)
    table_info.add_column("Value",  style="white",      no_wrap=False)

    status_val = "[bold green]✓ VALID[/bold green]" if is_valid else "[bold red]✗ TIDAK VALID[/bold red]"
    mx_color   = "green" if "Aktif" in domain_status else "red"

    rows_info = [
        ("Email",             escape(email_input)),
        ("Username",          escape(username_email)),
        ("Domain",            escape(domain)),
        ("Provider",          escape(provider)),
        ("Status Email",      status_val),
        ("Status Domain",     f"[{mx_color}]{escape(domain_status)}[/{mx_color}]"),
    ]

    for f, v in rows_info:
        table_info.add_row(f, v)

    show_result_panel("ANALISIS EMAIL", table_info, "green")

    # Tabel cek sumber publik
    console.print()
    table_src = Table(
        show_header=True,
        header_style="bold red",
        box=box.SIMPLE_HEAVY,
        border_style="green",
        padding=(0, 2)
    )
    table_src.add_column("Sumber",  style="bold green", no_wrap=True, width=14)
    table_src.add_column("Status",  style="white",      no_wrap=False)

    def fmt_status(s: str) -> str:
        if s.startswith("✓"):
            return f"[bold green]{escape(s)}[/bold green]"
        elif s.startswith("✗"):
            return f"[bold red]{escape(s)}[/bold red]"
        return f"[dim]{escape(s)}[/dim]"

    table_src.add_row("Gravatar", fmt_status(gravatar_status))
    table_src.add_row("GitHub",   fmt_status(github_status))
    table_src.add_row("Reddit",   fmt_status(reddit_status))
    table_src.add_row("Pastebin", "[dim]Memerlukan API key premium[/dim]")

    show_result_panel("CEK SUMBER PUBLIK", table_src, "green")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 7 — ULTRADORK
# ══════════════════════════════════════════════════════════════════════════════

def feature_ultradork():
    """Launcher untuk dork.py lokal."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  ULTRADORK  [/bold red]",
        border_style="red"
    ))
    console.print()

    dork_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dork.py")

    if os.path.isfile(dork_path):
        console.print(f"  [bold green][✓] dork.py ditemukan: {escape(dork_path)}[/bold green]")
        console.print("  [dim]Meluncurkan dork.py...[/dim]")
        time.sleep(1)
        try:
            subprocess.run([sys.executable, dork_path], check=False)
        except Exception as e:
            console.print(f"  [bold red][!] Gagal menjalankan dork.py: {escape(str(e))}[/bold red]")
    else:
        console.print("  [bold red][!] dork.py tidak ditemukan di direktori yang sama.[/bold red]")
        console.print(f"  [dim]Pastikan dork.py ada di: {escape(os.path.dirname(dork_path))}[/dim]")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 8 — ULTRADOS
# ══════════════════════════════════════════════════════════════════════════════

def feature_ultrados():
    """Launcher untuk dos.py lokal."""
    show_banner()
    show_separator("red")
    console.print(Panel(
        "[bold red]  ULTRADOS  [/bold red]",
        border_style="red"
    ))
    console.print()

    dos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dos.py")

    if os.path.isfile(dos_path):
        console.print(f"  [bold green][✓] dos.py ditemukan: {escape(dos_path)}[/bold green]")
        console.print("  [dim]Meluncurkan dos.py...[/dim]")
        time.sleep(1)
        try:
            subprocess.run([sys.executable, dos_path], check=False)
        except Exception as e:
            console.print(f"  [bold red][!] Gagal menjalankan dos.py: {escape(str(e))}[/bold red]")
    else:
        console.print("  [bold red][!] dos.py tidak ditemukan di direktori yang sama.[/bold red]")
        console.print(f"  [dim]Pastikan dos.py ada di: {escape(os.path.dirname(dos_path))}[/dim]")

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# FITUR 9 — ABOUT
# ══════════════════════════════════════════════════════════════════════════════

def feature_about():
    """Tampilkan informasi tentang OSINTJAR."""
    show_banner()
    show_separator("red")

    about_text = Text()
    about_text.append("\n")
    about_text.append("  OSINTJAR", style="bold red")
    about_text.append("  v1.0\n", style="bold green")
    about_text.append("  ─────────────────────────────────\n", style="dim red")
    about_text.append("  Developer  : ", style="dim")
    about_text.append("Pajar\n", style="bold green")
    about_text.append("  Platform   : ", style="dim")
    about_text.append("Termux / Linux\n", style="bold green")
    about_text.append("  Language   : ", style="dim")
    about_text.append("Python 3.12\n", style="bold green")
    about_text.append("  ─────────────────────────────────\n", style="dim red")
    about_text.append("\n  Modules:\n", style="bold white")

    modules = [
        ("01", "Phone OSINT",         "Analisis nomor telepon"),
        ("02", "IP OSINT",            "Informasi detail IP address"),
        ("03", "My IP",               "Deteksi IP publik sendiri"),
        ("04", "Username Finder",     "Cek username di 14 platform"),
        ("05", "Social Media Finder", "Cek username di 20 platform"),
        ("06", "Email OSINT",         "Analisis email & domain"),
        ("07", "UltraDork",           "Launcher modul dork.py"),
        ("08", "UltraDOS",            "Launcher modul dos.py"),
    ]

    for num, name, desc in modules:
        about_text.append(f"  [{num}] ", style="bold red")
        about_text.append(f"{name:<24}", style="bold white")
        about_text.append(f"{desc}\n", style="dim green")

    about_text.append("\n  ─────────────────────────────────\n", style="dim red")
    about_text.append("  Dibuat dengan ", style="dim")
    about_text.append("❤", style="bold red")
    about_text.append(" untuk komunitas Termux Indonesia\n", style="dim")

    panel = Panel(
        about_text,
        title="[bold red]  ABOUT OSINTJAR  [/bold red]",
        border_style="red",
        padding=(0, 2)
    )
    console.print(panel)

    press_enter()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Loop utama program OSINTJAR."""
    # Mapping pilihan menu ke fungsi
    menu_map = {
        "1":  feature_phone_osint,
        "01": feature_phone_osint,
        "2":  feature_ip_osint,
        "02": feature_ip_osint,
        "3":  feature_my_ip,
        "03": feature_my_ip,
        "4":  feature_username_finder,
        "04": feature_username_finder,
        "5":  feature_social_finder,
        "05": feature_social_finder,
        "6":  feature_email_osint,
        "06": feature_email_osint,
        "7":  feature_ultradork,
        "07": feature_ultradork,
        "8":  feature_ultrados,
        "08": feature_ultrados,
        "9":  feature_about,
        "09": feature_about,
        "0":  None,
        "00": None,
    }

    while True:
        try:
            show_menu()
            pilihan = Prompt.ask(
                "\n  [bold red]OSINTJAR[/bold red][dim]>[/dim]",
                default=""
            ).strip()

            if pilihan in ("0", "00"):
                # Exit
                show_banner()
                console.print()
                console.print(Align.center(
                    Text("Terima kasih telah menggunakan OSINTJAR !", style="bold green")
                ))
                console.print(Align.center(
                    Text("Developer: Pajar  |  v1.0", style="dim red")
                ))
                console.print()
                sys.exit(0)

            elif pilihan in menu_map:
                func = menu_map[pilihan]
                if func:
                    func()
            else:
                console.print()
                console.print(f"  [bold red][!] Pilihan '{escape(pilihan)}' tidak valid.[/bold red]")
                console.print("  [dim]Masukkan angka 00-09.[/dim]")
                time.sleep(1.5)

        except KeyboardInterrupt:
            console.print()
            console.print()
            console.print(Align.center(
                Text("[ Ctrl+C terdeteksi ] Kembali ke menu...", style="bold yellow")
            ))
            time.sleep(1.2)
            continue

        except Exception as e:
            console.print()
            console.print(f"  [bold red][!] Error tidak terduga: {escape(str(e))}[/bold red]")
            console.print("  [dim]Kembali ke menu...[/dim]")
            time.sleep(2)
            continue

# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Cek versi Python minimal
    if sys.version_info < (3, 8):
        print("[!] OSINTJAR membutuhkan Python 3.8 atau lebih baru.")
        sys.exit(1)
    main()
