#Pagnoncelli
import Morale_Eventi
import nuovo_mondo
from termcolor import colored, cprint
import time

# ==========================================
# COSTANTI
# ==========================================

COSTI_RUOLO = {
    "cuochi": 15,
    "marinai": 10,
    "meccanici": 15,
    "medici": 25,
    "navigatori": 20
}

NOMI_RUOLO = {
    "cuochi": "Cuoco",
    "marinai": "Marinaio",
    "meccanici": "Meccanico",
    "medici": "Medico",
    "navigatori": "Navigatore"
}

COSTI_SCORTE = {
    "verdura": 0.5,
    "frutta": 1.0,
    "carne": 2.0,
    "acqua": 0.5
}

CONSUMI_SETTIMANALI_PER_MEMBRO = {
    "verdura": 0.5,
    "frutta": 1.0,
    "carne": 1.0,
    "acqua": 0.5
}

COSTI_MERCI = {
    "bottiglie_medicinale": 30,
    "armi": 50,
    "sale": 20,
    "stoffa": 25,
    "coltelli": 15,
    "diamanti": 200
}

SETTIMANE_STIMATE_VIAGGIO = 16
MAX_EQUIPAGGIO = 16
PA_NESSUN_CUOCO = 30

# ==========================================
# UTILI PER STAMPA
# ==========================================

def stampa_risorse(stato):
    ciurma_totale = sum(stato['equipaggio'].values())
    cprint(
        f"👥 Ciurma: {ciurma_totale} | 🪙 Budget: {stato['budget']:.0f} | "
        f"🥬 Verdura: {stato['scorte']['verdura']:.1f}kg | "
        f"🍊 Frutta: {stato['scorte']['frutta']:.1f}kg | "
        f"🥩 Carne: {stato['scorte']['carne']:.1f}kg | "
        f"💧 Acqua: {stato['scorte']['acqua']:.1f}brl",
        "cyan", attrs=["bold"]
    )
    cprint(
        f"🛡️ Integrità: {stato.get('integrita', 100)}% | "
        f"⚠️ Punti Ammutinamento: {stato.get('punti_ammutinamento', 0)}",
        "magenta", attrs=["bold"]
    )

    morali = list(stato.get('morale_individuale', {}).values())
    if morali:
        media_morale = sum(morali) / len(morali)
        colore_morale = "green" if media_morale > 60 else ("yellow" if media_morale > 30 else "red")
        cprint(f"❤️  Morale medio equipaggio: {media_morale:.0f}/100", colore_morale, attrs=["bold"])

    sett_percorse = stato.get('settimane_percorse', 0)
    if sett_percorse > 0:
        cprint(f"🗓️  Settimane percorse: {sett_percorse}", "dark_grey")

def variazione_stat(messaggio, colore):
    cprint(f"  {messaggio}", colore, attrs=["bold"])

# ==========================================
# UTILITY EQUIPAGGIO
# ==========================================

def conta_equipaggio(stato):
    return sum(stato['equipaggio'].values())

def aggiungi_membro(stato, ruolo, nome=None):
    if nome is None:
        n_esistenti = stato['equipaggio'].get(ruolo, 0)
        nome = f"{NOMI_RUOLO.get(ruolo, ruolo)}_{n_esistenti + 1}"
    stato['equipaggio'][ruolo] = stato['equipaggio'].get(ruolo, 0) + 1
    stato['morale_individuale'][nome] = 100
    return nome

def rimuovi_membro(stato, ruolo):
    if stato['equipaggio'].get(ruolo, 0) > 0:
        stato['equipaggio'][ruolo] -= 1
        chiavi_ruolo = [k for k in stato['morale_individuale']
                        if k.startswith(NOMI_RUOLO.get(ruolo, ruolo))]
        if chiavi_ruolo:
            vittima = min(chiavi_ruolo, key=lambda k: stato['morale_individuale'][k])
            del stato['morale_individuale'][vittima]
            costo_sett = COSTI_RUOLO.get(ruolo, 0)
            if costo_sett > 0 and ruolo in stato.get('costo_sett_ruolo', {}):
                stato['costo_sett_ruolo'][ruolo] = max(
                    0, stato['costo_sett_ruolo'][ruolo] - costo_sett
                )
            return vittima
    return None

