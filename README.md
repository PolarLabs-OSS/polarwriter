# PolarWriter

Editor e redattore AI • PolarLabs-OSS

## Funzioni

Legge testo, suggerisce revisioni e salva bozze TXT/MD. Il modello può scegliere strumenti dedicati, leggerne i risultati e proseguire fino a 5 passaggi. Ogni scrittura, spostamento o patch richiede conferma.

## Installazione Windows

Scarica l'archivio Windows x64, estrai l'intera cartella e avvia polarwriter-v0.3.exe. Non occorre installare Python. L'eseguibile è unsigned: le policy di sicurezza potrebbero bloccarlo. Windows ARM64 può usare l'emulazione x64.

## Configurazione

Avvia LM Studio, Ollama o altra piattaforma che fornisca API OpenAI-compatible. Carica un modello che segua istruzioni JSON, avvia il server, incolla l'URL in-app (es. http://127.0.0.1:1234/v1) e fai clic su Connetti. Scegli il modello, autorizza una cartella di lavoro e descrivi un obiettivo. L'app accetta solo server localhost/127.0.0.1 e non trasmette dati in cloud autonomamente.

## Limiti

Sono supportati fino a 5 passaggi e non è possibile usare modelli incapaci di produrre JSON affidabile per le funzioni operative. Le elaborazioni possono essere lente e dipendono dal modello e dalle risorse del computer. Il pulsante Interrompi agisce tra una richiesta e la successiva; una richiesta HTTP già in corso può dover attendere il timeout. PolarDocs non esegue OCR delle scansioni. Tutte le modifiche richiedono autorizzazione e sono limitate alla cartella scelta. Nessun accesso a email o applicazioni esterne.

## Licenza

MIT, vedi LICENSE. PolarLabs | Space Services SRLS.
