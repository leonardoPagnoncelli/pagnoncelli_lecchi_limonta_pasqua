"relazione_indigeni": 40,
"doni_offerti": [],
"cerimonia_completata": False,

# ==========================================
# SISTEMA INDIGENI - NUOVO MONDO
# ==========================================

# Relazione indigeni: 0-100
# 0-20   = Ostili       → attacco immediato
# 21-40  = Diffidenti   → nessun baratto
# 41-60  = Neutrali     → baratto base
# 61-80  = Amichevoli   → baratto favorevole
# 81-100 = Alleati      → baratto + bonus cerimonia

def _inizializza_relazione_indigeni(stato):
    """Imposta la relazione iniziale se non esiste ancora."""
    if 'relazione_indigeni' not in stato:
        stato['relazione_indigeni'] = 40
    if 'doni_offerti' not in stato:
        stato['doni_offerti'] = []
    if 'cerimonia_completata' not in stato:
        stato['cerimonia_completata'] = False

def _varia_relazione(stato, delta, motivo=""):
    """Varia la relazione con gli indigeni con log."""
    stato['relazione_indigeni'] = max(0, min(100, stato['relazione_indigeni'] + delta))
    if motivo:
        segno = "📈" if delta > 0 else "📉"
        col = "green" if delta > 0 else "red"
        variazione_stat(f"{segno} Relazione indigeni {'+' if delta > 0 else ''}{delta} ({motivo})", col)

def _stampa_stato_relazione(stato):
    """Mostra la relazione attuale con gli indigeni."""
    r = stato['relazione_indigeni']
    if r <= 20:
        etichetta = colored("💀 OSTILI", "red", attrs=["bold"])
    elif r <= 40:
        etichetta = colored("😠 DIFFIDENTI", "yellow", attrs=["bold"])
    elif r <= 60:
        etichetta = colored("😐 NEUTRALI", "white", attrs=["bold"])
    elif r <= 80:
        etichetta = colored("🤝 AMICHEVOLI", "green", attrs=["bold"])
    else:
        etichetta = colored("✨ ALLEATI", "cyan", attrs=["bold"])
    cprint(f"  🌿 Relazione con gli indigeni: {r}/100 — {etichetta}", "white")