# ==========================================
# GESTIONE MORALE
# ==========================================

def controlla_morti_morale_zero(stato):
    morti = [k for k, v in list(stato['morale_individuale'].items()) if v <= 0]
    for morto in morti:
        del stato['morale_individuale'][morto]
        for ruolo, nome_singolo in NOMI_RUOLO.items():
            if morto.startswith(nome_singolo):
                stato['equipaggio'][ruolo] = max(0, stato['equipaggio'].get(ruolo, 0) - 1)
                costo_sett = COSTI_RUOLO.get(ruolo, 0)
                if costo_sett > 0 and ruolo in stato.get('costo_sett_ruolo', {}):
                    stato['costo_sett_ruolo'][ruolo] = max(
                        0, stato['costo_sett_ruolo'][ruolo] - costo_sett
                    )
                cprint(f"  💀 {morto} è morto per morale a zero!", "red", attrs=["bold"])
                break


# ==========================================
# GESTIONE SETTIMANE E SCORTE
# ==========================================

def incrementa_settimane(stato, n=1):
    stato['settimane_percorse'] = stato.get('settimane_percorse', 0) + n

def consuma_scorte_dettagliate(stato, moltiplicatore=1.0):
    n = conta_equipaggio(stato)
    esaurite = []

    if 'razioni_moltiplicatore' not in stato:
        stato['razioni_moltiplicatore'] = {c: 1.0 for c in CONSUMI_SETTIMANALI_PER_MEMBRO}

    for cat, consumo_per_membro in CONSUMI_SETTIMANALI_PER_MEMBRO.items():
        fattore_razione = stato['razioni_moltiplicatore'].get(cat, 1.0)
        consumo = consumo_per_membro * n * moltiplicatore * fattore_razione
        stato['scorte'][cat] -= consumo
        if stato['scorte'][cat] < 0:
            esaurite.append(cat)
            stato['scorte'][cat] = 0

    if esaurite:
        for cat in esaurite:
            Morale_Eventi.varia_morale_tutti(stato, -10, f"scorte {cat} esaurite")
            Morale_Eventi.aggiungi_punti_ammutinamento(stato, 15, f"scorte {cat} esaurite")

    if stato.get('punti_ammutinamento', 0) >= 100:
        return "ammutinamento"

    if stato.get('integrita', 100) <= 0:
        return "affondato"

    if esaurite:
        return "scorte_esaurite"

    return "ok"

# ==========================================
# FASE 1: ARRUOLAMENTO
# ==========================================

