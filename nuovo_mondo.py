import random
import sys
import time
import json
import os

from termcolor import colored, cprint

import Morale_Eventi
import Stati_Ingaggio
import Indigeni_baratto
import riepilogo_gg



try:
    import msvcrt
    is_windows = True
except ImportError:
    import select
    is_windows = False


# ==========================================
# GESTIONE DATI E SALVATAGGI
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_SALVATAGGIO = os.path.join(BASE_DIR, "galeone_save.json")

def pulisci_schermo():
    os.system('cls' if os.name == 'nt' else 'clear')

def carica_dati():
    dati_base = {
        "stats": {
            "morti": 0,
            "vittorie_epiche": 0,
            "vittorie_pirro": 0,
            "rovine": 0
        },
        "salvataggi": {}
    }
    if os.path.exists(FILE_SALVATAGGIO):
        try:
            with open(FILE_SALVATAGGIO, "r", encoding="utf-8") as f:
                dati_letti = json.load(f)
                if "stats" in dati_letti:
                    dati_base["stats"].update(dati_letti["stats"])
                if "salvataggi" in dati_letti:
                    dati_base["salvataggi"].update(dati_letti["salvataggi"])
        except json.JSONDecodeError:
            cprint("\n⚠️  ATTENZIONE: Il file di salvataggio è corrotto!", "red", attrs=["bold"])
        except Exception as e:
            cprint(f"\n⚠️  Errore imprevisto nel caricamento: {e}", "red")
    return dati_base

def salva_dati(dati):
    try:
        with open(FILE_SALVATAGGIO, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4, ensure_ascii=False)
    except Exception as e:
        cprint(f"❌ Errore durante il salvataggio: {e}", "red")

def archivia_partita(capitano, stato, esito):
    print()
    nome = input(colored("👉 Inserisci un nome per registrare questa partita (Invio per casuale): ", "cyan")).strip()
    if not nome:
        nome = f"Cronaca_di_{capitano}_{random.randint(1000,9999)}"
    dati = carica_dati()
    stato["esito"] = esito
    dati["salvataggi"][nome] = {"capitano": capitano, "stato": stato}
    salva_dati(dati)
    cprint(f"✅ Partita '{nome}' registrata negli archivi.", "green")

def mostra_statistiche_globali(dati):
    pulisci_schermo()
    cprint("\n" + "="*60, "cyan", attrs=["bold"])
    cprint(" 📊 --- REGISTRO DEL CAPITANO (STATISTICHE GLOBALI) --- 📊 ", "yellow", attrs=["bold"])
    cprint("="*60, "cyan", attrs=["bold"])
    stats = dati["stats"]
    print(f"💀 Morti in mare:        {colored(stats['morti'], 'red', attrs=['bold'])}")
    print(f"👑 Vittorie Epiche:      {colored(stats['vittorie_epiche'], 'yellow', attrs=['bold'])}")
    print(f"⚖️  Vittorie di Pirro:   {colored(stats['vittorie_pirro'], 'cyan', attrs=['bold'])}")
    print(f"⛓️  Rovina Totale:       {colored(stats['rovine'], 'dark_grey', attrs=['bold'])}")
    input(colored("\n📖 [Premi Invio per tornare al Menù] ", "dark_grey"))

# ==========================================
# FUNZIONI DI INPUT E STAMPA
# ==========================================

