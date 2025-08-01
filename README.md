# Generatore di Assoli di Chitarra per Genere Musicale

Questo progetto implementa un sistema basato su reti neurali per la generazione automatica di assoli di chitarra, con la capacità di adattarsi a diversi generi musicali. L'interazione con il sistema avviene tramite una web application intuitiva.

## Caratteristiche Principali

*   **Generazione per Genere**: Scegli tra diversi generi musicali (Rock, Jazz, Funk, Bossa Nova, Singer-Songwriter, o un modello generale "All Genres") per generare assoli stilisticamente coerenti.
*   **Input "Seed" Personalizzato**: Fornisci una breve sequenza di note come punto di partenza, permettendo un controllo creativo sull'inizio dell'assolo.
*   **Controllo dei Parametri**: Regola la "temperatura" (per influenzare la creatività e la prevedibilità dell'assolo) e la lunghezza desiderata dell'assolo.
*   **Download MIDI**: Scarica l'assolo generato in formato MIDI, compatibile con la maggior parte delle Digital Audio Workstation (DAW) e software musicali.

## Come Funziona

Il cuore del sistema è una Rete Neurale Ricorrente (RNN) basata su architetture Long Short-Term Memory (LSTM), addestrata su un vasto dataset di trascrizioni di assoli di chitarra.

1.  **Preprocessing dei Dati**: Il dataset originale (GuitarSet) viene processato per estrarre sequenze di note MIDI. Queste sequenze vengono filtrate per limitare le ripetizioni consecutive e vengono aumentate tramite trasposizione per arricchire il dataset di training. I dati sono separati per genere musicale.
2.  **Addestramento del Modello**: Viene addestrato un modello LSTM separato per ciascun genere musicale (e uno per tutti i generi combinati). Il training utilizza tecniche come il Dropout e l'Early Stopping per prevenire l'overfitting e migliorare la generalizzazione.
3.  **Generazione**: Dato un genere selezionato, una sequenza di note iniziale (seed), una temperatura e una lunghezza desiderata, il modello predice iterativamente la nota successiva, componendo l'assolo. La libreria `midiutil` viene utilizzata per scrivere l'assolo finale in un file MIDI.
4.  **Web Application**: Un backend API sviluppato con FastAPI gestisce le richieste di generazione dal frontend. Il frontend, realizzato con HTML, CSS e JavaScript puro, fornisce l'interfaccia utente per interagire con il sistema.

## Setup e Avvio del Progetto

Segui questi passaggi per configurare ed eseguire il progetto sul tuo sistema locale.

### Prerequisiti

*   Python 3.8+
*   `pip` (gestore di pacchetti Python)
*   `git` (per clonare il repository)

### 1. Clonazione del Repository

Apri il tuo terminale e clona il repository:

```bash
git clone https://github.com/tuo-utente/btc-project.git # Sostituisci con l'URL del tuo repository
cd btc-project
```

### 2. Configurazione dell'Ambiente Python

È fortemente consigliato creare un ambiente virtuale:

```bash
python3 -m venv venv
source venv/bin/activate # Su Windows: venv\Scripts\activate
```

Installa le dipendenze Python:

```bash
pip install -r webapp/backend/requirements.txt
pip install tensorflow networkx mido
```
*(Nota: `tensorflow` e `networkx` non sono nel `requirements.txt` del backend perché sono usati negli script di ML, ma sono necessari per il progetto completo.)*

### 3. Preprocessing dei Dati

Esegui lo script di preprocessing per preparare i dataset per il training. Questo creerà file di sequenze per ogni genere nella cartella `data/`.

```bash
python3 src/data_preprocessing/data_preprocessing.py
```

### 4. Addestramento dei Modelli

Addestra i modelli di rete neurale per ogni genere. Questo processo potrebbe richiedere tempo, specialmente se non hai una GPU.

```bash
python3 src/modeling/modeling.py
```

### 5. Avvio del Backend API

Apri un **nuovo terminale** e naviga nella directory del backend:

```bash
cd webapp/backend
```

Avvia il server FastAPI:

```bash
uvicorn main:app --reload --port 8000
```
Lascia questo terminale aperto e in esecuzione.

### 6. Avvio del Frontend Web

Apri un **terzo terminale** e naviga nella directory del frontend:

```bash
cd webapp/frontend
```

Avvia un semplice server HTTP per servire i file statici del frontend:

```bash
python3 -m http.server 8080
```
Lascia questo terminale aperto e in esecuzione.

### 7. Accesso alla Web Application

Apri il tuo browser web e vai a:

```
http://localhost:8080
```

Ora puoi interagire con il generatore di assoli!

## Struttura del Progetto

*   `data/`: Contiene il dataset originale (file JAMS) e i file di sequenze pre-processate.
*   `models/`: Archivia i modelli LSTM addestrati (`.h5`) e i file di mappatura delle note (`.json`).
*   `output/`: Cartella per gli assoli MIDI generati.
*   `src/`: Contiene il codice sorgente Python per:
    *   `data_preprocessing/`: Script per la preparazione e l'aumento dei dati.
    *   `modeling/`: Script per la definizione e l'addestramento dei modelli.
    *   `generation/`: Script per la generazione di assoli e la scrittura di file MIDI.
    *   `analysis/`: Script per l'analisi di rete degli assoli.
*   `.gitignore`: Definisce i file e le directory da ignorare per Git.

## Valutazione e Miglioramento

Il progetto include uno script per la valutazione oggettiva degli assoli generati, confrontando le loro metriche di rete con quelle dei dati originali. Questo è un passo fondamentale per il miglioramento continuo della qualità degli assoli.

Per eseguire la valutazione:

```bash
python3 src/analysis/evaluate_models.py
```

## Prospettive Future

*   **Variazione della Durata delle Note**: Attualmente, tutte le note generate hanno una durata fissa. Un miglioramento significativo sarebbe estrarre e prevedere anche le durate delle note dal dataset, permettendo assoli più ritmicamente complessi e naturali.
*   **Integrazione di Altri Parametri Musicali**: Esplorare la previsione di altri parametri come la velocity (volume della nota), l'articolazione o l'espressione per arricchire ulteriormente gli assoli.
*   **Dataset più Ampi e Specifici**: L'utilizzo di dataset più grandi e specifici per artista/sottogenere potrebbe migliorare ulteriormente la coerenza stilistica.
*   **Interfaccia Utente Avanzata**: Sviluppare un'interfaccia utente più sofisticata, magari con una tastiera MIDI virtuale per l'input del seed o una visualizzazione in tempo reale dell'assolo generato.