def fase_arruolamento(stato, capitano):

    ruoli_info = {
        "cuochi":    ("🍲 Cuoco",      15),
        "marinai":   ("🪢 Marinaio",   10),
        "meccanici": ("⚙️  Meccanico", 15),
        "medici":    ("🩸 Medico",     25),
        "navigatori":("🧭 Navigatore", 20),
    }
    RUOLI_OBBLIGATORI = list(ruoli_info.keys())

    while True:
        nuovo_mondo.pulisci_schermo()
        print()
        cprint("="*60, "green", attrs=["bold"])
        cprint("🍻 TAVERNA DEL PORTO - ARRUOLAMENTO (paga a fine viaggio)", "green", attrs=["bold"])
        nuovo_mondo.stampa_lenta(
            "Devi ingaggiare ESATTAMENTE 1 persona per ogni ruolo prima di salpare.", "yellow"
        )
        print()

        for i, (ruolo, (etichetta, costo)) in enumerate(ruoli_info.items(), 1):
            ingaggiato = stato['equipaggio'].get(ruolo, 0) > 0
            stato_str = (
                colored("✅ INGAGGIATO", "green", attrs=["bold"])
                if ingaggiato
                else colored(f"❌ {costo}🪙/sett (fine viaggio)", "red")
            )
            print(f"  {i}. {etichetta:<22} {stato_str}")

        print()
        cprint(f"🪙 Budget attuale: {stato['budget']:.0f}", "cyan")

        # INGAGGIO-1: mostra limite equipaggio
        ciurma_tot = conta_equipaggio(stato)
        colore_ciurma = "yellow" if ciurma_tot >= MAX_EQUIPAGGIO else "cyan"
        cprint(f"👥 Equipaggio attuale: {ciurma_tot}/{MAX_EQUIPAGGIO}", colore_ciurma)
        print()

        tutti_obbligatori = all(stato['equipaggio'].get(r, 0) >= 1 for r in RUOLI_OBBLIGATORI)
        mancanti = [r for r in RUOLI_OBBLIGATORI if stato['equipaggio'].get(r, 0) == 0]

        if tutti_obbligatori:
            cprint("✅ Tutti i ruoli coperti! Puoi salpare.", "green", attrs=["bold"])
            print(colored("\n  0.", "red", attrs=["bold"]) + " 🚢 SALPA! (Termina Arruolamento)")
        else:
            cprint(
                f"⚠️   Mancano ancora: {', '.join(NOMI_RUOLO[r] for r in mancanti)}",
                "yellow", attrs=["bold"]
            )
            print(colored("\n  0.", "dark_grey") + " 🚢 Salpa (NON disponibile - ingaggia prima tutti i ruoli)")

        print()
        nuovo_mondo.stampa_lenta("  ── Ingaggia membri extra ──", "dark_grey")
        opzioni_extra = {}
        lettera = ord('1')
        for ruolo, (etichetta, costo) in ruoli_info.items():
            tasto = chr(lettera)
            opzioni_extra[tasto] = ruolo
            if ciurma_tot < MAX_EQUIPAGGIO:
                print(colored(f"  {tasto}.", "magenta") + f" ➕ {etichetta} extra ({costo}🪙/sett)")
            else:
                print(colored(f"  {tasto}.", "dark_grey") + f" ➕ {etichetta} extra (limite raggiunto)")
            lettera += 1

        scelte_valide = ['0', '1', '2', '3', '4', '5'] + list(opzioni_extra.keys())
        scelta = nuovo_mondo.chiedi_scelta(colored("\n👉 Scegli (0-6): ", "magenta", attrs=["bold"]),scelte_valide)

        if scelta == "0":
            if not tutti_obbligatori:
                cprint(
                    f"\n🚫 IMPOSSIBILE SALPARE! Mancano: {', '.join(NOMI_RUOLO[r] for r in mancanti)}",
                    "red", attrs=["bold"]
                )
                nuovo_mondo.stampa_lenta("Devi ingaggiare almeno un membro per ogni ruolo.", "red")
                time.sleep(2)
                continue
            break

        ruoli_lista = list(ruoli_info.keys())

        if scelta in ['1', '2', '3', '4', '5']:
            idx = int(scelta) - 1
            ruolo_scelto = ruoli_lista[idx]
            etichetta, costo_sett = ruoli_info[ruolo_scelto]

            # INGAGGIO-1: controlla il limite anche per i ruoli obbligatori
            if conta_equipaggio(stato) >= MAX_EQUIPAGGIO:
                cprint(
                    f"\n❌ Limite equipaggio raggiunto ({MAX_EQUIPAGGIO}/{MAX_EQUIPAGGIO})! "
                    "Non puoi aggiungere altri membri.",
                    "red"
                )
                time.sleep(1.5)
                continue

            aggiungi_membro(stato, ruolo_scelto)

            stato.setdefault('debito_equipaggio', 0)
            stato['debito_equipaggio'] += costo_sett
            stato.setdefault('costo_sett_ruolo', {})
            stato['costo_sett_ruolo'][ruolo_scelto] = (
                stato['costo_sett_ruolo'].get(ruolo_scelto, 0) + costo_sett
            )
            nuovo_mondo.stampa_lenta(
                f"  ✍️  {etichetta} ingaggiato! ({costo_sett}🪙/sett — paghi a fine viaggio).", "green"
            )
            time.sleep(0.8)

        elif scelta == '6':
            # INGAGGIO-1: controlla il limite per i marinai extra
            if conta_equipaggio(stato) >= MAX_EQUIPAGGIO:
                cprint(
                    f"\n❌ Limite equipaggio raggiunto ({MAX_EQUIPAGGIO}/{MAX_EQUIPAGGIO})! "
                    "Non puoi aggiungere altri marinai.",
                    "red"
                )
                time.sleep(1.5)
                continue

            costo_sett = ruoli_info['marinai'][1]
            aggiungi_membro(stato, 'marinai')
            stato.setdefault('debito_equipaggio', 0)
            stato['debito_equipaggio'] += costo_sett
            stato.setdefault('costo_sett_ruolo', {})
            stato['costo_sett_ruolo']['marinai'] = (
                stato['costo_sett_ruolo'].get('marinai', 0) + costo_sett
            )
            nuovo_mondo.stampa_lenta(
                f"  ✍️  Marinaio extra ingaggiato! ({costo_sett}🪙/sett — paghi a fine viaggio).", "green"
            )
            time.sleep(0.8)

    if conta_equipaggio(stato) == 0:
        return nuovo_mondo.game_over(
            "Senza ciurma, i creditori ti raggiungono sul molo. Fine.", stato, capitano
        )
    return True

