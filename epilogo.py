def _barra_progresso(valore, massimo, lunghezza=20):
    """Genera una barra testuale colorata per visualizzare percentuali."""
    if massimo <= 0:
        return colored("█" * lunghezza, "dark_grey")
    riempita = int((valore / massimo) * lunghezza)
    riempita = max(0, min(lunghezza, riempita))
    vuota = lunghezza - riempita
    percentuale = valore / massimo
    colore = "green" if percentuale > 0.5 else ("yellow" if percentuale > 0.25 else "red")
    return colored("█" * riempita, colore, attrs=["bold"]) + colored("░" * vuota, "dark_grey")
 
def _colore_soglia(valore, soglia_ok, soglia_warn):
    """Ritorna il colore in base alle soglie: verde/giallo/rosso."""
    if valore >= soglia_ok:
        return "green"
    elif valore >= soglia_warn:
        return "yellow"
    return "red"
 
def riepilogo_fine_settimana(stato, settimana, settimane_totali, fase_nome):
    """
    Step 4: riepilogo dettagliato a fine di ogni settimana di viaggio.
    Mostra scorte, equipaggio, morale individuale, integrità, punti ammutinamento,
    avanzamento viaggio e avvisi critici. Chiamato da _ciclo_viaggio ogni settimana.
    """
    pulisci_schermo()
    settimane_rimaste = max(0, settimane_totali - settimana)
    n = conta_equipaggio(stato)
 
    # ── Intestazione ──────────────────────────────────────────────
    cprint("\n" + "═" * 60, "yellow", attrs=["bold"])
    cprint(f"  📋  RIEPILOGO SETTIMANA {settimana}  ·  {fase_nome.upper()}  ·  ~{settimane_rimaste} RIMASTE", "yellow", attrs=["bold"])
    cprint("═" * 60, "yellow", attrs=["bold"])
 
    # ── Avanzamento viaggio ───────────────────────────────────────
    print()
    cprint("🗺️  AVANZAMENTO VIAGGIO", "cyan", attrs=["bold"])
    barra_v = _barra_progresso(settimana, settimane_totali)
    sett_extra = stato.get('settimane_extra', 0)
    sett_risp  = stato.get('settimane_risparmiate', 0)
    print(f"  {barra_v}  Sett. {settimana}/{settimane_totali}")
    if sett_extra > 0:
        cprint(f"  ⚠️  +{sett_extra} settimane extra accumulate", "red", attrs=["bold"])
    if sett_risp > 0:
        cprint(f"  💨  -{sett_risp} settimane risparmiate", "green", attrs=["bold"])
 
    # ── Stato nave ────────────────────────────────────────────────
    print()
    cprint("⚙️  STATO NAVE", "cyan", attrs=["bold"])
    integrita = stato.get('integrita', 100)
    barra_i = _barra_progresso(integrita, 100)
    col_int = _colore_soglia(integrita, 50, 25)
    print(f"  🛡️  Integrità:     {barra_i}  {colored(f'{integrita}%', col_int, attrs=['bold'])}")
 
    punti_amm = stato.get('punti_ammutinamento', 0)
    barra_a = _barra_progresso(punti_amm, 100)
    col_amm = "green" if punti_amm < 40 else ("yellow" if punti_amm < 70 else "red")
    print(f"  ⚠️  Ammutinamento: {barra_a}  {colored(f'{punti_amm}/100', col_amm, attrs=['bold'])}")
 
    # ── Scorte ────────────────────────────────────────────────────
    print()
    cprint("🥬 SCORTE DI BORDO", "cyan", attrs=["bold"])
 
    simboli_sc = {"verdura": "🥬", "frutta": "🍊", "carne": "🥩", "acqua": "💧"}
    unita_sc   = {"verdura": "kg", "frutta": "kg", "carne": "kg", "acqua": "brl"}
 
    for cat, simbolo in simboli_sc.items():
        disponibile = stato['scorte'].get(cat, 0.0)
        fabbisogno_sett = CONSUMI_SETTIMANALI_PER_MEMBRO[cat] * n
        fabbisogno_tot  = fabbisogno_sett * settimane_rimaste
        riferimento = max(fabbisogno_tot, fabbisogno_sett) or 1
        barra_s = _barra_progresso(disponibile, riferimento)
        col_s = _colore_soglia(disponibile, fabbisogno_tot, fabbisogno_sett)
        sett_coperte = (disponibile / fabbisogno_sett) if fabbisogno_sett > 0 else 99
        if sett_coperte < settimane_rimaste and sett_coperte < 2:
            avviso = colored("  ← CRITICO!", "red", attrs=["bold"])
        elif sett_coperte < settimane_rimaste:
            avviso = colored(f"  ← {sett_coperte:.1f} sett", "yellow")
        else:
            avviso = ""
        print(
            f"  {simbolo} {cat.capitalize():<8} {barra_s}  "
            f"{colored(f'{disponibile:.1f} {unita_sc[cat]}', col_s, attrs=['bold'])}"
            f"{avviso}"
        )
 
    # ── Equipaggio e morale individuale ───────────────────────────
    print()
    cprint("👥 EQUIPAGGIO & MORALE", "cyan", attrs=["bold"])
    cprint(f"  Ciurma totale: {n} membri", "white")
    print()
 
    for ruolo, n_ruolo in stato['equipaggio'].items():
        if n_ruolo == 0:
            continue
        etichetta = NOMI_RUOLO.get(ruolo, ruolo)
        chiavi_ruolo = []
        for k in stato['morale_individuale']:
            if k.startswith(etichetta):
                chiavi_ruolo.append(k)
        if chiavi_ruolo:
            for nome_membro in chiavi_ruolo:
                m = stato['morale_individuale'][nome_membro]
                barra_m = _barra_progresso(m, 100, lunghezza=12)
                col_m = _colore_soglia(m, 60, 30)
                print(
                    f"    {barra_m}  {colored(f'{m:3d}/100', col_m, attrs=['bold'])}  "
                    f"{colored(nome_membro, 'white')}"
                )
        else:
            print(f"  ⚓ {etichetta}: {n_ruolo}  (nessun dato morale)")
 
    morali = list(stato.get('morale_individuale', {}).values())
    if morali:
        media = sum(morali) / len(morali)
        col_media = _colore_soglia(media, 60, 30)
        print()
        print(f"  ❤️  Morale medio: {colored(f'{media:.0f}/100', col_media, attrs=['bold'])}")
        if equipaggio_basso_morale(stato, 30):
            cprint("  🔴 PIÙ DELLA METÀ dell'equipaggio ha morale critico! Rischio rallentamento.", "red", attrs=["bold"])
 
    # ── Merci e risorse baratto (solo se presenti) ─────────────────
    merci_presenti = {}
    for k, v in stato.get('merci', {}).items():
        if v > 0:
            merci_presenti[k] = v
 
    risorse_presenti = {}
    for k, v in stato.get('risorse_baratto', {}).items():
        if v > 0:
            risorse_presenti[k] = v
 
    if merci_presenti or risorse_presenti:
        print()
        cprint("📦 STIVA MERCI", "cyan", attrs=["bold"])
        simboli_merci = {
            "bottiglie_medicinale": "💊", "armi": "⚔️ ", "sale": "🧂",
            "stoffa": "🧵", "coltelli": "🔪", "diamanti": "💎"
        }
        simboli_baratto = {"perle": "🔮", "manufatti": "🗿", "spezie": "🌶️"}
        for merce, qty in merci_presenti.items():
            print(f"  {simboli_merci.get(merce, '📦')} {merce.replace('_', ' ').capitalize()}: {qty}")
        for risorsa, qty in risorse_presenti.items():
            print(f"  {simboli_baratto.get(risorsa, '🔮')} {risorsa.capitalize()}: {qty:.1f}")
 
    # ── Budget e debito stimato ────────────────────────────────────
    print()
    cprint("🪙 FINANZE", "cyan", attrs=["bold"])
    col_budget = _colore_soglia(stato['budget'], 500, 100)
    print(f"  🪙 Budget attuale:      {colored(f\"{stato['budget']:.0f}🪙\", col_budget, attrs=['bold'])}")
 
    debito_stimato = 0
    costo_sett_ruolo = stato.get('costo_sett_ruolo', {})
    sett_percorse = stato.get('settimane_percorse', 0)
    for ruolo, costo_s in costo_sett_ruolo.items():
        debito_stimato += costo_s * (sett_percorse + settimane_rimaste)
    if debito_stimato > 0:
        saldo_stimato = stato['budget'] - debito_stimato
        col_deb = _colore_soglia(saldo_stimato, 500, 0)
        print(f"  ⛓️  Debito stimato fin.:  {colored(f'{debito_stimato:.0f}🪙', 'yellow', attrs=['bold'])}")
        print(f"  📊 Saldo stimato:        {colored(f'{saldo_stimato:.0f}🪙', col_deb, attrs=['bold'])}")
 
    # ── Avvisi speciali ────────────────────────────────────────────
    avvisi = []
    if stato.get('albatro_ucciso', False):
        avvisi.append(("☠️  La maledizione dell'albatro incombe sulla nave.", "red"))
    if stato.get('avvistamenti_albatro', 0) > 0 and not stato.get('albatro_ucciso', False):
        avvisi.append((f"🦅 L'albatro è stato avvistato {stato['avvistamenti_albatro']}/3 volte.", "cyan"))
    if stato['equipaggio'].get('cuochi', 0) == 0:
        avvisi.append(("🍲 Nessun cuoco a bordo! Morale e ammutinamento ne risentono.", "yellow"))
    if stato['equipaggio'].get('medici', 0) == 0:
        avvisi.append(("🩺 Nessun medico! Le epidemie potrebbero essere fatali.", "yellow"))
    if stato['equipaggio'].get('navigatori', 0) == 0:
        avvisi.append(("🧭 Nessun navigatore! Fuga e rotte di emergenza impossibili.", "yellow"))
    if integrita <= 25:
        avvisi.append(("💥 INTEGRITÀ CRITICA! La nave rischia di affondare.", "red"))
    if punti_amm >= 70:
        avvisi.append(("⚠️  AMMUTINAMENTO IMMINENTE! Intervieni subito.", "red"))
 
    if avvisi:
        print()
        cprint("🔔 AVVISI", "cyan", attrs=["bold"])
        for testo_avviso, col_avviso in avvisi:
            cprint(f"  {testo_avviso}", col_avviso, attrs=["bold"])
 
    # ── Chiusura ───────────────────────────────────────────────────
    cprint("\n" + "═" * 60, "yellow", attrs=["bold"])
    leggi_input(colored("📖 [Premi Invio per proseguire il viaggio...] ", "dark_grey"))
    pulisci_schermo()
 
 
