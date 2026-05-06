"""
Leo — Gestione di:
  - Struttura dati dello stato (crea_stato_iniziale → in nuovo_mondo.py)
  - Fase 1: Arruolamento della flotta
  - Fase 2: Acquisto provviste
  - Fase 3: Acquisto merci
  - Utility: stampa_risorse, conta_equipaggio, aggiungi_membro, etc.
"""

from termcolor import colored, cprint
import random
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

# MERCI-1 fix: prezzi allineati al resto del progetto (nuovo_mondo.py / baratto)
COSTI_MERCI = {
    "bottiglie_medicinale": 30,
    "armi": 50,
    "sale": 20,
    "stoffa": 25,
    "coltelli": 15,
    "diamanti": 200
}

# TODO-49: settimane stimate totali usate per il suggerito acquisto scorte
SETTIMANE_STIMATE_VIAGGIO = 16

# Limite massimo equipaggio (INGAGGIO-1)
MAX_EQUIPAGGIO = 16

# Punti ammutinamento per nessun cuoco (TODO-13)
PA_NESSUN_CUOCO = 30

# ==========================================
# UTILITY DI STAMPA
# ==========================================

def stampa_risorse(stato):
    """Mostra risorse correnti del giocatore."""
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
    """Conta il totale di membri equipaggio."""
    return sum(stato['equipaggio'].values())

def aggiungi_membro(stato, ruolo, nome=None):
    """
    Aggiunge un membro con morale individuale.
    BUG-5 fix: il nome viene calcolato PRIMA di incrementare l'equipaggio,
    usando il contatore progressivo per ruolo per evitare salti di indice.
    """
    if nome is None:
        # Conta quanti membri di questo ruolo esistono già (prima di aggiungere)
        n_esistenti = stato['equipaggio'].get(ruolo, 0)
        nome = f"{NOMI_RUOLO.get(ruolo, ruolo)}_{n_esistenti + 1}"
    stato['equipaggio'][ruolo] = stato['equipaggio'].get(ruolo, 0) + 1
    stato['morale_individuale'][nome] = 100
    return nome

def rimuovi_membro(stato, ruolo):
    """
    Rimuove il membro con morale più bassa del ruolo dato.
    BUG-2 fix: aggiorna costo_sett_ruolo sottraendo il costo/sett del membro
    rimosso, in modo che il calcolo stipendi finali non conti i morti.
    """
    if stato['equipaggio'].get(ruolo, 0) > 0:
        stato['equipaggio'][ruolo] -= 1
        chiavi_ruolo = [k for k in stato['morale_individuale']
                        if k.startswith(NOMI_RUOLO.get(ruolo, ruolo))]
        if chiavi_ruolo:
            vittima = min(chiavi_ruolo, key=lambda k: stato['morale_individuale'][k])
            del stato['morale_individuale'][vittima]
            # BUG-2 fix: decrementa il debito stipendiale del ruolo perso
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
    """
    TODO-11: morte automatica membri con morale = 0.
    Rimuove dalla morale_individuale e decrementa l'equipaggio.
    """
    morti = [k for k, v in list(stato['morale_individuale'].items()) if v <= 0]
    for morto in morti:
        del stato['morale_individuale'][morto]
        for ruolo, nome_singolo in NOMI_RUOLO.items():
            if morto.startswith(nome_singolo):
                stato['equipaggio'][ruolo] = max(0, stato['equipaggio'].get(ruolo, 0) - 1)
                # BUG-2 fix: aggiorna anche il debito stipendiale
                costo_sett = COSTI_RUOLO.get(ruolo, 0)
                if costo_sett > 0 and ruolo in stato.get('costo_sett_ruolo', {}):
                    stato['costo_sett_ruolo'][ruolo] = max(
                        0, stato['costo_sett_ruolo'][ruolo] - costo_sett
                    )
                cprint(f"  💀 {morto} è morto per morale a zero!", "red", attrs=["bold"])
                break

def varia_morale_tutti(stato, delta, motivo=""):
    """
    Varia morale di tutti i membri dell'equipaggio.
    Chiama controlla_morti_morale_zero dopo ogni variazione (TODO-11).
    """
    for k in stato['morale_individuale']:
        stato['morale_individuale'][k] = max(
            0, min(100, stato['morale_individuale'][k] + delta)
        )
    if motivo:
        segno = "📈" if delta > 0 else "📉"
        variazione_stat(
            f"{segno} Morale {'+' if delta > 0 else ''}{delta} ({motivo})",
            "green" if delta > 0 else "red"
        )
    controlla_morti_morale_zero(stato)