# ==========================================
# FASE 2: ACQUISTO PROVVISTE
# ==========================================

def fase_acquisto_provviste(stato, capitano):
    import nuovo_mondo

    nuovo_mondo.pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🏪 --- MERCATO DEL PORTO (PROVVISTE) ---", "green", attrs=["bold"])
    nuovo_mondo.stampa_lenta("Scegli bene le scorte. Ogni membro consuma ogni settimana:", "cyan")
    print()
    print(f"  🥬 Verdura:  {CONSUMI_SETTIMANALI_PER_MEMBRO['verdura']} kg/membro/sett  → {COSTI_SCORTE['verdura']}🪙/kg")
    print(f"  🍊 Frutta:   {CONSUMI_SETTIMANALI_PER_MEMBRO['frutta']} kg/membro/sett  → {COSTI_SCORTE['frutta']}🪙/kg")
    print(f"  🥩 Carne:    {CONSUMI_SETTIMANALI_PER_MEMBRO['carne']} kg/membro/sett  → {COSTI_SCORTE['carne']}🪙/kg")
    print(f"  💧 Acqua:    {CONSUMI_SETTIMANALI_PER_MEMBRO['acqua']} brl/membro/sett → {COSTI_SCORTE['acqua']}🪙/brl")
    print()

    n_eq = conta_equipaggio(stato)
    cprint(f"👥 Equipaggio: {n_eq} | 🪙 Budget: {stato['budget']:.0f}", "cyan", attrs=["bold"])

    budget_consigliato = sum(
        CONSUMI_SETTIMANALI_PER_MEMBRO[c] * n_eq * SETTIMANE_STIMATE_VIAGGIO * COSTI_SCORTE[c]
        for c in CONSUMI_SETTIMANALI_PER_MEMBRO
    )
    if stato['budget'] < budget_consigliato:
        cprint(
            f"⚠️  Budget consigliato per {SETTIMANE_STIMATE_VIAGGIO} settimane: "
            f"{budget_consigliato:.0f}🪙 — potresti avere scorte insufficienti!",
            "yellow", attrs=["bold"]
        )
    print()

    simboli = {"verdura": "🥬", "frutta": "🍊", "carne": "🥩", "acqua": "💧"}
    unita  = {"verdura": "kg", "frutta": "kg", "carne": "kg", "acqua": "barili"}

    costo_totale = 0
    for cat in ["verdura", "frutta", "carne", "acqua"]:
        n_suggerito   = CONSUMI_SETTIMANALI_PER_MEMBRO[cat] * n_eq * SETTIMANE_STIMATE_VIAGGIO
        costo_suggerito = n_suggerito * COSTI_SCORTE[cat]
        while True:
            try:
                prompt = colored(
                    f"{simboli[cat]} {cat.capitalize()} ({COSTI_SCORTE[cat]}🪙/{unita[cat]}) "
                    f"[suggerito: {n_suggerito:.1f} = {costo_suggerito:.0f}🪙 | "
                    f"budget rimasto: {stato['budget'] - costo_totale:.0f}🪙]: ",
                    "yellow", attrs=["bold"]
                )
                qty_str = nuovo_mondo.leggi_input(prompt)
                qty = float(qty_str) if qty_str.strip() else n_suggerito
                if qty < 0:
                    raise ValueError("quantità negativa")
                costo = qty * COSTI_SCORTE[cat]
                if costo_totale + costo > stato['budget']:
                    cprint(
                        f"❌ Non hai abbastanza budget! "
                        f"Budget rimasto: {stato['budget'] - costo_totale:.0f}🪙",
                        "red"
                    )
                    continue
                stato['scorte'][cat] = qty
                costo_totale += costo
                break
            except ValueError:
                cprint("❌ Inserisci un numero valido.", "red")

    stato['budget'] -= costo_totale
    cprint(
        f"\n✅ Scorte caricate! Spesi {costo_totale:.0f}🪙 | Budget rimasto: {stato['budget']:.0f}🪙",
        "green", attrs=["bold"]
    )

    stato['spese_iniziali'] = stato.get('spese_iniziali', 0) + costo_totale

    print()
    cprint("─"*60, "yellow")
    cprint("📋 FASE 2 - GESTIONE RAZIONI INIZIALI", "yellow", attrs=["bold"])
    nuovo_mondo.stampa_lenta(
        "Puoi regolare le razioni per categoria (influenza morale e ammutinamento).", "cyan"
    )
    print(f"  Dimezzare:   -5 morale, +30 punti ammutinamento")
    print(f"  Raddoppiare: +5 morale (costa le scorte originali in monete aggiuntive)")
    print()

    stato.setdefault('razioni_moltiplicatore', {c: 1.0 for c in CONSUMI_SETTIMANALI_PER_MEMBRO})

    for cat in ["verdura", "frutta", "carne", "acqua"]:
        scelta_razione = nuovo_mondo.chiedi_scelta(
            colored(
                f"{simboli[cat]} {cat.capitalize()} "
                f"({stato['scorte'][cat]:.1f} {unita[cat]}): "
                "[N] Normale | [D] Dimezza | [R] Raddoppia: ",
                "magenta"
            ),
            ['N', 'D', 'R']
        )

        if scelta_razione == 'D':
            stato['razioni_moltiplicatore'][cat] *= 0.5
            Morale_Eventi.varia_morale_tutti(stato, -5, f"razioni {cat} dimezzate")
            Morale_Eventi.aggiungi_punti_ammutinamento(stato, 30, "razioni ridotte")

        elif scelta_razione == 'R':
            quantita_aggiuntiva = stato['scorte'][cat]
            costo_extra = quantita_aggiuntiva * COSTI_SCORTE[cat]

            if stato['budget'] >= costo_extra:
                stato['razioni_moltiplicatore'][cat] *= 2.0
                stato['budget'] -= costo_extra
                Morale_Eventi.varia_morale_tutti(stato, +5, f"razioni {cat} raddoppiate")
                cprint(
                    f"  💰 Spesi {costo_extra:.0f}🪙 per raddoppiare {cat} | "
                    f"Budget: {stato['budget']:.0f}🪙",
                    "yellow"
                )
                stato['spese_iniziali'] = stato.get('spese_iniziali', 0) + costo_extra
            else:
                cprint(
                    f"  ❌ Budget insufficiente ({costo_extra:.0f}🪙 necessari, "
                    f"hai {stato['budget']:.0f}🪙). Razioni rimaste normali.",
                    "red"
                )

    time.sleep(1.5)
    return True

