#Limonta
import Stati_Ingaggio
import nuovo_mondo
import random


def varia_morale_tutti(stato, delta:int, motivo=""):
    delta_map = {
        "venti favorevoli": lambda: random.randint(5, 15),
        "razioni ridotte": -5,
        "razioni aumentate": +5,
        "scorte esaurite": -10,
        "collega caduto in mare": -15,
        "morte in mare": -15,
        "pesca miracolosa": +5,
        "tempesta miracolosa": +15,
        "presagio di sfiga": -20,
        "ottimismo": +10,
    }

    if motivo in delta_map:
        valore = delta_map[motivo]
        if callable(valore): # callable = funzione che restituisce un valore dinamico da un oggetto non definito
            delta = delta_map[motivo]()  
        else:
            delta = valore

    for k in stato["morale_individuale"]:
        stato["morale_individuale"][k] = max(0, min(100, stato["morale_individuale"][k] + delta))

    if motivo:
        nuovo_mondo.variazione_stat(f"📊 Morale {delta:+} ({motivo})", "green" if delta > 0 else "red")

    controlla_morti_morale_zero(stato)

def controlla_morti_morale_zero(stato):
    morti = [k for k, v in stato["morale_individuale"].items() if v <= 0]

    for morto in morti:
        del stato["morale_individuale"][morto]

        for ruolo, nome in Stati_Ingaggio.NOMI_RUOLO.items():
            if morto.startswith(nome):
                stato["equipaggio"][ruolo] = max(0, stato["equipaggio"].get(ruolo, 0) - 1)
                nuovo_mondo.stampa_lenta(f"💀 {morto} morto per morale zero", "red", attrs=["bold"])
                break


def equipaggio_basso_morale(stato, soglia=30):
    morali = list(stato["morale_individuale"].values())
    if not morali:
        return False
    bassi = sum(1 for m in morali if m <= soglia)
    return bassi > len(morali) / 2


def calcola_ammutinamento(stato):
    p = 0
    cause = []

    if any(v < 1 for v in stato["razioni_moltiplicatore"].values()):
        p += 30
        cause.append("Razioni ridotte")

    if stato["equipaggio"].get("cuochi", 0) == 0:
        p += 30
        cause.append("Nessun cuoco a bordo")

    if stato.get("albatro_ucciso"):
        p += 30
        cause.append("Presagio di sfiga (albatro ucciso)")

    if stato["avvistamenti_albatro"] > 0 and not stato.get("albatro_ucciso"):
        p -= 20
        cause.append("Ottimismo (avvistamento albatro)")

    if Stati_Ingaggio.conta_equipaggio(stato) > 12:
        p += 30
        cause.append("Nave troppo affollata")

    p += 10 * stato.get("settimane_extra", 0)
    p -= 10 * stato.get("settimane_risparmiate", 0)

    if p >= 100:
        nuovo_mondo.game_over("Ammutinamento totale", "", "")
    elif 1 <= p < 100:
        nuovo_mondo.stampa_lenta(f"⚠️ Ammutinamento: {p}% | Cause: {', '.join(cause)}", "red")

    return p, cause


def aggiungi_punti_ammutinamento(stato, punti, motivo=""):
    stato['punti_ammutinamento'] = stato.get('punti_ammutinamento', 0) + punti
    if motivo:
        nuovo_mondo.variazione_stat(f"⚠️  +{punti} punti ammutinamento ({motivo})", "red")


# ==========================================
# UTILITÀ
# ==========================================

def perdita_frazione(valore):
    return int(valore * random.choice([1/2, 1/3, 1/4, 1/5]))


# ==========================================
# EVENTI
# ==========================================