def fase_primo_contatto(stato, capitano):
    """
    Primo contatto con gli indigeni sulla spiaggia.
    La reazione iniziale dipende dall'albatro e dalla composizione dell'equipaggio.
    Restituisce False solo in caso di game over immediato.
    """
    pulisci_schermo()
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])
    stampa_lenta(" TERRA IN VISTA! Il Nuovo Mondo emerge tra la nebbia mattutina.", "green", ["bold"])
    cprint("🌴" + "="*58 + "🌴", "green", attrs=["bold"])

    _inizializza_relazione_indigeni(stato)

    stampa_lenta("\nLa barca tocca la spiaggia. Il caldo è denso, l'aria profuma di spezie selvatiche.", "yellow")
    stampa_lenta("Poi... centinaia di guerrieri emergono dalla foresta, dipinti di ocra rossa.", "red", attrs=["bold"])
    stampa_lenta("I tamburi battono un ritmo lento e minaccioso.", "red")
    time.sleep(1)

    # Modificatori relazione iniziale
    if stato.get('albatro_ucciso', False):
        stampa_lenta("⚠️  Gli sciamani agitano le lance — come se sentissero la colpa dell'albatro su di voi!", "red", attrs=["bold"])
        _varia_relazione(stato, -20, "maledizione dell'albatro percepita dagli sciamani")

    if stato['equipaggio'].get('navigatori', 0) > 0:
        stampa_lenta("🧭 Il navigatore riconosce alcuni gesti rituali e li imita. I guerrieri si fermano.", "green")
        _varia_relazione(stato, +10, "navigatore esperto di culture straniere")

    if stato['equipaggio'].get('medici', 0) > 0:
        stampa_lenta("🩺 Il medico estrae un kit di bende e lo mostra a mani aperte. Gesto di pace riconosciuto.", "green")
        _varia_relazione(stato, +5, "gesto di cura riconosciuto")

    # Scelta iniziale del capitano
    print()
    _stampa_stato_relazione(stato)
    print()
    stampa_lenta("Il capo tribù avanza di tre passi. Silenzio totale.", "cyan", attrs=["bold"])

    scelta = chiedi_scelta(
        colored("\n👉 [F] FAI FUOCO subito | [A] Avanza disarmato | [A] Aspetta e osserva: ", "magenta", attrs=["bold"]),
        ['F', 'A', 'O']
    )

    if scelta == 'F':
        stampa_lenta("💥 'FUOCO A VOLONTÀ!'", "red", attrs=["bold", "blink"])
        stampa_lenta("Un attimo di silenzio... poi migliaia di frecce avvelenate oscurano il sole.", "red")
        stampa_lenta("Siete sopraffatti in secondi. Nessun sopravvissuto.", "red", attrs=["bold"])
        return game_over("Avete provocato un massacro. Il Nuovo Mondo vi inghiotte.", stato, capitano)

    elif scelta == 'A':
        stampa_lenta("🤝 Avanzate lentamente, mani aperte, armi a terra.", "cyan")
        tiro = random.randint(1, 10)
        if tiro >= 5:
            stampa_lenta("Il capo tribù abbassa la lancia. Un segno di rispetto.", "green", attrs=["bold"])
            _varia_relazione(stato, +15, "avanzata pacifica rispettata")
        else:
            stampa_lenta("Un guerriero giovane scaglia una lancia di avvertimento. Cade ai vostri piedi.", "yellow")
            stampa_lenta("Non è un attacco — è un test.", "yellow")
            _varia_relazione(stato, +5, "test di coraggio superato")

    elif scelta == 'O':
        stampa_lenta("🔭 Vi fermate. Osservate i rituali, i gesti, le posture.", "cyan")
        stampa_lenta("Il medico e il navigatore bisbigliando interpretano i simboli dipinti sui corpi.", "cyan")
        tiro = random.randint(1, 10) + stato['equipaggio'].get('navigatori', 0)
        if tiro >= 7:
            stampa_lenta("✨ Capite: mostrano un simbolo di benvenuto condizionato. Portate doni.", "green", attrs=["bold"])
            _varia_relazione(stato, +10, "comprensione dei rituali indigeni")
        else:
            stampa_lenta("Non riuscite a decifrare nulla. I tamburi accelerano.", "yellow")
            _varia_relazione(stato, -5, "attesa interpretata come paura")

    time.sleep(1)
    return True

