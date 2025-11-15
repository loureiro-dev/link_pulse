# ATENÇÃO:
# Esta lista define as páginas que serão monitoradas.
# O usuário final deve inserir manualmente os URLs das páginas de captura 
# que deseja minerar.

import argparse
from src.collectors.requests_collector import collect_from_page
from src.processing.cleaning import normalize_whatsapp_link, is_group_link
from src.storage.database import save_links, list_links
from src.notifications.telegram import send_message
import os, time


# Default pages list (you can externalize this to a JSON or CSV)
PAGES = [
    ("https://sndflw.com/i/black-friday-cripto-monstruosa", "black cripto"),
    ("https://sndflw.com/i/mega-black-fluency-na-midia-crm", "black fluency"),
]

def run(mode='quick'):
    found_total = 0
    all_new = []

    for url, name in PAGES:
        # Checando página (nome + URL)
        print(f"Checking {name}: {url}")

        links, has_form, is_thanks = collect_from_page(url)

        cleaned = []
        for l in links:
            c = normalize_whatsapp_link(l)
            if is_group_link(c):
                cleaned.append(c)

        if cleaned:
            save_links(cleaned, source=name)
            found_total += len(cleaned)
            all_new.extend(cleaned)
            print(f"✔ Found {len(cleaned)} group link(s) on {name}")
        else:
            print(f"✖ No links found on {name}")

    # Summary final
    print("\n--- SUMMARY ---")
    print(f"Total links found: {found_total}")

    if all_new:
        msg = "Novos links encontrados:\n" + "\n".join(all_new)
        send_message(msg)
    # show recent links
    for row in list_links(20):
        print(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='quick')
    args = parser.parse_args()
    run(mode=args.mode)