def evento_uomo_in_mare(stato):  # A
    nuovo_mondo.stampa_lenta("🌊 UOMO IN MARE! Un'onda gigantesca spazza il ponte senza preavviso!", "red", attrs=["bold"])
    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]

    if ruoli_vivi:
        ruolo = random.choice(ruoli_vivi)
        vittima = Stati_Ingaggio.rimuovi_membro(stato, ruolo)
        varia_morale_tutti(stato, -15, "collega caduto in mare")
        nuovo_mondo.variazione_stat(f"💀 Hai perso {vittima or f'1 {ruolo}'}!", "red")
        aggiungi_punti_ammutinamento(stato, 10, "morte in mare")
    else:
        nuovo_mondo.stampa_lenta("Miracolosamente, nessuno cade.", "green")


def evento_verdura_in_mare(stato):  # B
    stato["merci"]["verdura"] = perdita_frazione(stato["merci"]["verdura"])
    nuovo_mondo.stampa_lenta("🌊 Un'onda strappa verdura dalla nave", "yellow")


def evento_frutta_in_mare(stato):  # C
    stato["merci"]["frutta"] = perdita_frazione(stato["merci"]["frutta"])
    nuovo_mondo.stampa_lenta("🌊 Un'onda strappa frutta dalla nave", "yellow")


def evento_carne_in_mare(stato):  # D
    stato["merci"]["carne"] = perdita_frazione(stato["merci"]["carne"])
    nuovo_mondo.stampa_lenta("🌊 Un'onda strappa carne dalla nave", "yellow")


def evento_acqua_in_mare(stato):  # E
    stato["merci"]["acqua"] = perdita_frazione(stato["merci"]["acqua"])
    nuovo_mondo.stampa_lenta("🌊 Un'onda strappa acqua dalla nave", "yellow")


def evento_pesca_miracolosa(stato):  # F
    nuovo_mondo.stampa_lenta("🎣 Un banco di pesci enormi circonda la nave. Pesca miracolosa!", "green", attrs=["bold"])
    carne_guadagnata = random.randint(11, 20)
    stato["merci"]["carne"] = stato["merci"].get("carne", 0) + carne_guadagnata
    nuovo_mondo.variazione_stat(f"📈 +{carne_guadagnata} 🥩 Carne (pesca miracolosa)", "green")
    varia_morale_tutti(stato, +5, "pesca miracolosa")


def evento_tempesta_miracolosa(stato):  # G
    nuovo_mondo.stampa_lenta("⛈️  Una tempesta provvidenziale! La pioggia riempie ogni contenitore e lava i malati.", "cyan", attrs=["bold"])
    acqua_guadagnata = random.randint(11, 20)
    stato["merci"]["acqua"] = stato["merci"].get("acqua", 0) + acqua_guadagnata
    nuovo_mondo.variazione_stat(f"📈 +{acqua_guadagnata} 💧 Acqua", "green")
    varia_morale_tutti(stato, +15, "tempesta miracolosa")


def evento_venti_favorevoli(stato):  # H
    nuovo_mondo.stampa_lenta("💨 VENTI FAVOREVOLI! Le vele si gonfiano al massimo. Avanzate di settimane in giorni!", "green", attrs=["bold"])
    stato['settimane_risparmiate'] = stato.get('settimane_risparmiate', 0) + 1
    bonus = random.randint(5, 15)
    varia_morale_tutti(stato, bonus, "venti favorevoli")
    nuovo_mondo.variazione_stat("📈 Viaggio accorciato di 1 settimana!", "green")


def evento_cattivo_tempo(stato):  # I
    stato["merci"]["bottiglie_medicinale"] = perdita_frazione(stato["merci"]["bottiglie_medicinale"])
    nuovo_mondo.stampa_lenta("⛈️  Cattivo tempo: bottiglie di medicinale danneggiate", "yellow")


def evento_ondata(stato):  # J
    stato["merci"]["armi"] = perdita_frazione(stato["merci"]["armi"])
    nuovo_mondo.stampa_lenta("🌊 Ondata gigantesca: armi danneggiate dall'acqua", "yellow")