# ==========================================
# FASE 3: ACQUISTO MERCI
# ==========================================

def fase_merci_arsenale(stato, capitano):
    import nuovo_mondo

    nuovo_mondo.pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("⚔️  --- L'ARSENALE E IL MERCATO DELLE MERCI ---", "green", attrs=["bold"])
    nuovo_mondo.stampa_lenta(
        "Equipaggia la nave con armi e merci da barattare nel Nuovo Mondo.", "cyan"
    )
    nuovo_mondo.stampa_lenta(
        "Le bottiglie di medicinale curano le epidemie. Le armi difendono dai pirati.", "yellow"
    )
    print()

    catalogo_merci = {
        "bottiglie_medicinale": ("💊 Bottiglie Medicinale", COSTI_MERCI["bottiglie_medicinale"]),
        "armi":                 ("⚔️  Armi",               COSTI_MERCI["armi"]),
        "sale":                 ("🧂 Sale",                 COSTI_MERCI["sale"]),
        "stoffa":               ("🧵 Stoffa",               COSTI_MERCI["stoffa"]),
        "coltelli":             ("🔪 Coltelli",             COSTI_MERCI["coltelli"]),
        "diamanti":             ("💎 Diamanti",             COSTI_MERCI["diamanti"]),
    }

    cprint(f"🪙 Budget disponibile: {stato['budget']:.0f}", "cyan", attrs=["bold"])
    print()

    spesa_merci_sessione = 0

    for codice, (nome, costo) in catalogo_merci.items():
        if stato['budget'] < costo:
            cprint(f"  ❌ {nome} ({costo}🪙) - Budget insufficiente", "dark_grey")
            continue

        while True:
            try:
                qty_str = nuovo_mondo.leggi_input(
                    colored(
                        f"  {nome} ({costo}🪙/unità) "
                        f"[Budget: {stato['budget']:.0f}🪙] Quante? [0=nessuna]: ",
                        "yellow"
                    )
                )
                qty = int(qty_str) if qty_str.strip() else 0
                if qty < 0:
                    raise ValueError
                costo_tot = qty * costo
                if costo_tot > stato['budget']:
                    cprint(
                        f"  ❌ Non hai abbastanza budget! ({stato['budget']:.0f}🪙 rimasti)", "red"
                    )
                    continue
                stato['merci'][codice] = stato['merci'].get(codice, 0) + qty
                if qty > 0:
                    stato['budget'] -= costo_tot
                    spesa_merci_sessione += costo_tot
                    cprint(
                        f"  ✅ Acquistato {qty}x {nome} per {costo_tot}🪙 | "
                        f"Rimasto: {stato['budget']:.0f}🪙",
                        "green"
                    )
                break
            except ValueError:
                cprint("  ❌ Numero non valido.", "red")

    if stato['merci'].get('armi', 0) == 0:
        nuovo_mondo.stampa_lenta(
            "\n⚠️  Nessuna arma! Sarete vulnerabili agli attacchi dei pirati.",
            "yellow", attrs=["bold"]
        )

    stato['spese_iniziali'] = stato.get('spese_iniziali', 0) + spesa_merci_sessione

    cprint(f"\n🪙 Budget rimasto: {stato['budget']:.0f}", "cyan", attrs=["bold"])
    time.sleep(1.5)
    return True

