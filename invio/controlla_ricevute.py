#!/usr/bin/env python3
"""Legge le ricevute PEC dalla casella e aggiorna registro.csv.

Per ogni PEC inviata il gestore restituisce due ricevute:
  - ACCETTAZIONE: il tuo gestore ha preso in carico il messaggio;
  - CONSEGNA: il messaggio è arrivato nella casella del destinatario (ha valore legale).
In caso di problemi arrivano invece AVVISO DI NON ACCETTAZIONE o AVVISO DI MANCATA CONSEGNA.

Le ricevute si collegano agli invii tramite l'intestazione X-Riferimento-Message-ID.
Lo script legge soltanto: non cancella e non sposta messaggi.

Uso:
    PEC_PASSWORD=... python3 invio/controlla_ricevute.py

Variabili d'ambiente: PEC_PASSWORD, PEC_UTENTE, PEC_IMAP_HOST (predefinito imaps.pec.aruba.it),
PEC_IMAP_PORT (predefinito 993).
"""

import csv
import email
import imaplib
import os
import sys
from email.header import decode_header, make_header
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent
REGISTRO = CARTELLA / "registro.csv"
def carica_env(percorso):
    """Legge KEY=VALORE da un file .env senza passare dalla shell.

    Il valore è preso alla lettera dopo il primo '=': caratteri speciali, apici e spazi interni
    restano intatti. Le variabili già presenti nell'ambiente hanno la precedenza.
    """
    if not percorso.exists():
        return
    for riga in percorso.read_text(encoding="utf-8").splitlines():
        if not riga.strip() or riga.lstrip().startswith("#") or "=" not in riga:
            continue
        chiave, valore = riga.split("=", 1)
        os.environ.setdefault(chiave.strip(), valore)


carica_env(Path(__file__).resolve().parent.parent / ".env")


UTENTE = os.environ.get("PEC_UTENTE", "info.francescobianco@pec.it")
IMAP_HOST = os.environ.get("PEC_IMAP_HOST", "imaps.pec.aruba.it")
IMAP_PORT = int(os.environ.get("PEC_IMAP_PORT", "993"))

TIPI = [
    ("AVVISO DI MANCATA CONSEGNA", "consegna", "MANCATA"),
    ("AVVISO DI NON ACCETTAZIONE", "accettazione", "NON ACCETTATA"),
    ("ACCETTAZIONE", "accettazione", "ok"),
    ("CONSEGNA", "consegna", "ok"),
]


def main():
    password = os.environ.get("PEC_PASSWORD")
    if not password:
        sys.exit("Imposta la variabile d'ambiente PEC_PASSWORD.")
    if not REGISTRO.exists():
        sys.exit("registro.csv non esiste ancora: nessun invio da controllare.")

    with REGISTRO.open(encoding="utf-8", newline="") as f:
        lettore = csv.DictReader(f)
        campi = lettore.fieldnames
        righe = list(lettore)
    per_id = {r["message_id"].strip("<> "): r for r in righe if r["message_id"]}

    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(UTENTE, password)
        imap.select("INBOX", readonly=True)
        _, dati = imap.search(None, 'HEADER', 'X-Riferimento-Message-ID', '""')
        numeri = dati[0].split()
        for n in numeri:
            _, parti = imap.fetch(n, "(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE X-RIFERIMENTO-MESSAGE-ID)])")
            intest = email.message_from_bytes(parti[0][1])
            rif = (intest.get("X-Riferimento-Message-ID") or "").strip("<> \r\n")
            riga = per_id.get(rif)
            if not riga:
                continue
            oggetto = str(make_header(decode_header(intest.get("Subject", "")))).upper()
            for prefisso, colonna, valore in TIPI:
                if oggetto.startswith(prefisso):
                    if riga.get(colonna) in ("", None, "ok") or valore != "ok":
                        riga[colonna] = valore if valore != "ok" else f"ok {intest.get('Date', '')}".strip()
                    break

    with REGISTRO.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        w.writerows(righe)

    print(f"{'id':<20} {'accettazione':<40} consegna")
    for r in righe:
        print(f"{r['id']:<20} {r.get('accettazione') or '-':<40} {r.get('consegna') or '-'}")


if __name__ == "__main__":
    main()