def evento_infestazione_ratti(stato):  # K
    stato["merci"]["stoffa"] = perdita_frazione(stato["merci"]["stoffa"])
    nuovo_mondo.stampa_lenta("🐭 Infestazione di ratti: stoffa danneggiata", "yellow")


def evento_albatro(stato):  # ALBATRO
    if stato["merci"]["armi"] <= 0:
        nuovo_mondo.stampa_lenta("🐦 Un albatro maestoso vola vicino... ma senza armi, non puoi fare nulla.", "cyan")
        stato["avvistamenti_albatro"] += 1
        return

    vivi = Stati_Ingaggio.conta_equipaggio(stato)
    max_tiri = min(stato["merci"]["armi"], vivi)

    nuovo_mondo.stampa_lenta(f"🐦 Un albatro gigantesco appare! Hai {max_tiri} tentativi disponibili.", "cyan")

    if not nuovo_mondo.chiedi_opzione("Vuoi sparare all'albatro?"):
        stato["avvistamenti_albatro"] += 1
        nuovo_mondo.stampa_lenta("🐦 L'albatro vola via indisturbato.", "cyan")
        return

    armi_usate = 0
    abbattuto = False
    tentativo = 1

    while tentativo <= max_tiri and abbattuto == False:
        armi_usate += 1
        if random.random() < 0.5:
            abbattuto = True
            nuovo_mondo.stampa_lenta(f"  🎯 Tentativo {tentativo}: COLPITO!", "green")
        else:
            nuovo_mondo.stampa_lenta(f"  ❌ Tentativo {tentativo}: mancato", "yellow")
        tentativo += 1

    stato["merci"]["armi"] -= armi_usate

    if abbattuto == True:
        carne_aggiunta = random.randint(10, 15)
        stato["merci"]["carne"] = stato["merci"].get("carne", 0) + carne_aggiunta
        stato["albatro_ucciso"] = True
        stato["avvistamenti_albatro"] += 1
        nuovo_mondo.stampa_lenta(f"☠️  Albatro abbattuto! +{carne_aggiunta} kg di carne fresca", "red", attrs=["bold"])
        nuovo_mondo.stampa_lenta(f"⚠️  Hai usato {armi_usate} armi che non potranno essere barattate.", "yellow")
    else:
        stato["avvistamenti_albatro"] += 1
        nuovo_mondo.stampa_lenta("🐦 L'albatro scappa dopo il fuoco. Cattivo presagio...", "cyan")


def evento_scialuppa(stato):  # SCIALUPPA
    nuovo_mondo.stampa_lenta("🛟 Scialuppa in difficoltà avvistata nel mare!", "cyan", attrs=["bold"])

    if not nuovo_mondo.chiedi_opzione("Vuoi salvare i 4 naufraghi?"):
        nuovo_mondo.stampa_lenta("⛵ La scialuppa si allontana al largo. Non succede nulla.", "cyan")
        return

    for i in range(4):
        ruolo = random.choice(list(Stati_Ingaggio.NOMI_RUOLO.keys()))
        nome = Stati_Ingaggio.NOMI_RUOLO[ruolo]
        stato["equipaggio"][ruolo] = stato["equipaggio"].get(ruolo, 0) + 1
        morale_casuale = random.randint(25, 75)
        stato["morale_individuale"][nome] = morale_casuale
        nuovo_mondo.stampa_lenta(f"  ✓ {nome} ({ruolo}) salvato, morale: {morale_casuale}", "green")

    merci_cassa = ["armi", "sale", "stoffa", "coltelli", "diamanti"]
    nuovo_mondo.stampa_lenta("  🎁 Cassa ritrovata:", "yellow")
    for m in merci_cassa:
        bonus = random.randint(10, 20)
        stato["merci"][m] = stato["merci"].get(m, 0) + bonus
        nuovo_mondo.stampa_lenta(f"     +{bonus} {m}", "yellow")