def fase_doni_iniziali(stato, capitano):
    """
    Offerta di doni prima del baratto.
    Ogni merce offerta come dono non genera risorse baratto ma aumenta la relazione.
    """
    pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🎁 --- OFFERTA DEI DONI INIZIALI ---", "green", attrs=["bold"])
    stampa_lenta("Prima di trattare, il protocollo tribale impone doni al capo.", "cyan")
    stampa_lenta("I doni non tornano indietro — ma la fiducia che generano vale oro.", "yellow")
    print()
    _stampa_stato_relazione(stato)
    print()

    catalogo_doni = {
        "sale":     ("🧂 Sale",    10, "bene raro — gli indigeni lo venerano"),
        "stoffa":   ("🧵 Stoffa",  15, "tessuti colorati — li affascinano"),
        "coltelli": ("🔪 Coltelli", 20, "strumenti utili — li rispettano"),
        "diamanti": ("💎 Diamanti", 5,  "pietre lucenti — li incantano"),
    }

    doni_disponibili = {}
    for k, v in stato['merci'].items():
        if k in catalogo_doni and v > 0:
            doni_disponibili[k] = v

    if not doni_disponibili:
        stampa_lenta("❌ Non hai merci da offrire come dono. Gli indigeni lo notano.", "red")
        _varia_relazione(stato, -10, "nessun dono offerto")
        time.sleep(1.5)
        return

    # Mostra opzioni
    lista_doni = list(doni_disponibili.keys())
    for i, merce in enumerate(lista_doni, 1):
        nome, bonus_rel, descrizione = catalogo_doni[merce]
        print(f"  {i}. {nome:<18} (hai {doni_disponibili[merce]})  +{bonus_rel} relazione  — {descrizione}")
    print(f"  0. Non offrire nulla")
    print()

    scelta = chiedi_scelta(
        colored(f"👉 Cosa offri come dono? (0-{len(lista_doni)}): ", "magenta", attrs=["bold"]),
        ['0'] + [str(i) for i in range(1, len(lista_doni) + 1)]
    )

    if scelta == '0':
        stampa_lenta("😐 Non offri nulla. Il capo tribù stringe le labbra.", "yellow")
        _varia_relazione(stato, -10, "dono rifiutato — mancanza di rispetto")
        return

    idx = int(scelta) - 1
    merce_scelta = lista_doni[idx]
    nome_dono, bonus_rel, _ = catalogo_doni[merce_scelta]

    # Quante unità offrire
    massimo = doni_disponibili[merce_scelta]
    while True:
        try:
            qty_str = leggi_input(colored(f"  Quante unità di {nome_dono} vuoi offrire? (1-{massimo}): ", "yellow"))
            qty = int(qty_str) if qty_str.strip() else 1
            if qty < 1 or qty > massimo:
                cprint(f"  ❌ Quantità non valida (1-{massimo})", "red")
                continue
            break
        except ValueError:
            cprint("  ❌ Numero non valido.", "red")

    stato['merci'][merce_scelta] -= qty
    stato['doni_offerti'].append(merce_scelta)

    # Bonus relazione scalato per quantità (ma con diminishing returns)
    if qty == 1:
        bonus_finale = bonus_rel
    elif qty <= 3:
        bonus_finale = bonus_rel + 5
    else:
        bonus_finale = bonus_rel + 10

    _varia_relazione(stato, bonus_finale, f"dono di {qty}x {merce_scelta}")

    stampa_lenta(f"🎁 Offri {qty} {nome_dono}. Il capo tribù li prende solennemente.", "green", attrs=["bold"])

    # Reazione speciale se la relazione supera certe soglie dopo il dono
    r = stato['relazione_indigeni']
    if r >= 80:
        stampa_lenta("✨ Il capo tribù sorride e ordina ai guerrieri di abbassare le armi completamente.", "cyan", attrs=["bold"])
        stampa_lenta("Una donna anziana — la sciamana — si avvicina e vi pone una collana di conchiglie.", "cyan")
        varia_morale_tutti(stato, +10, "accoglienza tribale calorosa")
    elif r >= 60:
        stampa_lenta("🤝 Il capo tribù annuisce con rispetto. I tamburi cambiano ritmo — più lento, pacifico.", "green")
        varia_morale_tutti(stato, +5, "rispetto guadagnato dagli indigeni")
    elif r >= 40:
        stampa_lenta("😐 Il dono viene accettato senza espressione. Un inizio.", "yellow")

    time.sleep(1.5)

def fase_esplorazione_villaggio(stato, capitano):
    """
    Esplorazione del villaggio indigeno.
    Disponibile solo se relazione >= 60.
    Può trovare: piante medicinali, acqua, cibo, o provocare incidenti.
    """
    if stato['relazione_indigeni'] < 60:
        stampa_lenta("🚫 Gli indigeni non vi permettono di entrare nel villaggio. Troppa diffidenza.", "red")
        return

    pulisci_schermo()
    cprint("="*60, "cyan", attrs=["bold"])
    cprint("🏘️  --- ESPLORAZIONE DEL VILLAGGIO ---", "cyan", attrs=["bold"])
    stampa_lenta("Un guerriero vi scorta all'interno del villaggio tra sguardi curiosi.", "cyan")
    print()
    _stampa_stato_relazione(stato)
    print()

    # Quante zone esplorare (max 3)
    zone = [
        ("🌿 Giardino delle erbe", _esplora_giardino_erbe),
        ("💧 Sorgente sacra",      _esplora_sorgente),
        ("🍖 Cucine tribali",      _esplora_cucine),
        ("🗿 Tempio degli antenati", _esplora_tempio),
    ]

    random.shuffle(zone)
    zone_disponibili = zone[:3]

    for i, (nome_zona, _) in enumerate(zone_disponibili, 1):
        print(f"  {i}. {nome_zona}")
    print(f"  0. Torna alla nave")
    print()

    scelta = chiedi_scelta(
        colored(f"👉 Dove esplori? (0-{len(zone_disponibili)}): ", "magenta", attrs=["bold"]),
        ['0'] + [str(i) for i in range(1, len(zone_disponibili) + 1)]
    )

    if scelta == '0':
        stampa_lenta("Tornate alla nave. I guerrieri vi salutano con un cenno.", "cyan")
        return

    idx = int(scelta) - 1
    nome_zona, funzione_zona = zone_disponibili[idx]
    cprint(f"\n🔍 Esplori: {nome_zona}", "yellow", attrs=["bold"])
    funzione_zona(stato)

    time.sleep(1.5)