def aggiungi_punti_ammutinamento(stato, punti, motivo=""):
    """TODO-13: aggiunge punti ammutinamento con log."""
    stato['punti_ammutinamento'] = stato.get('punti_ammutinamento', 0) + punti
    if motivo:
        variazione_stat(f"⚠️  +{punti} punti ammutinamento ({motivo})", "red")

# ==========================================
# TODO-12: EQUIPAGGIO BASSO MORALE
# ==========================================

def equipaggio_basso_morale(stato, soglia=30):
    """
    TODO-12: restituisce True se più della metà dell'equipaggio
    ha morale ≤ soglia (usato dal motore viaggio per +1 settimana).
    """
    morali = list(stato.get('morale_individuale', {}).values())
    if not morali:
        return False
    bassi = sum(1 for m in morali if m <= soglia)
    return bassi > len(morali) / 2

# ==========================================
# GESTIONE SETTIMANE E SCORTE
# ==========================================

def incrementa_settimane(stato, n=1):
    """Incrementa le settimane realmente percorse per il calcolo stipendi."""
    stato['settimane_percorse'] = stato.get('settimane_percorse', 0) + n

def consuma_scorte_dettagliate(stato, moltiplicatore=1.0):
    """
    TODO-05: consumi settimanali specifici per categoria.
    STATO-7: applica razioni_moltiplicatore per categoria.
    """
    n = conta_equipaggio(stato)
    esaurite = []

    # STATO-7: assicura che razioni_moltiplicatore esista (difesa contro
    # stati salvati pre-refactor che non hanno il campo)
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
            varia_morale_tutti(stato, -10, f"scorte {cat} esaurite")
            aggiungi_punti_ammutinamento(stato, 15, f"scorte {cat} esaurite")

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
    """
    TODO-01/02/03: esattamente 1 per ruolo obbligatorio,
    costi differenziati, pagamento differito a fine viaggio.
    INGAGGIO-1: limite massimo di 16 membri totali.
    """
    import nuovo_mondo
    import Arrivo_GameOver

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

        # INGAGGIO-1: opzione marinaio extra disabilitata a limite raggiunto
        if ciurma_tot < MAX_EQUIPAGGIO:
            print(colored("  6.", "magenta") + " 🪢 Ingaggia Marinaio Extra (supporto in combattimento)")
        else:
            print(colored("  6.", "dark_grey") + f" 🪢 Limite equipaggio raggiunto ({MAX_EQUIPAGGIO}/{MAX_EQUIPAGGIO})")

        scelta = nuovo_mondo.chiedi_scelta(
            colored("\n👉 Scegli (0-6): ", "magenta", attrs=["bold"]),
            ['0', '1', '2', '3', '4', '5', '6']
        )

        if scelta == "0":
            # TODO-01: blocco obbligatorio — non si può salpare senza tutti i ruoli
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

            if stato['equipaggio'].get(ruolo_scelto, 0) > 0:
                cprint(
                    f"\n❌ Hai già un {NOMI_RUOLO[ruolo_scelto]}! Ogni ruolo richiede esattamente 1 membro.",
                    "red"
                )
                time.sleep(1.5)
                continue

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

            # TODO-02/03: costo differenziato, registrato come debito (non sottratto subito)
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
        return Arrivo_GameOver.game_over(
            "Senza ciurma, i creditori ti raggiungono sul molo. Fine.", stato, capitano
        )
    return True

# ==========================================
# FASE 2: ACQUISTO PROVVISTE
# ==========================================