# ==========================================
# CICLO DI VIAGGIO
# ==========================================
 
def _ciclo_viaggio(stato, capitano, fase_nome, settimane_base):
    """
    Motore comune per andata e ritorno.
    Restituisce True se sopravvivono, False in caso di game over.
    Traccia le settimane reali percorse per il calcolo stipendi (fix TODO-44/47).
    """
    settimana = 1
    while True:
        settimane_totali = settimane_base + stato.get('settimane_extra', 0) - stato.get('settimane_risparmiate', 0)
        settimane_totali = max(settimane_totali, settimana)
 
        cprint(f"\n📅 --- SETTIMANA {settimana} DI {fase_nome.upper()} (di ~{settimane_totali}) ---", "yellow", attrs=["bold"])
        stampa_risorse(stato)
 
        # TODO-12: se più della metà ha morale ≤ 30, +1 settimana extra
        if equipaggio_basso_morale(stato, 30):
            stampa_lenta("⚠️   Il morale è a pezzi! La navigazione rallenta terribilmente.", "red", attrs=["bold"])
            stato['settimane_extra'] = stato.get('settimane_extra', 0) + 1
            settimane_totali += 1
            cprint(f"📅 Il viaggio si allunga! Ora mancano ancora {settimane_totali - settimana} settimane.", "red")
 
        # Evento ogni 2 settimane
        if settimana % 2 == 0:
            gestisci_evento_casuale(stato)
 
        # ── Step 4: riepilogo fine settimana ──────────────────────
        riepilogo_fine_settimana(stato, settimana, settimane_totali, fase_nome)
 
        esito = consuma_scorte_dettagliate(stato)
        incrementa_settimane(stato)
 
        if esito == "ammutinamento":
            return game_over(
                "I punti ammutinamento hanno raggiunto il massimo. La ciurma si ribella.\n"
                "Ti sgozzano sul ponte mentre l'alba tinge di rosso l'oceano.",
                stato, capitano
            )
        elif esito == "affondato":
            return game_over("La nave non regge più. L'acqua invade la stiva. Naufragate.", stato, capitano)
        elif esito == "scorte_esaurite":
            stampa_lenta("☠️  Le scorte di qualche categoria sono esaurite! L'equipaggio soffre.", "red", attrs=["bold"])
 
        # TODO-14: ammutinamento a soglia punti
        if stato.get('punti_ammutinamento', 0) >= 100:
            return game_over(
                "L'ammutinamento esplode! Anni di torti si riversano in una notte di fuoco e sangue.\n"
                "Il tuo corpo viene gettato in pasto agli squali.",
                stato, capitano
            )
 
        if conta_equipaggio(stato) == 0:
            return game_over("L'ultimo uomo è morto. La nave vaga senza vita verso l'abisso.", stato, capitano)
 
        if settimana >= settimane_totali:
            break
        settimana += 1
 
    return True