def _esplora_giardino_erbe(stato):
    """Trova piante medicinali nel giardino tribale."""
    stampa_lenta("🌿 Piante di ogni tipo crescono ordinate in filari. La sciamana vi mostra le proprietà.", "green")
    tiro = random.randint(1, 10)
    if tiro >= 5:
        medicine_trovate = random.randint(1, 3)
        stato['merci']['bottiglie_medicinale'] = stato['merci'].get('bottiglie_medicinale', 0) + medicine_trovate
        variazione_stat(f"📈 +{medicine_trovate} 💊 Bottiglie medicinale (erbe indigene)", "green")
        _varia_relazione(stato, +5, "condivisione della conoscenza medica")
    else:
        stampa_lenta("⚠️  Un guerriero vi blocca bruscamente. Avete toccato una pianta sacra.", "yellow")
        _varia_relazione(stato, -10, "violazione del giardino sacro")
        varia_morale_tutti(stato, -5, "incidente diplomatico")

def _esplora_sorgente(stato):
    """Riempie le scorte d'acqua alla sorgente sacra."""
    stampa_lenta("💧 L'acqua è cristallina e fredda. Degli indigeni vi invitano a bere.", "cyan")
    acqua_raccolta = random.uniform(15, 30)
    stato['scorte']['acqua'] += acqua_raccolta
    variazione_stat(f"📈 +{acqua_raccolta:.1f} 💧 Acqua (sorgente sacra)", "green")
    varia_morale_tutti(stato, +8, "acqua fresca e abbondante")
    _varia_relazione(stato, +5, "condivisione della sorgente")

def _esplora_cucine(stato):
    """Trova cibo nelle cucine tribali."""
    stampa_lenta("🍖 Enormi pentole bollono su fuochi vivi. Vi offrono cibo con gesti amichevoli.", "green")
    tiro = random.randint(1, 10)
    if tiro >= 4:
        carne_trovata = random.uniform(10, 25)
        frutta_trovata = random.uniform(8, 15)
        stato['scorte']['carne'] += carne_trovata
        stato['scorte']['frutta'] += frutta_trovata
        variazione_stat(f"📈 +{carne_trovata:.1f} 🥩 Carne | +{frutta_trovata:.1f} 🍊 Frutta (ospitalità tribale)", "green")
        varia_morale_tutti(stato, +10, "banchetto tribale")
        _varia_relazione(stato, +8, "banchetto condiviso — legame rafforzato")
    else:
        stampa_lenta("😐 Un membro dell'equipaggio tocca il cibo prima che venisse offerto. Silenzio gelo.", "yellow")
        _varia_relazione(stato, -8, "mancanza di rispetto a tavola")