def fase_acquisto_provviste(stato, capitano):
    """
    TODO-04/05/06: 4 categorie, consumi specifici, dimezzamento/raddoppio razioni.
    TODO-49: avviso se budget insufficiente per le settimane stimate.
    STATO-7 fix: aggiorna razioni_moltiplicatore invece di scorte dirette.
    TODO-06 fix: costo raddoppio calcolato sulla quantità aggiuntiva corretta.
    """
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

    # TODO-49: avviso se il budget non copre il viaggio stimato
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

    # EPILOGO-4 fix: traccia spese iniziali (campo garantito da crea_stato_iniziale)
    stato['spese_iniziali'] = stato.get('spese_iniziali', 0) + costo_totale

    # ──────────────────────────────────────────
    # TODO-06: Step 2 — gestione razioni iniziali
    # STATO-7 fix: si aggiorna razioni_moltiplicatore, NON le scorte direttamente.
    #   Il consumo settimanale sarà poi: consumo_base × moltiplicatore.
    # TODO-06 fix: il costo del raddoppio è pari alle scorte acquistate
    #   (la quantità aggiuntiva uguale all'originale), calcolato PRIMA
    #   di modificare il moltiplicatore.
    # ──────────────────────────────────────────
    print()
    cprint("─"*60, "yellow")
    cprint("📋 FASE 2 - GESTIONE RAZIONI INIZIALI", "yellow", attrs=["bold"])
    nuovo_mondo.stampa_lenta(
        "Puoi regolare le razioni per categoria (influenza morale e ammutinamento).", "cyan"
    )
    print(f"  Dimezzare:   -5 morale, +30 punti ammutinamento")
    print(f"  Raddoppiare: +5 morale (costa le scorte originali in monete aggiuntive)")
    print()

    # STATO-7: assicura che il campo esista (difesa per salvataggi vecchi)
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
            # TODO-06: aggiorna il moltiplicatore (STATO-7)
            stato['razioni_moltiplicatore'][cat] *= 0.5
            varia_morale_tutti(stato, -5, f"razioni {cat} dimezzate")
            aggiungi_punti_ammutinamento(stato, 30, "razioni ridotte")

        elif scelta_razione == 'R':
            # TODO-06 fix: costo = quantità acquistata × prezzo unitario
            # (si acquista una quantità aggiuntiva pari a quella già caricata)
            quantita_aggiuntiva = stato['scorte'][cat]
            costo_extra = quantita_aggiuntiva * COSTI_SCORTE[cat]

            if stato['budget'] >= costo_extra:
                stato['razioni_moltiplicatore'][cat] *= 2.0
                stato['budget'] -= costo_extra
                varia_morale_tutti(stato, +5, f"razioni {cat} raddoppiate")
                cprint(
                    f"  💰 Spesi {costo_extra:.0f}🪙 per raddoppiare {cat} | "
                    f"Budget: {stato['budget']:.0f}🪙",
                    "yellow"
                )
                # EPILOGO-4: traccia anche queste spese
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
    """
    TODO-07/08: 6 tipi di merci barattabili, niente legno/carpentiere.
    MERCI-1 fix: prezzi allineati al resto del progetto (COSTI_MERCI).
    BUG-3 fix: le spese vengono calcolate incrementalmente durante l'acquisto,
    non a posteriori sulle merci totali (che potrebbe includere stock precedenti).
    EPILOGO-4 fix: traccia le spese in stato['spese_iniziali'].
    """
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

    # MERCI-1 fix: usa COSTI_MERCI allineati
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

    # BUG-3 fix: si accumula la spesa di questa sessione di acquisto,
    # non si ricalcola sull'intero stato['merci'] (che include stock pre-esistenti)
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

    # EPILOGO-4 fix: traccia spese merci nella sessione corrente
    stato['spese_iniziali'] = stato.get('spese_iniziali', 0) + spesa_merci_sessione

    cprint(f"\n🪙 Budget rimasto: {stato['budget']:.0f}", "cyan", attrs=["bold"])
    time.sleep(1.5)
    return True

# ==========================================
# UTILITY: NORMALIZZAZIONE STATO
# ==========================================

def normalizza_stato_ingaggio(stato):
    """
    Aggiunge i campi gestiti da questo modulo se mancanti
    (compatibilità con salvataggi precedenti al refactor).
    Chiamare da nuovo_mondo.normalizza_stato().
    """
    stato.setdefault('debito_equipaggio', 0)
    stato.setdefault('costo_sett_ruolo', {})
    stato.setdefault('settimane_percorse', 0)
    stato.setdefault('naufraghi_tot', 0)
    stato.setdefault('spese_iniziali', 0)          # EPILOGO-4
    stato.setdefault('razioni_moltiplicatore', {   # STATO-7
        c: 1.0 for c in CONSUMI_SETTIMANALI_PER_MEMBRO
    })
    # Assicura che tutti i campi di razioni_moltiplicatore esistano
    for cat in CONSUMI_SETTIMANALI_PER_MEMBRO:
        stato['razioni_moltiplicatore'].setdefault(cat, 1.0)
    # Pulizia chiavi non valide in costo_sett_ruolo (TODO-50)
    chiavi_non_valide = [k for k in stato['costo_sett_ruolo'] if k not in COSTI_RUOLO]
    for k in chiavi_non_valide:
        del stato['costo_sett_ruolo'][k]
    return stato


def campi_stato_iniziale():
    """
    Restituisce i campi di competenza di questo modulo
    da includere in crea_stato_iniziale() in nuovo_mondo.py.
    """
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
        "spese_iniziali": 0,           # EPILOGO-4
        "razioni_moltiplicatore": {    # STATO-7
            "verdura": 1.0,
            "frutta": 1.0,
            "carne": 1.0,
            "acqua": 1.0,
        },
    }