# ==========================================
# UTILITY: NORMALIZZAZIONE STATO
# ==========================================

def normalizza_stato_ingaggio(stato):
    stato.setdefault('debito_equipaggio', 0)
    stato.setdefault('costo_sett_ruolo', {})
    stato.setdefault('settimane_percorse', 0)
    stato.setdefault('naufraghi_tot', 0)
    stato.setdefault('spese_iniziali', 0)          
    stato.setdefault('razioni_moltiplicatore', {   
        c: 1.0 for c in CONSUMI_SETTIMANALI_PER_MEMBRO
    })
    for cat in CONSUMI_SETTIMANALI_PER_MEMBRO:
        stato['razioni_moltiplicatore'].setdefault(cat, 1.0)
    chiavi_non_valide = [k for k in stato['costo_sett_ruolo'] if k not in COSTI_RUOLO]
    for k in chiavi_non_valide:
        del stato['costo_sett_ruolo'][k]
    return stato


def campi_stato_iniziale():
    return {
        "equipaggio": {
            "marinai": 0,
            "cuochi": 0,
            "meccanici": 0,
            "medici": 0,
            "navigatori": 0,
        },
        "scorte": {
            "verdura": 0.0,
            "frutta": 0.0,
            "carne": 0.0,
            "acqua": 0.0,
        },
        "merci": {
            "bottiglie_medicinale": 0,
            "armi": 0,
            "sale": 0,
            "stoffa": 0,
            "coltelli": 0,
            "diamanti": 0,
        },
        "morale_individuale": {},
        "debito_equipaggio": 0,
        "costo_sett_ruolo": {},
        "settimane_percorse": 0,
        "naufraghi_tot": 0,
        "spese_iniziali": 0,          
        "razioni_moltiplicatore": {    
            "verdura": 1.0,
            "frutta": 1.0,
            "carne": 1.0,
            "acqua": 1.0,
        },
    }