def _esplora_tempio(stato):
    """Evento rischioso al tempio degli antenati."""
    stampa_lenta("🗿 Statue enormi di antenati vi fissano dall'alto. La sciamana accompagna in silenzio.", "cyan")
    stampa_lenta("Al centro del tempio: una cesta di perle offerte agli dei.", "yellow")

    scelta = chiedi_scelta(
        colored("👉 [O] Osserva rispettoso | [P] Prendi qualche perla di nascosto: ", "magenta", attrs=["bold"]),
        ['O', 'P']
    )

    if scelta == 'O':
        stampa_lenta("🙏 Vi inginocchiate in segno di rispetto. La sciamana annuisce soddisfatta.", "green")
        _varia_relazione(stato, +15, "rispetto per il tempio sacro")
        varia_morale_tutti(stato, +5, "momento di pace spirituale")
    else:
        tiro = random.randint(1, 10)
        if tiro <= 4:
            stampa_lenta("🚨 La sciamana urla! Siete stati visti!", "red", attrs=["bold"])
            perle_confiscate = random.randint(2, 8)
            stato['risorse_baratto']['perle'] = max(0, stato['risorse_baratto'].get('perle', 0) - perle_confiscate)
            _varia_relazione(stato, -30, "furto nel tempio sacro")
            aggiungi_punti_ammutinamento(stato, 15, "scandalo nel tempio")
            varia_morale_tutti(stato, -15, "vergogna del furto scoperto")
            variazione_stat(f"📉 -{perle_confiscate} 🔮 Perle confiscate", "red")
        else:
            perle_rubate = random.randint(3, 10)
            stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + perle_rubate
            stampa_lenta(f"🥷 Nessuno ha visto. Tasca più pesante di {perle_rubate} perle.", "green")
            variazione_stat(f"📈 +{perle_rubate} 🔮 Perle rubate al tempio", "green")

def fase_cerimonia_tribale(stato, capitano):
    """
    Cerimonia tribale disponibile solo se relazione >= 70.
    Può sbloccare bonus permanenti per il viaggio di ritorno.
    """
    if stato['relazione_indigeni'] < 70:
        return
    if stato.get('cerimonia_completata', False):
        return

    pulisci_schermo()
    cprint("="*60, "yellow", attrs=["bold"])
    cprint("🔥 --- CERIMONIA TRIBALE ---", "yellow", attrs=["bold"])
    stampa_lenta("Il capo tribù vi invita a una cerimonia sacra al tramonto.", "cyan")
    stampa_lenta("Fuochi enormi, danze, tamburi. Siete ospiti d'onore.", "yellow", attrs=["bold"])
    print()
    _stampa_stato_relazione(stato)
    print()

    scelta = chiedi_scelta(
        colored("👉 [P] Partecipa pienamente | [G] Guarda da lontano | [R] Rifiuta: ", "magenta", attrs=["bold"]),
        ['P', 'G', 'R']
    )

    if scelta == 'R':
        stampa_lenta("😔 Il capo tribù abbassa lo sguardo. Un insulto non dimenticato.", "red")
        _varia_relazione(stato, -25, "cerimonia rifiutata — grave offesa")
        return

    elif scelta == 'G':
        stampa_lenta("🔥 Osservate da lontano. Gli indigeni lo notano ma non protestano.", "yellow")
        _varia_relazione(stato, +5, "presenza rispettosa alla cerimonia")
        varia_morale_tutti(stato, +5, "spettacolo tribale magnifico")

    elif scelta == 'P':
        stampa_lenta("💃 Vi unite alle danze goffamente. Le risate sono genuine e calde.", "green", attrs=["bold"])
        stampa_lenta("La sciamana vi dipinge il viso con ocra rossa — siete fratelli di sangue.", "cyan", attrs=["bold"])
        _varia_relazione(stato, +20, "integrazione nella cerimonia tribale")
        varia_morale_tutti(stato, +15, "fratellanza con gli indigeni")

        # Bonus speciale: la sciamana rivela una rotta più sicura
        if stato['equipaggio'].get('navigatori', 0) > 0:
            stampa_lenta("🧭 Il navigatore e la sciamana comunicano con gesti e disegni sulla sabbia.", "green")
            stampa_lenta("✨ Una rotta di ritorno più sicura! -1 settimana extra di viaggio.", "yellow", attrs=["bold"])
            stato['settimane_risparmiate'] = stato.get('settimane_risparmiate', 0) + 1
            variazione_stat("📈 -1 settimana (rotta della sciamana)", "green")

        # Bonus scorte extra
        n = conta_equipaggio(stato)
        for cat, consumo in CONSUMI_SETTIMANALI_PER_MEMBRO.items():
            stato['scorte'][cat] += consumo * n * 1
        variazione_stat("📈 +1 settimana di scorte (dono della cerimonia)", "green")

    stato['cerimonia_completata'] = True
    time.sleep(1.5)

