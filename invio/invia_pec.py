#!/usr/bin/env python3
"""Invia la lettera via PEC ai destinatari di un'ondata.

Per impostazione predefinita fa una PROVA: mostra cosa verrebbe inviato e non spedisce nulla.
Per spedire davvero serve --invia, e lo script chiede conferma prima di partire.

Ogni destinatario riceve una PEC separata, con il proprio saluto e la lettera in PDF allegata.
Gli invii riusciti finiscono in registro.csv e non vengono ripetuti.

Uso:
    python3 invio/invia_pec.py --ondata 1                 # prova
    PEC_PASSWORD=... python3 invio/invia_pec.py --ondata 1 --invia

Variabili d'ambiente:
    PEC_PASSWORD   password della casella PEC (obbligatoria con --invia); letta anche dal file .env
    PEC_UTENTE     indirizzo PEC del mittente (predefinito: info.francescobianco@pec.it)
    PEC_SMTP_HOST  server SMTP (predefinito: smtps.pec.aruba.it)
    PEC_SMTP_PORT  porta SMTP SSL (predefinito: 465)
"""

import argparse
import csv
import os
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent
DESTINATARI = CARTELLA / "destinatari.csv"
MESSAGGIO = CARTELLA / "messaggio.txt"
ALLEGATO = CARTELLA / "lettera-deontologia-informatica.pdf"
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

CAMPI_REGISTRO = ["id", "ente", "pec", "data_invio", "message_id", "esito", "accettazione", "consegna"]

MITTENTE = os.environ.get("PEC_UTENTE", "info.francescobianco@pec.it")
SMTP_HOST = os.environ.get("PEC_SMTP_HOST", "smtps.pec.aruba.it")
SMTP_PORT = int(os.environ.get("PEC_SMTP_PORT", "465"))


def leggi_messaggio():
    testo = MESSAGGIO.read_text(encoding="utf-8")
    prima, _, corpo = testo.partition("\n")
    if not prima.startswith("Oggetto:"):
        sys.exit("messaggio.txt deve iniziare con una riga 'Oggetto: ...'")
    return prima.removeprefix("Oggetto:").strip(), corpo.lstrip("\n")


def leggi_registro():
    if not REGISTRO.exists():
        return []
    with REGISTRO.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def gia_inviati(registro):
    return {r["id"] for r in registro if r["esito"] == "inviato"}


def aggiungi_al_registro(riga):
    nuovo = not REGISTRO.exists()
    with REGISTRO.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPI_REGISTRO)
        if nuovo:
            w.writeheader()
        w.writerow({k: riga.get(k, "") for k in CAMPI_REGISTRO})


def componi(dest, oggetto, corpo, pdf):
    msg = EmailMessage()
    msg["From"] = MITTENTE
    msg["To"] = dest["pec"]
    msg["Subject"] = oggetto
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=MITTENTE.split("@")[1])
    msg.set_content(corpo.replace("{saluto}", dest["saluto"]))
    msg.add_attachment(pdf, maintype="application", subtype="pdf", filename=ALLEGATO.name)
    return msg


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ondata", required=True, help="numero dell'ondata da inviare (colonna 'ondata')")
    p.add_argument("--solo", help="invia solo al destinatario con questo id")
    p.add_argument("--invia", action="store_true", help="spedisce davvero (senza, è solo una prova)")
    p.add_argument("--pausa", type=int, default=60, help="secondi di attesa tra un invio e l'altro (predefinito 60)")
    p.add_argument("--anche-non-verificati", action="store_true",
                   help="include i destinatari con verificato=no (sconsigliato)")
    a = p.parse_args()

    if not ALLEGATO.exists():
        sys.exit(f"Manca l'allegato {ALLEGATO.name}. Rigeneralo dalla pagina HTML (vedi invio/README.md).")

    oggetto, corpo = leggi_messaggio()
    pdf = ALLEGATO.read_bytes()
    inviati = gia_inviati(leggi_registro())

    with DESTINATARI.open(encoding="utf-8", newline="") as f:
        tutti = [d for d in csv.DictReader(f) if d["ondata"] == a.ondata]
    if a.solo:
        tutti = [d for d in tutti if d["id"] == a.solo]

    coda, saltati = [], []
    for d in tutti:
        if d["id"] in inviati:
            saltati.append((d, "già inviato"))
        elif d["verificato"].strip().lower() != "si" and not a.anche_non_verificati:
            saltati.append((d, "indirizzo PEC non ancora verificato"))
        else:
            coda.append(d)

    print(f"Ondata {a.ondata} · mittente {MITTENTE} · server {SMTP_HOST}:{SMTP_PORT}")
    print(f"Oggetto: {oggetto}")
    print(f"Allegato: {ALLEGATO.name} ({len(pdf) // 1024} KB)\n")
    for d, motivo in saltati:
        print(f"  SALTATO  {d['id']:<20} {d['pec']:<35} ({motivo})")
    for d in coda:
        print(f"  IN CODA  {d['id']:<20} {d['pec']:<35} {d['ente']}")

    if not coda:
        print("\nNessun destinatario da inviare.")
        return

    if not a.invia:
        print("\nPROVA: nessuna PEC è stata inviata. Anteprima del primo messaggio:\n")
        print(componi(coda[0], oggetto, corpo, pdf).get_body(("plain",)).get_content())
        print("Per spedire davvero aggiungi --invia.")
        return

    password = os.environ.get("PEC_PASSWORD")
    if not password:
        sys.exit("Imposta la variabile d'ambiente PEC_PASSWORD per inviare.")

    risposta = input(f"\nStai per inviare {len(coda)} PEC. Scrivi INVIA per confermare: ")
    if risposta.strip() != "INVIA":
        sys.exit("Annullato, nessuna PEC inviata.")

    contesto = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=contesto) as smtp:
        smtp.login(MITTENTE, password)
        for i, d in enumerate(coda):
            msg = componi(d, oggetto, corpo, pdf)
            riga = {"id": d["id"], "ente": d["ente"], "pec": d["pec"],
                    "data_invio": datetime.now().isoformat(timespec="seconds"),
                    "message_id": msg["Message-ID"]}
            try:
                smtp.send_message(msg)
                riga["esito"] = "inviato"
                print(f"  INVIATO  {d['id']:<20} {d['pec']}")
            except smtplib.SMTPException as e:
                riga["esito"] = f"errore: {e}"
                print(f"  ERRORE   {d['id']:<20} {d['pec']}  {e}")
            aggiungi_al_registro(riga)
            if i < len(coda) - 1:
                time.sleep(a.pausa)

    print(f"\nFatto. Controlla le ricevute con: python3 invio/controlla_ricevute.py")


if __name__ == "__main__":
    main()