def evento_epidemia(stato):  # EPIDEMIA
    malati = []
    curati = []
    morti = []

    medici = stato["equipaggio"].get("medici", 0)
    bottiglie = stato["merci"]["bottiglie_medicinale"]

    nuovo_mondo.stampa_lenta("🦠 EPIDEMIA! Una malattia misteriosa dilaga sulla nave!", "yellow", attrs=["bold"])

    for membro in list(stato["morale_individuale"].keys()):
        if random.random() < 0.7:
            malati.append(membro)

    for membro in malati:
        if medici > 0 and bottiglie > 0:
            bottiglie -= 1
            curati.append(membro)
            nuovo_mondo.stampa_lenta(f"  ✓ {membro} curato", "green")
        else:
            morti.append(membro)
            nuovo_mondo.stampa_lenta(f"  💀 {membro} non poteva essere salvato", "red")

    stato["merci"]["bottiglie_medicinale"] = bottiglie

    for membro in morti:
        if membro in stato["morale_individuale"]:
            del stato["morale_individuale"][membro]
        for ruolo, nome in Stati_Ingaggio.NOMI_RUOLO.items():
            if membro.startswith(nome):
                stato["equipaggio"][ruolo] = max(0, stato["equipaggio"].get(ruolo, 0) - 1)
                break

    nuovo_mondo.stampa_lenta(
        f"🦠 Epidemia riassunto | Malati: {len(malati)} | Curati: {len(curati)} | Morti: {len(morti)} | Bottiglie rimaste: {bottiglie}",
        "yellow" if len(morti) == 0 else "red"
    )


def evento_pirati(stato):  # PIRATI
    pirati = random.randint(3, 10)
    equipaggio_vivo = Stati_Ingaggio.conta_equipaggio(stato)
    difensori = min(stato["merci"]["armi"], equipaggio_vivo)

    uomini_persi = max(0, pirati - difensori)
    stato["merci"]["armi"] = max(0, stato["merci"]["armi"] - difensori)

    if uomini_persi <= 0:
        nuovo_mondo.stampa_lenta(f"⚔️  Attacco pirata respinto! {pirati} pirati vs {difensori} difensori", "green", attrs=["bold"])
        varia_morale_tutti(stato, +5, "vittoria contro i pirati")
        return

    nuovo_mondo.stampa_lenta(f"⚔️  ATTACCO PIRATA! {pirati} pirati vs {difensori} difensori | {uomini_persi} perdite", "red", attrs=["bold"])

    for i in range(min(uomini_persi, equipaggio_vivo)):
        vittima = Stati_Ingaggio.rimuovi_membro(stato, None)
        nuovo_mondo.stampa_lenta(f"  💀 {vittima or '1 membro'} caduto in battaglia", "red")

    varia_morale_tutti(stato, -15, "morte in battaglia")
    aggiungi_punti_ammutinamento(stato, 15, "vittime in battaglia pirata")


def evento_timone(stato):  # TIMONE
    if stato["equipaggio"].get("meccanici", 0) > 0:
        stato["settimane_extra"] = stato.get("settimane_extra", 0) + 1
        nuovo_mondo.stampa_lenta("🔧 Un meccanico ripara il timone rapidamente (+1 settimana)", "green")
    else:
        extra = random.randint(2, 4)
        stato["settimane_extra"] = stato.get("settimane_extra", 0) + extra
        nuovo_mondo.stampa_lenta(f"⚙️  Timone riparato malamente (+{extra} settimane)", "yellow")


def evento_vento(stato):  # VENTO
    if stato["equipaggio"].get("navigatori", 0) > 0:
        stato["settimane_extra"] = stato.get("settimane_extra", 0) + 1
        nuovo_mondo.stampa_lenta("🧭 Un navigatore esperto gestisce le raffiche (+1 settimana)", "green")
    else:
        extra = random.randint(2, 4)
        stato["settimane_extra"] = stato.get("settimane_extra", 0) + extra
        nuovo_mondo.stampa_lenta(f"🌪️  Raffiche di vento causano rallentamento (+{extra} settimane)", "yellow")