def fase_baratto_indigeni(stato, capitano):
    """
    Baratto con gli indigeni.
    I tassi di cambio dipendono dalla relazione:
    - Neutrali (40-60): tassi base
    - Amichevoli (61-80): tassi +25%
    - Alleati (81-100): tassi +50%
    """
    pulisci_schermo()
    cprint("="*60, "green", attrs=["bold"])
    cprint("🤝 --- GRANDE BARATTO NEL NUOVO MONDO ---", "green", attrs=["bold"])
    stampa_lenta("Il capo tribù siede sul trono di conchiglie. È tempo di trattare.", "cyan")
    print()
    _stampa_stato_relazione(stato)
    print()

    r = stato['relazione_indigeni']
    if r <= 40:
        stampa_lenta("😠 Gli indigeni sono troppo diffidenti per trattare. Migliora la relazione prima.", "red", attrs=["bold"])
        time.sleep(2)
        return True

    # Fattore moltiplicatore tassi in base alla relazione
    if r >= 81:
        moltiplicatore = 1.5
        cprint("✨ Siete ALLEATI — tassi di baratto eccellenti (+50%)!", "cyan", attrs=["bold"])
    elif r >= 61:
        moltiplicatore = 1.25
        cprint("🤝 Siete AMICHEVOLI — tassi di baratto favorevoli (+25%)!", "green", attrs=["bold"])
    else:
        moltiplicatore = 1.0
        cprint("😐 Siete NEUTRALI — tassi di baratto standard.", "white")

    print()

    # Tabelle baratto base (i valori vengono poi moltiplicati)
    tabelle_baratto = {
        "sale": [
            ("perle",     3.0, "🔮"),
            ("manufatti", 2.0, "🗿"),
            ("spezie",    1.5, "🌶️"),
        ],
        "stoffa": [
            ("perle",     5.0, "🔮"),
            ("manufatti", 4.0, "🗿"),
            ("spezie",    3.0, "🌶️"),
        ],
        "coltelli": [
            ("perle",     4.0, "🔮"),
            ("manufatti", 3.0, "🗿"),
            ("spezie",    2.0, "🌶️"),
        ],
        "diamanti": [
            ("perle",     20.0, "🔮"),
            ("manufatti", 15.0, "🗿"),
            ("spezie",    10.0, "🌶️"),
        ],
    }

    merci_barattabili = {}
    for k, v in stato['merci'].items():
        if k in tabelle_baratto and v > 0:
            merci_barattabili[k] = v

    if not merci_barattabili:
        stampa_lenta("❌ Non hai merci barattabili! Il capo tribù ti congeda deluso.", "red", attrs=["bold"])
        _varia_relazione(stato, -5, "nessuna merce da barattare")
        return True

    stato.setdefault('barattato', {"sale": 0, "stoffa": 0, "coltelli": 0, "diamanti": 0})

    for merce, quantita in merci_barattabili.items():
        if quantita <= 0:
            continue
        pulisci_schermo()
        cprint(f"🔄 Baratto: {merce.upper()} (hai {quantita} unità)", "yellow", attrs=["bold"])
        _stampa_stato_relazione(stato)
        print()

        offerte = tabelle_baratto[merce]
        for i, (cosa, tasso_base, simbolo) in enumerate(offerte, 1):
            tasso_reale = tasso_base * moltiplicatore
            guadagno_stimato = quantita * tasso_reale
            print(f"  {i}. {simbolo} {cosa.capitalize():<12} → {tasso_reale:.1f} {simbolo}/unità  (max: {guadagno_stimato:.1f} {simbolo})")
        print(f"  0. Salta (non barattare {merce})")
        print()

        scelta_offerta = chiedi_scelta(
            colored(f"👉 Quale offerta scegli? (0-{len(offerte)}): ", "magenta", attrs=["bold"]),
            ['0'] + [str(i) for i in range(1, len(offerte) + 1)]
        )

        if scelta_offerta == '0':
            continue

        idx = int(scelta_offerta) - 1
        cosa, tasso_base, simbolo = offerte[idx]
        tasso_reale = tasso_base * moltiplicatore

        while True:
            try:
                qty_str = leggi_input(colored(f"  Quante unità di {merce} vuoi barattare? (max {quantita}): ", "yellow"))
                qty = int(qty_str) if qty_str.strip() else 0
                if qty < 0 or qty > quantita:
                    cprint(f"  ❌ Quantità non valida (0-{int(quantita)})", "red")
                    continue
                break
            except ValueError:
                cprint("  ❌ Numero non valido.", "red")

        if qty > 0:
            guadagno = qty * tasso_reale
            stato['merci'][merce] -= qty
            stato['barattato'][merce] = stato['barattato'].get(merce, 0) + qty
            stato['risorse_baratto'][cosa] = stato['risorse_baratto'].get(cosa, 0) + guadagno
            cprint(f"  ✅ Barattato {qty}x {merce} → +{guadagno:.1f} {simbolo} {cosa}", "green", attrs=["bold"])
            time.sleep(0.8)

    # Riepilogo baratto
    print()
    cprint("📊 RIEPILOGO BARATTO:", "cyan", attrs=["bold"])
    for risorsa, qty in stato['risorse_baratto'].items():
        if qty > 0:
            simboli_r = {"perle": "🔮", "manufatti": "🗿", "spezie": "🌶️"}
            print(f"  {simboli_r.get(risorsa, '')} {risorsa.capitalize()}: {qty:.1f}")

    time.sleep(2)
    return True

