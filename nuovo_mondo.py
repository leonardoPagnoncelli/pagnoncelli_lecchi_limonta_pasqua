import random
import sys
import time
import json
import os
from termcolor import colored, cprint

import Morale_Eventi
import Stati_Ingaggio
import Arrivo_GameOver

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
    print("\033[H\033[2J", end="", flush=True) # universale per ogni OS  con ANSI 

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
    
    is_windows = (os.name == 'nt')

    if is_windows:
        import msvcrt
        while True:
            c = msvcrt.getch()
            
            if c == b'\x1b':  # Tasto ESC
                print()
                raise InterruptedError("ESC")
            elif c in (b'\r', b'\n'):  # Tasto Invio
                print()
                return risposta
            elif c == b'\x08':  # Backspace
                if len(risposta) > 0:
                    risposta = risposta[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif c == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif c in (b'\x00', b'\xe0'):  # Ignora i tasti speciali (es. Frecce direzionali)
                msvcrt.getch()  # "Brucia" il secondo byte del tasto speciale
            else:
                try:
                    char = c.decode('utf-8')
                    risposta += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
                except UnicodeDecodeError:
                    pass

    else:
        # Mac / Linux
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Imposta la modalità raw UNA SOLA VOLTA all'inizio
            tty.setraw(fd)
            while True:
                c = sys.stdin.read(1)
                
                if c == '\x1b':  # Tasto ESC
                    # Ritorna alla riga normale prima di sollevare l'errore
                    sys.stdout.write('\r\n') 
                    raise InterruptedError("ESC")
                elif c in ('\r', '\n'):  # Tasto Invio
                    sys.stdout.write('\r\n')
                    return risposta
                elif c in ('\x7f', '\x08'):  # Backspace
                    if len(risposta) > 0:
                        risposta = risposta[:-1]
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                elif c == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                else:
                    risposta += c
                    sys.stdout.write(c)
                    sys.stdout.flush()
        finally:
            # Ripristina il terminale alla normalità alla fine, in ogni caso
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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
        while msvcrt.kbhit():
            msvcrt.getch()
    for carattere in testo:
        if not salta_animazione:
            if is_windows:
                if msvcrt.kbhit():
                    tasto = msvcrt.getch()
                    if tasto in (b'\r', b'\n'):
                        salta_animazione = True
            else:
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

        punti = Morale_Eventi.calcola_ammutinamento(stato) #ammutinamento

        if punti >= 100: 
            return Arrivo_GameOver.game_over("L'ammutinamento esplode! La ciurma ti elimina.",stato, capitano)

 
        if esito == "affondato": #esiti
            return Arrivo_GameOver.game_over("La nave affonda.",stato, capitano)

        if esito == "ammutinamento":
            return Arrivo_GameOver.game_over("La ciurma si ribella.",stato, capitano)
 

        if Stati_Ingaggio.conta_equipaggio(stato) == 0: #equipaggio morto
            return Arrivo_GameOver.game_over("Tutti morti. Fine.",stato, capitano)


        if settimana >= settimane_totali: #fine viaggio
            break

        settimana = settimana + 1

    return True


# ==========================================
# FASI DI GIOCO
# ==========================================
def introduzione(): #INTRODUZIONE E CREAZIONE STATO INIZIALE

    pulisci_schermo()

    stampa_lenta("="*60, "yellow", attrs=["bold"])
    stampa_lenta(" ⚓  VERSO IL NUOVO MONDO: SANGUE, SALE E SPEZIE  ⚓ ", "red", "on_grey", attrs=["bold"])
    stampa_lenta("="*60, "yellow", attrs=["bold"])

    stampa_lenta("\nSiviglia, 1519. L'aria del porto è un miasma denso di pesce marcio, catrame e disperazione.", "cyan")
    stampa_lenta("I creditori bussano alla tua porta. La prigione ti aspetta.", "cyan")
    stampa_lenta("Davanti a te riposa il galeone 'La Maledizione d'Oro'.", "cyan")
    stampa_lenta("Obiettivo: Nuovo Mondo, profitto, sopravvivenza.", "cyan", ["bold"])

    capitano = leggi_input(colored("\n🏴‍☠️ Capitano, nome: ", "yellow", attrs=["bold"])).strip().capitalize()

    if capitano == "":
        capitano = "Senza Nome"

    stampa_lenta("\nChe Dio abbia pietà della tua anima, Capitano " + capitano + ".", "red", ["bold"])

    time.sleep(1)

    return capitano, 2000



def viaggio_andata(stato, capitano): #VIAGGIO ANDATA

    pulisci_schermo()

    stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(" SALPATE!", "cyan", ["bold"])
    stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    # NESSUN CUOCO → MALUS
    if stato["equipaggio"]["cuochi"] == 0:
        Morale_Eventi.aggiungi_punti_ammutinamento(stato, 30, "nessun cuoco")

    return _ciclo_viaggio(stato, capitano, "ANDATA", 8)



def viaggio_ritorno(stato, capitano): #VIAGGIO RITORNO

    pulisci_schermo()

    stampa_lenta("🎁 Il capo tribù rifornisce la nave per 3 settimane.", "green", attrs=["bold"])

    n = Stati_Ingaggio.conta_equipaggio(stato)

    for cat in Stati_Ingaggio.CONSUMI_SETTIMANALI_PER_MEMBRO:
        consumo = Stati_Ingaggio.CONSUMI_SETTIMANALI_PER_MEMBRO[cat]
        aggiunte = consumo * n * 3
        stato["scorte"][cat] = stato["scorte"][cat] + aggiunte

    variazione_stat("📈 Scorte caricate per 3 settimane!", "green")

    settimane_base_ritorno = 8

    # NAVIGATORE
    if stato["equipaggio"]["navigatori"] > 0:
        settimane_base_ritorno = settimane_base_ritorno - 1
        stampa_lenta("🧭 Rotta ottimizzata. -1 settimana.", "green")

    # ALBATRO
    if stato["albatro_ucciso"] == True:
        settimane_base_ritorno = settimane_base_ritorno + 1
        stampa_lenta("☠️ Maledizione dell'albatro. +1 settimana.", "red")

    stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    stampa_lenta(" IL RITORNO. ~" + str(settimane_base_ritorno) + " settimane.", "cyan", ["bold"])
    stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    return _ciclo_viaggio(stato, capitano, "RITORNO", settimane_base_ritorno)



# ==========================================
# CREAZIONE STATO INIZIALE E NORMALIZZAZIONE
# ==========================================
# ==========================================
# CREAZIONE E NORMALIZZAZIONE STATO
# ==========================================

def crea_stato_iniziale():

    return {
        "fase": "inizio",
        "budget": 2000,
        "spese_iniziali": 0,

        "scorte": {
            "verdura": 0.0,
            "frutta": 0.0,
            "carne": 0.0,
            "acqua": 0.0
        },

        "razioni_moltiplicatore": {
            "verdura": 1.0,
            "frutta": 1.0,
            "carne": 1.0,
            "acqua": 1.0
        },

        "merci": {
            "bottiglie_medicinale": 0,
            "armi": 0,
            "sale": 0,
            "stoffa": 0,
            "coltelli": 0,
            "diamanti": 0
        },

        "risorse_baratto": {
            "perle": 0.0,
            "manufatti": 0.0,
            "spezie": 0.0
        },

        "barattato": {
            "sale": 0,
            "stoffa": 0,
            "coltelli": 0,
            "diamanti": 0
        },

        "morale_individuale": {},

        "punti_ammutinamento": 0,
        "integrita": 100,

        "equipaggio": {
            "marinai": 0,
            "cuochi": 0,
            "meccanici": 0,
            "medici": 0,
            "navigatori": 0
        },

        "debito_equipaggio": 0,
        "costo_sett_ruolo": {},

        "albatro_ucciso": False,
        "albatro_benevolo": False,
        "avvistamenti_albatro": 0,

        "eventi_accaduti": [],

        "settimane_risparmiate": 0,
        "settimane_extra": 0,
        "settimane_percorse": 0,

        "morti_recenti": 0,
        "eventi_negativi": 0,

        "naufraghi_tot": 0,
        "esito": "In corso"
    }


def normalizza_stato(stato):
    default = crea_stato_iniziale()
    for chiave in default:
        if chiave not in stato:
            stato[chiave] = default[chiave]

    # scorte
    for cat in ["verdura", "frutta", "carne", "acqua"]:
        if cat not in stato["scorte"]:
            stato["scorte"][cat] = 0.0

    # moltiplicatori
    for cat in ["verdura", "frutta", "carne", "acqua"]:
        if cat not in stato["razioni_moltiplicatore"]:
            stato["razioni_moltiplicatore"][cat] = 1.0

    # merci
    for m in ["bottiglie_medicinale", "armi", "sale", "stoffa", "coltelli", "diamanti"]:
        if m not in stato["merci"]:
            stato["merci"][m] = 0

    # baratto
    for r in ["perle", "manufatti", "spezie"]:
        if r not in stato["risorse_baratto"]:
            stato["risorse_baratto"][r] = 0.0

    return stato



def esegui_partita(nuova=True, dati_salvati=None): #PARTITA
    capitano = "Sconosciuto"
    stato_partita = {}
    try:
        if nuova:
            capitano, budget_iniziale = introduzione()
            stato_partita = crea_stato_iniziale()
            stato_partita["budget"] = budget_iniziale
        else:
            pulisci_schermo()
            stato_partita = normalizza_stato(dati_salvati["stato"])
            capitano = dati_salvati["capitano"]
            stampa_lenta("\n⚓ Bentornato a bordo, Capitano " + capitano + "!", "green", attrs=["bold"])
            stampa_lenta("   Fase: " + stato_partita["fase"] + " | Budget: " + str(int(stato_partita["budget"])) + "🪙", "cyan")
            time.sleep(1.5)

        #FASI DI GIOCO

        if stato_partita["fase"] == "inizio":
            stato_partita["fase"] = "arruolamento"

        if stato_partita["fase"] == "arruolamento":
            if not Stati_Ingaggio.fase_arruolamento(stato_partita, capitano):
                return
            stato_partita["fase"] = "provviste"

        if stato_partita["fase"] == "provviste":
            if not Stati_Ingaggio.fase_acquisto_provviste(stato_partita, capitano):
                return
            stato_partita["fase"] = "merci"

        if stato_partita["fase"] == "merci":
            if not Stati_Ingaggio.fase_merci_arsenale(stato_partita, capitano):
                return
            stato_partita["fase"] = "andata"

        if stato_partita["fase"] == "andata":
            if not viaggio_andata(stato_partita, capitano):
                return
            stato_partita["fase"] = "nuovo_mondo"

        if stato_partita["fase"] == "nuovo_mondo":
            risultato = Arrivo_GameOver.arrivo_nuovo_mondo(stato_partita, capitano)
            if risultato is False:
                return
            stato_partita["fase"] = "ritorno"

        if stato_partita["fase"] == "ritorno":
            if not viaggio_ritorno(stato_partita, capitano):
                return

            Arrivo_GameOver.conclusione(capitano, stato_partita)

    except InterruptedError:
        stampa_lenta("\n\n⏸️ GIOCO IN PAUSA", "yellow", attrs=["bold"])
        nome = input(colored("👉 Nome salvataggio: ", "cyan")).strip()
        if nome == "":
            nome = "Salvataggio_" + capitano + "_" + str(random.randint(100, 999))

        dati = carica_dati()
        stato_partita["esito"] = "In corso"

        dati["salvataggi"][nome] = {
            "capitano": capitano,
            "stato": stato_partita
        }

        salva_dati(dati)
        stampa_lenta("\n✅ Partita salvata come '" + nome + "'!", "green", attrs=["bold"])
        time.sleep(2)



# ==========================================
# MENU PRINCIPALE
# ==========================================
def menu_principale():
    while True:
        pulisci_schermo()
        dati = carica_dati()
        stampa_lenta("="*60, "cyan", attrs=["bold"])
        stampa_lenta("  ☠️ LA MALEDIZIONE D'ORO - MENU PRINCIPALE ☠️  ", "yellow", "on_grey", attrs=["bold"])
        stampa_lenta("="*60, "cyan", attrs=["bold"])
        print(colored("  1.", "magenta", attrs=["bold"]) + " 🏴‍☠️ Nuova Partita")


        salvataggi_in_corso = {} #salvataggi in corso
        for k in dati["salvataggi"]:
            v = dati["salvataggi"][k]
            if "esito" in v["stato"] and v["stato"]["esito"] == "In corso":
                salvataggi_in_corso[k] = v

        if len(salvataggi_in_corso) > 0:
            if len(salvataggi_in_corso) == 1:
                testo = "1 salvataggio"
            else:
                testo = str(len(salvataggi_in_corso)) + " salvataggi"
            print(colored("  2.", "magenta", attrs=["bold"]) + " ⚓ Continua Partita (" + testo + ")")
        else:
            print(colored("  2.", "dark_grey") + " ⚓ Continua Partita (Nessun salvataggio)")

        print(colored("  3.", "magenta", attrs=["bold"]) + " 📊 Statistiche Globali")
        print(colored("  4.", "magenta", attrs=["bold"]) + " 🔍 Esplora Archivi")
        print(colored("  0.", "magenta", attrs=["bold"]) + " 🚪 Esci")

        scelta = input(colored("\n👉 Scelta: ", "magenta", attrs=["bold"])).strip()


        if scelta == "1": #NUOVA PARTITA
            esegui_partita(True)

        elif scelta == "2": #CONTINUA PARTITA
            if len(salvataggi_in_corso) == 0:
                stampa_lenta("\n❌ Nessun salvataggio.", "red", attrs=["bold"])
                time.sleep(1.5)
            else:
                pulisci_schermo()
                print("\n⚓ Salvataggi:\n")
                nomi = []
                for nome in salvataggi_in_corso:
                    nomi.append(nome)

                i = 1

                for n in nomi:
                    sv = salvataggi_in_corso[n]
                    fase = sv["stato"]["fase"]
                    budget = sv["stato"]["budget"]
                    print("  " + str(i) + ". " + n)
                    print("     Capitano: " + sv["capitano"] + " | Fase: " + fase + " | Budget: " + str(int(budget)) + "🪙")
                    print()
                    i = i + 1

                scelta_s = input(colored("👉 Numero o nome: ", "cyan")).strip()
                da_caricare = ""
                if scelta_s.isdigit():
                    idx = int(scelta_s)
                    if idx >= 1 and idx <= len(nomi):
                        da_caricare = nomi[idx - 1]
                else:
                    if scelta_s in salvataggi_in_corso:
                        da_caricare = scelta_s

                if da_caricare != "":
                    esegui_partita(False, salvataggi_in_corso[da_caricare])
                else:
                    stampa_lenta("❌ Non trovato.", "red", attrs=["bold"])
                    time.sleep(1.5)

        elif scelta == "3": #STATISTICHE GLOBALI
            mostra_statistiche_globali(dati)

        elif scelta == "4": #ESPLORA ARCHIVI
            pulisci_schermo()
            print("\n🔍 ARCHIVI:\n")
            if len(dati["salvataggi"]) == 0:
                stampa_lenta("❌ Nessuna partita.", "red", attrs=["bold"])
                time.sleep(1.5)
                continue

            nomi_archivi = []
            for nome in dati["salvataggi"]:
                nomi_archivi.append(nome)

            i = 1

            for n in nomi_archivi:
                s = dati["salvataggi"][n]
                esito = s["stato"]["esito"]
                cap = s["capitano"]
                print("  " + str(i) + ". " + n + " [" + esito + "] — Cap. " + cap)
                i = i + 1

            ricerca = input(colored("\n👉 Nome o numero: ", "cyan")).strip()
            da_cercare = ""

            if ricerca.isdigit():
                idx = int(ricerca)
                if idx >= 1 and idx <= len(nomi_archivi):
                    da_cercare = nomi_archivi[idx - 1]
            else:
                if ricerca in dati["salvataggi"]:
                    da_cercare = ricerca

            if da_cercare != "":
                pulisci_schermo()
                s = dati["salvataggi"][da_cercare]
                sp = s["stato"]
                stampa_lenta("\n📜 DETTAGLI: " + da_cercare, "yellow", attrs=["bold"])
                print("🏴‍☠️ Capitano: " + s["capitano"] + " | Esito: " + sp["esito"] + " | Fase: " + sp["fase"])
                print()
                stampa_lenta("💰 RISORSE:", "green")
                print("  🪙 Budget: " + str(int(sp["budget"])))

                for cat in sp["scorte"]:
                    print("  " + cat.capitalize() + ": " + str(round(sp["scorte"][cat], 1)))

                print("  🛡️ Integrità: " + str(sp["integrita"]) + "%")
                print("  ⚠️ Ammutinamento: " + str(sp["punti_ammutinamento"]))
                print("  🗓️ Settimane: " + str(sp["settimane_percorse"]))
                print()
                stampa_lenta("👥 EQUIPAGGIO:", "cyan")

                for ruolo in sp["equipaggio"]:
                    n_p = sp["equipaggio"][ruolo]
                    if n_p > 0:
                        print("  " + Stati_Ingaggio.NOMI_RUOLO[ruolo] + ": " + str(n_p))

                print()
                stampa_lenta("📦 MERCI:", "magenta")

                for merce in sp["merci"]:
                    qty = sp["merci"][merce]
                    if qty > 0:
                        print("  " + merce + ": " + str(qty))

                stampa_lenta("🔮 BARATTO:", "yellow")

                for r in sp["risorse_baratto"]:
                    qty = sp["risorse_baratto"][r]
                    if qty > 0:
                        print("  " + r + ": " + str(round(qty, 1)))

                input(colored("\n📖 Invio per tornare ", "dark_grey"))
            else:
                stampa_lenta("\n❌ Non trovato.", "red")
                time.sleep(1.5)


        elif scelta == "0": #ESCI
            stampa_lenta("\n🌊 Addio, Capitano.", "cyan")
            sys.exit()

        else: #ERRORE
            stampa_lenta("\n❌ Scelta non valida.", "red")
            time.sleep(1)


menu_principale()