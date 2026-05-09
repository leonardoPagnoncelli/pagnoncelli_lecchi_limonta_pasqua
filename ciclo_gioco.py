import nuovo_mondo
import Stati_Ingaggio
import Morale_Eventi
import Indigeni_baratto
import riepilogo_gg
import time
from termcolor import colored
import random
import sys
# ==========================================
# FASI DI GIOCO
# ==========================================
def introduzione(): #INTRODUZIONE E CREAZIONE STATO INIZIALE

    nuovo_mondo.pulisci_schermo()

    nuovo_mondo.stampa_lenta("="*60, "yellow", attrs=["bold"])
    nuovo_mondo.stampa_lenta(" ⚓  VERSO IL NUOVO MONDO: SANGUE, SALE E SPEZIE  ⚓ ", "red", attrs=["bold"])
    nuovo_mondo.stampa_lenta("="*60, "yellow", attrs=["bold"])

    nuovo_mondo.stampa_lenta("\nSiviglia, 1519. L'aria del porto è un miasma denso di pesce marcio, catrame e disperazione.", "cyan")
    nuovo_mondo.stampa_lenta("I creditori bussano alla tua porta. La prigione ti aspetta.", "cyan")
    nuovo_mondo.stampa_lenta("Davanti a te riposa il galeone 'La Maledizione d'Oro'.", "cyan")
    nuovo_mondo.stampa_lenta("Obiettivo: Nuovo Mondo, profitto, sopravvivenza.", "cyan", ["bold"])

    capitano = nuovo_mondo.leggi_input(nuovo_mondo.colored("\n🏴‍☠️ Capitano, nome: ", "yellow", attrs=["bold"])).strip().capitalize()

    if capitano == "":
        capitano = "Senza Nome"

    nuovo_mondo.stampa_lenta("\nChe Dio abbia pietà della tua anima, Capitano " + capitano + ".", "red", ["bold"])

    time.sleep(1)

    return capitano, 2000



def viaggio_andata(stato, capitano): #VIAGGIO ANDATA

    nuovo_mondo.pulisci_schermo()

    nuovo_mondo.stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    nuovo_mondo.stampa_lenta(" SALPATE!", "cyan", ["bold"])
    nuovo_mondo.stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    # NESSUN CUOCO → MALUS
    if stato["equipaggio"]["cuochi"] == 0:
        Morale_Eventi.aggiungi_punti_ammutinamento(stato, 30, "nessun cuoco")

    return nuovo_mondo._ciclo_viaggio(stato, capitano, "ANDATA", 8)



def viaggio_ritorno(stato, capitano): #VIAGGIO RITORNO

    nuovo_mondo.pulisci_schermo()

    nuovo_mondo.stampa_lenta("🎁 Il capo tribù rifornisce la nave per 3 settimane.", "green", attrs=["bold"])

    n = Stati_Ingaggio.conta_equipaggio(stato)

    for cat in Stati_Ingaggio.CONSUMI_SETTIMANALI_PER_MEMBRO:
        consumo = Stati_Ingaggio.CONSUMI_SETTIMANALI_PER_MEMBRO[cat]
        aggiunte = consumo * n * 3
        stato["scorte"][cat] = stato["scorte"][cat] + aggiunte

    Stati_Ingaggio.variazione_stat("📈 Scorte caricate per 3 settimane!", "green")

    settimane_base_ritorno = 8

    # NAVIGATORE
    if stato["equipaggio"]["navigatori"] > 0:
        settimane_base_ritorno = settimane_base_ritorno - 1
        nuovo_mondo.stampa_lenta("🧭 Rotta ottimizzata. -1 settimana.", "green")

    # ALBATRO
    if stato["albatro_ucciso"] == True:
        settimane_base_ritorno = settimane_base_ritorno + 1
        nuovo_mondo.stampa_lenta("☠️ Maledizione dell'albatro. +1 settimana.", "red")

    nuovo_mondo.stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])
    nuovo_mondo.stampa_lenta(" IL RITORNO. ~" + str(settimane_base_ritorno) + " settimane.", "cyan", ["bold"])
    nuovo_mondo.stampa_lenta("🌊" + "="*58 + "🌊", "blue", attrs=["bold"])

    return nuovo_mondo._ciclo_viaggio(stato, capitano, "RITORNO", settimane_base_ritorno)



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