def evento_tradimento_indigeni(stato):
    """
    Un guerriero rivale offre oro per armi.
    La probabilità di essere scoperti peggiora con albatro ucciso
    e migliora con relazione alta (più facile smascherare l'infiltrato).
    """
    if stato['merci'].get('armi', 0) <= 0:
        return

    stampa_lenta("\n🌑 Un guerriero solitario si avvicina di notte al campo.", "yellow")
    stampa_lenta("Sussurra: 'Il rivale del capo... offre 30 perle per ogni arma. In segreto.'", "red")

    scelta = chiedi_scelta(
        colored("👉 [A] Accetta il tradimento | [R] Rifiuta: ", "magenta", attrs=["bold"]),
        ['A', 'R']
    )

    if scelta == 'A':
        # Calcolo probabilità scoperta
        prob_base = 0.50
        if stato.get('albatro_ucciso', False):
            prob_base += 0.25
            stampa_lenta("☠️  La maledizione dell'albatro porta sfortuna...", "red")
        if stato['relazione_indigeni'] >= 70:
            # Alta relazione → il capo tribù è vigile e fidato
            prob_base += 0.15
            stampa_lenta("⚠️  Il vostro legame con il capo tribù lo rende molto attento ai traditori.", "yellow")

        if random.random() < prob_base:
            stampa_lenta("🚨 SIETE SCOPERTI! Il capo tribù urla vendetta!", "red", attrs=["bold"])
            armi_confiscate = stato['merci']['armi']
            stato['merci']['armi'] = 0
            _varia_relazione(stato, -40, "tradimento scoperto — relazione distrutta")
            ruoli_vivi = []
            for r in stato['equipaggio']:
                if stato['equipaggio'][r] > 0:
                    ruoli_vivi.append(r)
            for _ in range(min(3, conta_equipaggio(stato))):
                if ruoli_vivi:
                    ruolo = random.choice(ruoli_vivi)
                    rimuovi_membro(stato, ruolo)
                    ruoli_vivi = []
                    for r in stato['equipaggio']:
                        if stato['equipaggio'][r] > 0:
                            ruoli_vivi.append(r)
            varia_morale_tutti(stato, -30, "tradimento scoperto")
            aggiungi_punti_ammutinamento(stato, 40, "disonore del tradimento")
            variazione_stat(f"📉 -{armi_confiscate} armi confiscate", "red")
        else:
            armi_vendute = min(stato['merci']['armi'], 3)
            stato['merci']['armi'] -= armi_vendute
            guadagno = armi_vendute * 30
            stato['risorse_baratto']['perle'] = stato['risorse_baratto'].get('perle', 0) + guadagno
            stampa_lenta(f"💰 Il tradimento riesce! +{guadagno} 🔮 perle (vendute {armi_vendute} armi).", "green", attrs=["bold"])
    else:
        stampa_lenta("🤝 Rifiuti. Il guerriero scompare nell'oscurità.", "cyan")
        varia_morale_tutti(stato, +5, "onestà premiata")
        _varia_relazione(stato, +5, "rifiuto del tradimento — integrità rispettata")