def evento_isola(stato):  # ISOLA
    nuovo_mondo.stampa_lenta("🏝️  Un'isola sconosciuta appare all'orizzonte!", "cyan")

    if not nuovo_mondo.chiedi_opzione("Approdare sull'isola?"):
        nuovo_mondo.stampa_lenta("⛵ Decidi di non approdare e continui il viaggio", "cyan")
        return

    extra = random.choice([1, 2])
    stato["settimane_extra"] = stato.get("settimane_extra", 0) + extra
    nuovo_mondo.stampa_lenta(f"🏝️  Approdo all'isola (+{extra} settimane)", "yellow")

    if random.random() > 0.5:
        nuovo_mondo.stampa_lenta("🏝️  L'isola è disabitata. Non c'è nulla di interessante.", "cyan")
        return

    if random.random() < 0.5:
        nuovo_mondo.stampa_lenta("👹 Gli abitanti sono ostili! Fuggi rapidamente dalla spiaggia!", "red", attrs=["bold"])
        return

    nuovo_mondo.stampa_lenta("🏝️  Gli abitanti sono pacifici e accoglienti!", "green", attrs=["bold"])

    if stato["avvistamenti_albatro"] > 0 and not stato.get("albatro_ucciso"):
        bonus = random.randint(20, 40)
        ragione = "(fortunati! Albatro vivo visto)"
    else:
        bonus = random.randint(5, 20)
        ragione = "(baratto amichevole)"

    merci_bonus = ["armi", "sale", "stoffa", "coltelli", "diamanti"]
    nuovo_mondo.stampa_lenta(f"  🎁 Doni ricevuti {ragione}:", "green")
    for m in merci_bonus:
        stato["merci"][m] = stato["merci"].get(m, 0) + bonus
        nuovo_mondo.stampa_lenta(f"     +{bonus} {m}", "green")

    varia_morale_tutti(stato, +10, "approdo amichevole")


# ==========================================
# GESTIONE EVENTI CASUALI
# ==========================================

# CORREZIONE: tutti gli eventi (tranne albatro, pesca, tempesta, venti) sono UNICI per specifica
EVENTI_UNICI = {
    "uomo_in_mare":         evento_uomo_in_mare,
    "verdura_in_mare":      evento_verdura_in_mare,
    "frutta_in_mare":       evento_frutta_in_mare,
    "carne_in_mare":        evento_carne_in_mare,
    "acqua_in_mare":        evento_acqua_in_mare,
    "cattivo_tempo":        evento_cattivo_tempo,
    "ondata":               evento_ondata,
    "infestazione_ratti":   evento_infestazione_ratti,
    "scialuppa":            evento_scialuppa,
    "epidemia":             evento_epidemia,
    "pirati":               evento_pirati,
    "timone":               evento_timone,
    "vento":                evento_vento,
    "isola":                evento_isola,
}

EVENTI_RIPETIBILI = {
    "albatro":              evento_albatro,
    "pesca_miracolosa":     evento_pesca_miracolosa,
    "tempesta_miracolosa":  evento_tempesta_miracolosa,
    "venti_favorevoli":     evento_venti_favorevoli,
}