def leggi_input(prompt_testo):
    sys.stdout.write(prompt_testo)
    sys.stdout.flush()
    risposta = ""
    while True:
        if is_windows:
            import msvcrt
            c = msvcrt.getch()
            if c == b'\x1b':
                print()
                raise InterruptedError("ESC")
            elif c in (b'\r', b'\n'):
                print()
                return risposta
            elif c == b'\x08':
                if len(risposta) > 0:
                    risposta = risposta[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                try:
                    char = c.decode('utf-8')
                    risposta += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
                except: pass
        else:
            print("Sistema operativo non supportato per input avanzato.")

def chiedi_opzione(prompt_testo):
    while True:
        scelta = leggi_input(prompt_testo + " (S/N): ").upper().strip()
        if scelta == "S":
            return True
        elif scelta == "N":
            return False
        else:
            cprint("\n❌ Scelta non valida. Inserisci S o N.", "red")

def chiedi_scelta(prompt_testo, opzioni_valide):
    while True:
        scelta = leggi_input(prompt_testo).upper().strip()
        if scelta in opzioni_valide:
            return scelta
        cprint("\n❌ Scelta non valida. Scegli una delle opzioni tra parentesi.", "red")

def stampa_lenta(testo, colore=None, attrs=None, ritardo=0.03):
    salta_animazione = False
    if is_windows:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    for carattere in testo:
        if not salta_animazione:
            if is_windows:
                import msvcrt
                if msvcrt.kbhit():
                    tasto = msvcrt.getch()
                    if tasto in (b'\r', b'\n'):
                        salta_animazione = True
            else:
                import select
                i, o, e = select.select([sys.stdin], [], [], 0)
                if i:
                    sys.stdin.readline()
                    salta_animazione = True
        char_da_stampare = colored(carattere, colore, attrs=attrs) if colore else carattere
        sys.stdout.write(char_da_stampare)
        sys.stdout.flush()
        if not salta_animazione:
            time.sleep(ritardo)
    print()

def game_over(messaggio, stato, capitano):
    dati = carica_dati()
    dati["stats"]["morti"] += 1
    salva_dati(dati)
    print()
    stampa_lenta("="*60, "red", attrs=["bold"])
    stampa_lenta(messaggio, "red")
    stampa_lenta("\n💀 === GAME OVER === 💀\n", "red", attrs=["bold", "blink"])
    stampa_lenta("="*60, "red", attrs=["bold"])
    archivia_partita(capitano, stato, "Morto in mare")
    return False

def variazione_stat(messaggio, colore):
    stampa_lenta(f"  {messaggio}", colore, attrs=["bold"])


# ==========================================
#CICLO DI GIOCO E SCENARI
# ==========================================
def _ciclo_viaggio(stato, capitano, fase_nome, settimane_base):
    settimana = 1

    while True:
        settimane_totali = settimane_base + stato["settimane_extra"] - stato["settimane_risparmiate"]
        if settimane_totali < settimana:
            settimane_totali = settimana

        stampa_lenta("\n📅 --- SETTIMANA " + str(settimana) + " DI " + fase_nome.upper() + " (di ~" + str(settimane_totali) + ") ---", "yellow", attrs=["bold"])
        Stati_Ingaggio.stampa_risorse(stato)

        if Morale_Eventi.equipaggio_basso_morale(stato, 30): #basso morale
            stampa_lenta("⚠️ Il morale è a pezzi! La nave rallenta.", "red", attrs=["bold"])
            stato["settimane_extra"] = stato["settimane_extra"] + 1
            settimane_totali = settimane_totali + 1
            stampa_lenta("📅 Il viaggio si allunga! Restano " + str(settimane_totali - settimana) + " settimane.", "red")


        if settimana % 2 == 0: #eventi
            Morale_Eventi.gestisci_evento_casuale(stato)

        leggi_input(colored("\n📖 [Premi Invio per avanzare...] ", "dark_grey"))
        pulisci_schermo()

        esito = Stati_Ingaggio.consuma_scorte_dettagliate(stato) #consumo e controllo scorte
        Stati_Ingaggio.incrementa_settimane(stato)

        punti, cause = Morale_Eventi.calcola_ammutinamento(stato) #ammutinamento

        if punti >= 100: 
            return game_over("L'ammutinamento esplode! La ciurma ti elimina.",stato, capitano)

 
        if esito == "affondato": #esiti
            return game_over("La nave affonda.",stato, capitano)

        if esito == "ammutinamento":
            return game_over("La ciurma si ribella.",stato, capitano)
 

        if Stati_Ingaggio.conta_equipaggio(stato) == 0: #equipaggio morto
            return game_over("Tutti morti. Fine.",stato, capitano)


        if settimana >= settimane_totali: #fine viaggio
            break

        settimana = settimana + 1

    return True