def arrivo_nuovo_mondo(stato, capitano):
    """
    Orchestratore dell'intera sequenza nel Nuovo Mondo.
    Chiama in ordine: primo contatto → doni → esplorazione → cerimonia → baratto → tradimento.
    """
    _inizializza_relazione_indigeni(stato)

    # 1. Primo contatto
    risultato = fase_primo_contatto(stato, capitano)
    if risultato is False:
        return False

    # Controllo: se ostili dopo il primo contatto, attacco immediato
    if stato['relazione_indigeni'] <= 20:
        stampa_lenta("💀 Gli indigeni caricano! Non c'è via di scampo. L'accampamento viene raso al suolo.", "red", attrs=["bold"])
        ruoli_vivi = []
        for r in stato['equipaggio']:
            if stato['equipaggio'][r] > 0:
                ruoli_vivi.append(r)
        for _ in range(min(4, conta_equipaggio(stato))):
            if ruoli_vivi:
                ruolo = random.choice(ruoli_vivi)
                rimuovi_membro(stato, ruolo)
                ruoli_vivi = []
                for r in stato['equipaggio']:
                    if stato['equipaggio'][r] > 0:
                        ruoli_vivi.append(r)
        varia_morale_tutti(stato, -30, "attacco indigeno")
        aggiungi_punti_ammutinamento(stato, 25, "attacco subito — equipaggio terrorizzato")
        stampa_lenta("⚠️  Fuggite a stento verso la nave. Niente baratto.", "yellow", attrs=["bold"])
        time.sleep(2)
        return True

    # 2. Doni iniziali
    leggi_input(colored("\n📖 [Premi Invio per procedere con i doni...] ", "dark_grey"))
    fase_doni_iniziali(stato, capitano)

    # 3. Esplorazione villaggio (opzionale)
    if stato['relazione_indigeni'] >= 60:
        print()
        cprint("🏘️  Gli indigeni vi invitano a esplorare il villaggio.", "cyan", attrs=["bold"])
        scelta_esplora = chiedi_scelta(
            colored("👉 [S] Esplora il villaggio | [N] Vai direttamente al baratto: ", "magenta", attrs=["bold"]),
            ['S', 'N']
        )
        if scelta_esplora == 'S':
            fase_esplorazione_villaggio(stato, capitano)

    # 4. Cerimonia tribale (se relazione >= 70)
    if stato['relazione_indigeni'] >= 70 and not stato.get('cerimonia_completata', False):
        print()
        cprint("🔥 Il capo tribù vi invita alla cerimonia del tramonto.", "yellow", attrs=["bold"])
        scelta_cerimonia = chiedi_scelta(
            colored("👉 [S] Partecipa alla cerimonia | [N] Salta: ", "magenta", attrs=["bold"]),
            ['S', 'N']
        )
        if scelta_cerimonia == 'S':
            fase_cerimonia_tribale(stato, capitano)

    # 5. Baratto
    leggi_input(colored("\n📖 [Premi Invio per il baratto...] ", "dark_grey"))
    fase_baratto_indigeni(stato, capitano)

    # 6. Evento tradimento (solo se ci sono armi)
    if stato['merci'].get('armi', 0) > 0:
        evento_tradimento_indigeni(stato)

    return True