def esegui_partita(nuova=True, dati_salvati={}): #PARTITA
    capitano = "Sconosciuto"
    stato_partita = {}
    try:
        if nuova:
            capitano, budget_iniziale = introduzione()
            stato_partita = crea_stato_iniziale()
            stato_partita["budget"] = budget_iniziale
        else:
            nuovo_mondo.pulisci_schermo()
            stato_partita = normalizza_stato(dati_salvati["stato"])
            capitano = dati_salvati["capitano"]
            nuovo_mondo.stampa_lenta("\n⚓ Bentornato a bordo, Capitano " + capitano + "!", "green", attrs=["bold"])
            nuovo_mondo.stampa_lenta("   Fase: " + stato_partita["fase"] + " | Budget: " + str(int(stato_partita["budget"])) + "🪙", "cyan")
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
            risultato = Indigeni_baratto.arrivo_nuovo_mondo(stato_partita, capitano)
            if risultato is False:
                return
            stato_partita["fase"] = "ritorno"

        if stato_partita["fase"] == "ritorno":
            if not viaggio_ritorno(stato_partita, capitano):
                return

            riepilogo_gg.conclusione(capitano, stato_partita)

    except InterruptedError:
        nuovo_mondo.stampa_lenta("\n\n⏸️ GIOCO IN PAUSA", "yellow", attrs=["bold"])
        nome = input(colored("👉 Nome salvataggio: ", "cyan")).strip()
        if nome == "":
            nome = "Salvataggio_" + capitano + "_" + str(random.randint(100, 999))

        dati = nuovo_mondo.carica_dati()
        stato_partita["esito"] = "In corso"

        dati["salvataggi"][nome] = {
            "capitano": capitano,
            "stato": stato_partita
        }

        nuovo_mondo.salva_dati(dati)
        nuovo_mondo.stampa_lenta("\n✅ Partita salvata come '" + nome + "'!", "green", attrs=["bold"])
        time.sleep(2)



# ==========================================
# MENU PRINCIPALE
# ==========================================
def menu_principale():
    while True:
        nuovo_mondo.pulisci_schermo()
        dati = nuovo_mondo.carica_dati()
        nuovo_mondo.stampa_lenta("="*60, "cyan", attrs=["bold"])
        nuovo_mondo.stampa_lenta("  ☠️ LA MALEDIZIONE D'ORO - MENU PRINCIPALE ☠️  ", "yellow", attrs=["bold"])
        nuovo_mondo.stampa_lenta("="*60, "cyan", attrs=["bold"])
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
            esegui_partita(True, None)

        elif scelta == "2": #CONTINUA PARTITA
            if len(salvataggi_in_corso) == 0:
                nuovo_mondo.stampa_lenta("\n❌ Nessun salvataggio.", "red", attrs=["bold"])
                time.sleep(1.5)
            else:
                nuovo_mondo.pulisci_schermo()
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
                    nuovo_mondo.stampa_lenta("❌ Non trovato.", "red", attrs=["bold"])
                    time.sleep(1.5)

        elif scelta == "3": #STATISTICHE GLOBALI
            nuovo_mondo.mostra_statistiche_globali(dati)

        elif scelta == "4": #ESPLORA ARCHIVI
            nuovo_mondo.pulisci_schermo()
            print("\n🔍 ARCHIVI:\n")
            if len(dati["salvataggi"]) == 0:
                nuovo_mondo.stampa_lenta("❌ Nessuna partita.", "red", attrs=["bold"])
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
                nuovo_mondo.pulisci_schermo()
                s = dati["salvataggi"][da_cercare]
                sp = s["stato"]
                nuovo_mondo.stampa_lenta("\n📜 DETTAGLI: " + da_cercare, "yellow", attrs=["bold"])
                print("🏴‍☠️ Capitano: " + s["capitano"] + " | Esito: " + sp["esito"] + " | Fase: " + sp["fase"])
                print()
                nuovo_mondo.stampa_lenta("💰 RISORSE:", "green")
                print("  🪙 Budget: " + str(int(sp["budget"])))

                for cat in sp["scorte"]:
                    print("  " + cat.capitalize() + ": " + str(round(sp["scorte"][cat], 1)))

                print("  🛡️ Integrità: " + str(sp["integrita"]) + "%")
                print("  ⚠️ Ammutinamento: " + str(sp["punti_ammutinamento"]))
                print("  🗓️ Settimane: " + str(sp["settimane_percorse"]))
                print()
                nuovo_mondo.stampa_lenta("👥 EQUIPAGGIO:", "cyan")

                for ruolo in sp["equipaggio"]:
                    n_p = sp["equipaggio"][ruolo]
                    if n_p > 0:
                        print("  " + Stati_Ingaggio.NOMI_RUOLO[ruolo] + ": " + str(n_p))

                print()
                nuovo_mondo.stampa_lenta("📦 MERCI:", "magenta")

                for merce in sp["merci"]:
                    qty = sp["merci"][merce]
                    if qty > 0:
                        print("  " + merce + ": " + str(qty))

                nuovo_mondo.stampa_lenta("🔮 BARATTO:", "yellow")

                for r in sp["risorse_baratto"]:
                    qty = sp["risorse_baratto"][r]
                    if qty > 0:
                        print("  " + r + ": " + str(round(qty, 1)))

                input(colored("\n📖 Invio per tornare ", "dark_grey"))
            else:
                nuovo_mondo.stampa_lenta("\n❌ Non trovato.", "red")
                time.sleep(1.5)


        elif scelta == "0": #ESCI
            nuovo_mondo.stampa_lenta("\n🌊 Addio, Capitano.", "cyan")
            sys.exit()

        else: #ERRORE
            nuovo_mondo.stampa_lenta("\n❌ Scelta non valida.", "red")
            time.sleep(1)

menu_principale()