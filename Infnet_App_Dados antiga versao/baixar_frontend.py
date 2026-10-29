# ==============================================================================
# SCRIPT: baixar_frontend_infnet.py
# DATA/HORA: 29/10/2026 15:20
# AUTOR: Antigravity / Mattheus
# FINALIDADE: Baixa todo o frontend web (HTML, CSS, JS, Imagens, Manifest) que
# o app "Instituto Infnet" carrega ao ser aberto.
# ==============================================================================

import os
import re
import urllib.request
import ssl
from urllib.parse import urljoin, urlparse

DEST_DIR = r"C:\Users\matth\Desktop\Infnet_App_Dados\frontend_completo"
os.makedirs(DEST_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S948B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.102 Mobile Safari/537.36"
}

BASE_URL = "https://infnet.online/?bb_sso_bypass_cache=5b755696360312d00d8206528980f926"

print(f"[*] Baixando pagina inicial: {BASE_URL}")
req = urllib.request.Request(BASE_URL, headers=HEADERS)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
except Exception as e:
    print(f"Erro ao baixar HTML: {e}")
    html = ""

with open(os.path.join(DEST_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print(f"[+] index.html salvo ({len(html)} bytes)")

# Encontrar todos os assets
urls_to_download = set()

# CSS
for m in re.finditer(r'href=[\'"]([^\'"]+\.css[^\'"]*)[\'"]', html, re.I):
    urls_to_download.add(urljoin(BASE_URL, m.group(1)))

# JS
for m in re.finditer(r'src=[\'"]([^\'"]+\.js[^\'"]*)[\'"]', html, re.I):
    urls_to_download.add(urljoin(BASE_URL, m.group(1)))

# Imagens
for m in re.finditer(r'(?:src|href)=[\'"]([^\'"]+\.(?:png|jpg|jpeg|svg|webp|ico)[^\'"]*)[\'"]', html, re.I):
    urls_to_download.add(urljoin(BASE_URL, m.group(1)))

# Manifest
for m in re.finditer(r'href=[\'"]([^\'"]+(?:manifest|json)[^\'"]*)[\'"]', html, re.I):
    urls_to_download.add(urljoin(BASE_URL, m.group(1)))

print(f"[*] Total de arquivos identificados no frontend: {len(urls_to_download)}")

for u in sorted(urls_to_download):
    parsed = urlparse(u)
    # clean query params for file path
    clean_path = parsed.path.lstrip("/")
    if not clean_path:
        continue
    
    local_file = os.path.join(DEST_DIR, clean_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(local_file), exist_ok=True)
    
    try:
        r = urllib.request.Request(u, headers=HEADERS)
        with urllib.request.urlopen(r, context=ctx, timeout=10) as resp:
            content = resp.read()
            with open(local_file, "wb") as f_out:
                f_out.write(content)
        print(f"  [OK] {clean_path} ({len(content)} bytes)")
    except Exception as err:
        print(f"  [FALHA] {u} -> {err}")

print("[*] Concluido!")