def gestisci_evento_casuale(stato):
    nuovo_mondo.stampa_lenta("\n" + "~"*60, "blue", attrs=["bold"])
    nuovo_mondo.stampa_lenta("⚠️   EVENTO IN MARE!", "yellow", attrs=["bold", "blink"])
    nuovo_mondo.stampa_lenta("~"*60, "blue", attrs=["bold"])

    eventi_accaduti = stato.get('eventi_accaduti', [])

    if stato.get('avvistamenti_albatro', 0) >= 3:
        eventi_ripetibili_filtrati = {k: v for k, v in EVENTI_RIPETIBILI.items() if k != 'albatro'}
    else:
        eventi_ripetibili_filtrati = EVENTI_RIPETIBILI

    eventi_unici_disponibili = {k: v for k, v in EVENTI_UNICI.items() if k not in eventi_accaduti}

    pool_ripetibili = list(eventi_ripetibili_filtrati.values())
    pool_unici = list(eventi_unici_disponibili.items())

    if pool_unici and random.random() < 0.5:
        nome_ev, funzione_ev = random.choice(pool_unici)
        eventi_accaduti.append(nome_ev)
        stato['eventi_accaduti'] = eventi_accaduti
        funzione_ev(stato)
    elif pool_ripetibili:
        random.choice(pool_ripetibili)(stato)
    else:
        nuovo_mondo.stampa_lenta("🌅 Il mare è calmo. Nessun imprevisto questa settimana.", "cyan")

    nuovo_mondo.stampa_lenta("~"*60, "blue", attrs=["bold"])


# ==========================================
# CONTROLLO SCORTE SETTIMANALE
# ==========================================

def step2_controllo_scorte(stato, settimane_rimanenti):
    nuovo_mondo.stampa_lenta("\n📊 CONTROLLO SETTIMANALE DELLE SCORTE", "blue", attrs=["bold"])

    for categoria in stato["scorte"]:
        consumo_settimanale = stato["consumi_settimanali"][categoria] * stato["razioni_moltiplicatore"].get(categoria, 1)
        scorte_attuali = stato["scorte"][categoria]

        nuovo_mondo.stampa_lenta(f"\n  {categoria.upper()}: {scorte_attuali:.1f} unità", "cyan")
        nuovo_mondo.stampa_lenta(f"    Consumo settimanale: {consumo_settimanale:.1f}", "white")
        nuovo_mondo.stampa_lenta(f"    Settimane rimanenti: {settimane_rimanenti}", "white")

        if scorte_attuali < consumo_settimanale * settimane_rimanenti:
            nuovo_mondo.stampa_lenta(f"    ⚠️  INSUFFICIENTI PER {settimane_rimanenti} SETTIMANE!", "red", attrs=["bold"])
            if nuovo_mondo.chiedi_opzione(f"Dimezzare le razioni di {categoria}?"):
                stato["razioni_moltiplicatore"][categoria] *= 0.5
                varia_morale_tutti(stato, -5, "razioni ridotte")
                nuovo_mondo.stampa_lenta(f"    ✓ Razioni di {categoria} dimezzate", "yellow")

        elif scorte_attuali > consumo_settimanale * settimane_rimanenti * 2:
            nuovo_mondo.stampa_lenta(f"    ✓ Abbondanza di {categoria}", "green", attrs=["bold"])
            if nuovo_mondo.chiedi_opzione(f"Raddoppiare le razioni di {categoria}?"):
                stato["razioni_moltiplicatore"][categoria] *= 2.0
                varia_morale_tutti(stato, +5, "razioni aumentate")
                nuovo_mondo.stampa_lenta(f"    ✓ Razioni di {categoria} raddoppiate", "green")

        if scorte_attuali <= 0:
            varia_morale_tutti(stato, -10, "scorte esaurite")
            nuovo_mondo.stampa_lenta(f"    💀 Scorte di {categoria} ESAURITE!", "red", attrs=["bold"])


# ==========================================
# CONTROLLO MORALE
# ==========================================

def controlla_morale_basso(stato):
    vivi = Stati_Ingaggio.conta_equipaggio(stato)
    if vivi == 0:
        return

    basso_morale = sum(1 for v in stato["morale_individuale"].values() if v <= 30)

    if basso_morale > vivi / 2:
        stato["settimane_extra"] = stato.get("settimane_extra", 0) + 1
        nuovo_mondo.stampa_lenta(f"😔 Morale basso diffuso: il viaggio si allunga di 1 settimana", "yellow")