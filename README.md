# Lettera sulla deontologia informatica

Lettera aperta agli Ordini degli Ingegneri e alle istituzioni per una legge che affidi la sicurezza dei sistemi informatici e di intelligenza artificiale critici a professionisti iscritti all'Albo, sul modello di quanto già avviene per strutture e impianti.

**Leggi la lettera:** https://yafb.net/lettera-sulla-deontologia-informatica/

## La proposta in breve

Per i ponti e gli impianti elettrici la legge dà all'ingegnere una firma, una responsabilità e il potere di dire no. Per i sistemi informatici no: il software di un ospedale o di una pubblica amministrazione può essere messo in esercizio senza che nessun professionista abilitato lo firmi, lo collaudi o ne risponda.

La lettera chiede che, per i sistemi digitali critici, la legge introduca adempimenti obbligatori affidati a ingegneri iscritti all'Albo:

- progetto di sicurezza firmato;
- dichiarazione di conformità;
- collaudo prima della messa in esercizio;
- verifiche periodiche.

Il perimetro comprende sanità, pubblica amministrazione, infrastrutture critiche, soggetti NIS2 e sistemi di intelligenza artificiale ad alto rischio.

## Contenuto del repository

| Percorso | Contenuto |
| --- | --- |
| [`lettera.md`](lettera.md) | Testo della lettera in Markdown |
| [`index.html`](index.html) | Versione web della lettera, pubblicata con GitHub Pages |
| [`dossier/`](dossier/) | Documenti di approfondimento allegati alla lettera |
| [`invio/`](invio/) | Strumenti per l'invio della lettera via PEC e il controllo delle ricevute |

### Dossier

- [Stato delle cose](dossier/stato-delle-cose.md): perché l'ingegnere delle strutture onora il patto con la collettività e l'ingegnere informatico no.
- [Il patto sociale tra ingegnere e collettività](dossier/trattato-patto-sociale-ingegnere-collettivita.md): radici storiche, clausole, casi di violazione e tensioni del patto.
- [Falsi allarmi bomba in 6.000 scuole italiane](dossier/2026-11-11-allarme-bomba-scuole.md): la cronaca dell'11 novembre 2026.
- [ENISA: anche gli elettrodomestici nel mirino degli hacker](dossier/2026-11-10-enisa-elettrodomestici.md): il rapporto 2026 sullo stato della cybersicurezza nell'Unione.

### Invio via PEC

La lettera viene inviata per ondate, una PEC per destinatario, con lo script in [`invio/`](invio/). La procedura completa è descritta in [`invio/README.md`](invio/README.md).

Ondate previste:

1. Ordine degli Ingegneri della Provincia di Trapani (inviata il 12 novembre 2026)
2. Consiglio Nazionale degli Ingegneri
3. Gli altri Ordini provinciali
4. Commissioni parlamentari, ministeri, ACN, AgID
5. Università, associazioni, stampa

La password della casella PEC va nel file `.env`, che è escluso dal repository. Anche il registro degli invii (`invio/registro.csv`) resta solo in locale.

## Aggiornare la lettera

Il testo esiste in due versioni, `lettera.md` e `index.html`: una modifica va riportata in entrambe. Dopo ogni modifica, rigenera il PDF allegato alle PEC:

```
google-chrome --headless=new --no-pdf-header-footer \
  --print-to-pdf=invio/lettera-deontologia-informatica.pdf "file://$PWD/index.html"
```

## Autore

Ing. Francesco Bianco, iscritto alla Sezione A dell'Albo dell'Ordine degli Ingegneri della Provincia di Trapani, n. A1591.
PEC: info.francescobianco@pec.it

## Licenza

Distribuito con licenza MIT: vedi il file [LICENSE](LICENSE).
