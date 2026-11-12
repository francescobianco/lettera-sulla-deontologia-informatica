# Invio della lettera via PEC

Strumenti per spedire la lettera ai destinatari, un'ondata alla volta, e seguire le ricevute.

| File | A cosa serve |
| --- | --- |
| `destinatari.csv` | Elenco dei destinatari: ondata, ente, indirizzo PEC, saluto personalizzato, fonte dell'indirizzo |
| `messaggio.txt` | Testo della PEC di accompagnamento. La prima riga è l'oggetto, `{saluto}` viene sostituito per ogni destinatario |
| `lettera-deontologia-informatica.pdf` | La lettera in PDF, allegata a ogni PEC |
| `invia_pec.py` | Invia le PEC di un'ondata e annota gli invii in `registro.csv` |
| `controlla_ricevute.py` | Legge le ricevute di accettazione e consegna e aggiorna `registro.csv` |
| `registro.csv` | Creato al primo invio: chi ha ricevuto cosa e quando |

## Procedura

1. **Verifica gli indirizzi.** Controlla ogni PEC sul sito ufficiale dell'ente o sull'Indice delle Pubbliche Amministrazioni (indicepa.gov.it), poi scrivi `si` nella colonna `verificato`. Lo script salta gli indirizzi non verificati.
2. **Fai una prova.** Mostra i destinatari in coda e l'anteprima del messaggio, senza inviare nulla:
   ```
   python3 invio/invia_pec.py --ondata 1
   ```
3. **Invia a te stesso per primo.** Aggiungi in `destinatari.csv` una riga con la tua PEC e un'ondata di prova (per esempio `0`), verificata, e inviala:
   ```
   PEC_PASSWORD='la-tua-password' python3 invio/invia_pec.py --ondata 0 --invia
   ```
4. **Invia l'ondata.** Lo script chiede di scrivere `INVIA` per confermare e aspetta 60 secondi tra un invio e l'altro:
   ```
   PEC_PASSWORD='la-tua-password' python3 invio/invia_pec.py --ondata 1 --invia
   ```
5. **Controlla le ricevute** qualche minuto dopo:
   ```
   PEC_PASSWORD='la-tua-password' python3 invio/controlla_ricevute.py
   ```

Per non lasciare la password nella cronologia della shell, metti uno spazio prima del comando oppure usa `read -s PEC_PASSWORD && export PEC_PASSWORD`.

## Configurazione

Le impostazioni predefinite sono per Aruba PEC (`@pec.it`). Si cambiano con variabili d'ambiente:

| Variabile | Predefinito |
| --- | --- |
| `PEC_UTENTE` | `info.francescobianco@pec.it` |
| `PEC_SMTP_HOST` / `PEC_SMTP_PORT` | `smtps.pec.aruba.it` / `465` |
| `PEC_IMAP_HOST` / `PEC_IMAP_PORT` | `imaps.pec.aruba.it` / `993` |

Verifica i server nella guida del tuo gestore PEC prima del primo invio.

## Rigenerare il PDF

Dopo ogni modifica alla lettera:

```
google-chrome --headless=new --no-pdf-header-footer \
  --print-to-pdf=invio/lettera-deontologia-informatica.pdf "file://$PWD/index.html"
```

## Ondate previste

1. Ordine degli Ingegneri della Provincia di Trapani
2. Consiglio Nazionale degli Ingegneri
3. Gli altri Ordini provinciali
4. Commissioni parlamentari, ministeri, ACN, AgID
5. Università, associazioni, stampa

## Buone pratiche

- Una PEC per destinatario, mai elenchi in copia: è più cortese e ogni consegna ha la sua ricevuta.
- Procedi per ondate e aspetta le risposte prima di passare alla successiva.
- I gestori PEC hanno limiti giornalieri di invio: per ondate grandi distribuisci gli invii su più giorni.
- La ricevuta di consegna ha valore legale solo se anche il destinatario usa una PEC.
