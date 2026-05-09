# ==========================================
# EVENTO: IL TRADIMENTO
# ==========================================

TRADITORI = [
    ("Rodrigo il Losco",    "nostromo",      "un coltello"),
    ("Marta dalle Due Facce", "cuoca di bordo", "il veleno nella minestra"),
    ("Bastian Occhio Torto", "cannoniere",    "una miccia spenta di nascosto"),
    ("Ines la Sibilante",   "navigatrice",   "le carte nautiche falsificate"),
]

MOTIVAZIONI = [
    "vuole intascarsi il tesoro da solo",
    "è al soldo del governatore nemico",
    "non ha dimenticato il torto di Puerto Arco",
    "è stato corrotto dalla ciurma rivale dei Serpenti del Mare",
]

def _dado(facce=6):
    return random.randint(1, facce)

def _pausa():
    time.sleep(0.6)

def _stampa_separatore(colore="yellow"):
    cprint("\n" + "~" * 60, colore)

def _controlla_equipaggio(stato, capitano, soglia=3):
    """Verifica se l'equipaggio è troppo ridotto per sopravvivere."""
    if stato.get("equipaggio", 10) <= soglia:
        return game_over(
            f"Senza abbastanza uomini fedeli, il galeone non regge.\n"
            f"La ciurma ammutinatasi ti getta in mare aperto.",
            stato, capitano
        )
    return True

def _stampa_intestazione_evento():
    pulisci_schermo()
    _stampa_separatore("red")
    cprint(" ⚔️  --- UN VENTO DI TRADIMENTO --- ⚔️ ", "red", attrs=["bold"])
    _stampa_separatore("red")
    print()

def _fase_scoperta(capitano, traditore, ruolo, arma, motivazione):
    """Narrativa iniziale della scoperta del tradimento."""
    stampa_lenta(
        f"Una notte senza luna. Il tuo istinto di navigatore, {capitano},\n"
        f"ti sveglia di soprassalto nel cuore delle acque nere.",
        "white", ritardo=0.025
    )
    _pausa()
    stampa_lenta(
        f"Attraverso i listoni del ponte senti mormorare:\n"
        f"è {traditore}, il tuo {ruolo}. {traditore} che {motivazione}.",
        "yellow", ritardo=0.025
    )
    _pausa()
    stampa_lenta(
        f"Hai visto {arma} passare di mano in mano tra le ombre.",
        "red", attrs=["bold"], ritardo=0.03
    )
    print()

def _fase_scelta_iniziale():
    """Prima biforcazione: come reagisce il capitano alla scoperta."""
    cprint("Come agisci?", "cyan", attrs=["bold"])
    print()
    cprint("  [A] Affrontare il traditore a viso aperto sul ponte",    "white")
    cprint("  [B] Appostarti e spiarne i piani fino all'alba",          "white")
    cprint("  [C] Abbandonare il ponte e sparire nel buio della stiva", "white")
    print()
    return chiedi_scelta(
        colored("👉 La tua scelta (A/B/C): ", "cyan"),
        ["A", "B", "C"]
    )

# ------------------------------------------
# RAMO A — Confronto diretto
# ------------------------------------------

def _ramo_affronta(stato, capitano, traditore, ruolo, arma):
    """Il capitano sfida il traditore davanti all'equipaggio."""
    stampa_lenta(
        f"Scendi sul ponte a passo pesante.\n"
        f"«{traditore}!» — la tua voce taglia il buio come una sciabola.",
        "white", ritardo=0.025
    )
    _pausa()
    stampa_lenta(
        f"{traditore} si gira di scatto. {arma.capitalize()} lucica nella notte.\n"
        f"La ciurma si sveglia e forma un cerchio intorno a voi.",
        "yellow", ritardo=0.025
    )
    print()

    cprint("L'equipaggio vi osserva in silenzio. Decidi:", "cyan", attrs=["bold"])
    print()
    cprint("  [A] Sfidarlo a duello davanti a tutti",     "white")
    cprint("  [B] Offrirgli la grazia se confessa tutto", "white")
    print()
    scelta = chiedi_scelta(
        colored("👉 La tua scelta (A/B): ", "cyan"),
        ["A", "B"]
    )

    if scelta == "A":
        return _duello(stato, capitano, traditore, ruolo)
    else:
        return _perdona(stato, capitano, traditore, ruolo)

def _duello(stato, capitano, traditore, ruolo):
    """Duello a dado contro il traditore."""
    stampa_lenta(
        f"Le sciabole cantano. La ciurma trattiene il fiato.\n"
        f"Il tuo valore contro la disperazione di {traditore}.",
        "white", ritardo=0.025
    )
    _pausa()

    tiro_capitano  = _dado(20) + stato.get("fortuna", 0)
    tiro_traditore = _dado(20)

    cprint(f"\n  🎲 Tiro del Capitano:  {tiro_capitano}", "cyan")
    time.sleep(0.4)
    cprint(f"  🎲 Tiro del Traditore: {tiro_traditore}", "red")
    time.sleep(0.5)

    if tiro_capitano > tiro_traditore:
        stampa_lenta(
            f"\n{traditore} cade in ginocchio, disarmato.\n"
            f"«Getta{traditore.split()[0]} in mare!» urla la ciurma leale.",
            "green", ritardo=0.025
        )
        variazione_stat("▼ Equipaggio  -1  (il traditore è eliminato)",      "red")
        variazione_stat("▲ Morale ciurma +15  (il capitano ha vinto!)",       "green")
        variazione_stat("▲ Reputazione   +10  (nessuno osa più dubitare)",    "yellow")
        stato["equipaggio"]  = stato.get("equipaggio",  10) - 1
        stato["morale"]      = stato.get("morale",       0) + 15
        stato["reputazione"] = stato.get("reputazione",  0) + 10
        _pausa()
        stampa_lenta(
            "L'alba sorge. La rotta è tua, il galeone è tuo.",
            "green", attrs=["bold"], ritardo=0.03
        )
        return True

    elif tiro_capitano == tiro_traditore:
        stampa_lenta(
            f"\nLe lame si bloccano. Nessuno cede.\n"
            f"Un vecchio marinaio separa i duellanti: «Basta sangue per stanotte.»",
            "yellow", ritardo=0.025
        )
        variazione_stat("▼ Salute capitano -10  (ferita al fianco)",         "red")
        variazione_stat("▼ Morale ciurma   -5   (l'esito è incerto)",        "red")
        stato["salute"] = stato.get("salute", 100) - 10
        stato["morale"] = stato.get("morale",   0) -  5
        stampa_lenta(
            f"{traditore} viene messo in isolamento. La tensione non scompare.",
            "yellow", ritardo=0.025
        )
        return True

    else:
        stampa_lenta(
            f"\n{traditore} ti disarma con uno sgambetto basso.\n"
            f"Il traditore urla alla ciurma: «Il vecchio capitano è finito!»",
            "red", ritardo=0.025
        )
        variazione_stat("▼ Salute capitano -25  (colpo alla testa)", "red")
        stato["salute"] = stato.get("salute", 100) - 25
        if stato["salute"] <= 0:
            return game_over(
                f"Cadi sul ponte del tuo stesso galeone.\n"
                f"{traditore} issò la propria bandiera sull'albero maestro.",
                stato, capitano
            )
        stampa_lenta(
            "Riesci a strisciare fino alla stiva. Sopravvivi, per ora.",
            "red", ritardo=0.025
        )
        variazione_stat("▼ Reputazione -20  (sconfitto sotto gli occhi di tutti)", "red")
        stato["reputazione"] = stato.get("reputazione", 0) - 20
        return True

def _perdona(stato, capitano, traditore, ruolo):
    """Il capitano offre grazia in cambio di una confessione pubblica."""
    stampa_lenta(
        f"«Confessa davanti alla ciurma e avrai salva la vita,\n"
        f"traditore. Una sola parola falsa e finisci in mare.»",
        "white", ritardo=0.025
    )
    _pausa()

    fedeli = stato.get("equipaggio", 10)
    if fedeli >= 8:
        stampa_lenta(
            f"{traditore} guarda gli occhi duri della ciurma e crolla.\n"
            f"Confessa i nomi dei complici: tre uomini vengono sbarcati al prossimo porto.",
            "green", ritardo=0.025
        )
        variazione_stat("▼ Equipaggio  -3   (i complici abbandonano la nave)", "red")
        variazione_stat("▲ Morale      +8   (la lealtà premia)",               "green")
        variazione_stat("▲ Reputazione +5   (la magnanimità è rispettata)",    "yellow")
        stato["equipaggio"]  = stato.get("equipaggio",  10) - 3
        stato["morale"]      = stato.get("morale",       0) + 8
        stato["reputazione"] = stato.get("reputazione",  0) + 5
    else:
        stampa_lenta(
            f"La ciurma è troppo piccola e divisa. {traditore} ride in faccia alla tua grazia\n"
            f"e urla: «Chi mi segue?» — la metà dell'equipaggio esita.",
            "red", ritardo=0.025
        )
        variazione_stat("▼ Equipaggio  -5  (diserzioni nella notte)",        "red")
        variazione_stat("▼ Morale      -10 (la magnanimità è vista come debolezza)", "red")
        stato["equipaggio"] = stato.get("equipaggio", 10) - 5
        stato["morale"]     = stato.get("morale",      0) - 10
        esito = _controlla_equipaggio(stato, capitano)
        if esito is not True:
            return esito

    return True

# ------------------------------------------
# RAMO B — Ascolto nascosto
# ------------------------------------------

def _ramo_spia(stato, capitano, traditore, ruolo, motivazione):
    """Il capitano rimane nascosto ad ascoltare il piano nel dettaglio."""
    stampa_lenta(
        f"Ti muovi come un'ombra. Trattieni il respiro.\n"
        f"Le parole di {traditore} ti raggiungono nitide nel buio:",
        "white", ritardo=0.025
    )
    _pausa()

    piano_nemico = random.choice([
        f"vuole deviare la rotta verso {random.choice(['Cala Rossa','Porto Maledetto','Le Bocche di Ferro'])} per consegnarti ai nemici",
        "ha avvelenato i barili d'acqua — intende colpire all'alba",
        "ha già inviato un piccione con le coordinate del tesoro al governatore",
        "pianifica di aprire le stive durante la tempesta per affondare il galeone"
    ])
    stampa_lenta(
        f"«Il piano è pronto: {piano_nemico}.»\n"
        f"Ora sai tutto. La domanda è: come usi questa conoscenza?",
        "yellow", attrs=["bold"], ritardo=0.025
    )
    print()

    cprint("Hai sorpreso il traditore. Cosa fai con questa informazione?", "cyan", attrs=["bold"])
    print()
    cprint("  [A] Rivelare il piano alla ciurma fedele e usare il traditore come esca",  "white")
    cprint("  [B] Affrontare il traditore da solo, usandola come leva di potere",         "white")
    print()
    scelta = chiedi_scelta(
        colored("👉 La tua scelta (A/B): ", "cyan"),
        ["A", "B"]
    )

    if scelta == "A":
        return _svela_piano(stato, capitano, traditore)
    else:
        return _leva_potere(stato, capitano, traditore)

def _svela_piano(stato, capitano, traditore):
    """Il capitano usa il piano segreto per smascherare il traditore davanti a tutti."""
    stampa_lenta(
        "All'alba raduni la ciurma leale. Parli a bassa voce.\n"
        "In dieci minuti, la trappola è tesa.",
        "white", ritardo=0.025
    )
    _pausa()
    stampa_lenta(
        f"{traditore} cade nella rete. Viene catturato con le prove in mano.\n"
        f"La ciurma lo lega all'albero maestro tra urla di trionfo.",
        "green", ritardo=0.025
    )
    variazione_stat("▲ Reputazione +20  (tattico infallibile)",          "green")
    variazione_stat("▲ Morale      +12  (la ciurma si sente protetta)",  "green")
    variazione_stat("▲ Oro         +30  (trovate le sue riserve nascoste)", "yellow")
    stato["reputazione"] = stato.get("reputazione",  0) + 20
    stato["morale"]      = stato.get("morale",       0) + 12
    stato["oro"]         = stato.get("oro",           0) + 30

    cprint("\n🗺️  Bonus speciale: la rotta del nemico è nelle tue mani.", "yellow", attrs=["bold"])
    stampa_lenta(
        "Conosci ora i punti d'incontro segreti della flotta nemica.\n"
        "Puoi scegliere di tendere un'imboscata o evitarla con largo anticipo.",
        "cyan", ritardo=0.025
    )
    stato["info_nemico"] = True
    return True

def _leva_potere(stato, capitano, traditore):
    """Il capitano affronta il traditore da solo, usando le informazioni come leverage."""
    stampa_lenta(
        f"Lo trovi da solo sotto coperta. Ti avvicini in silenzio.\n"
        f"«So tutto, {traditore.split()[0]}.» — le tue parole lo pietrificano.",
        "white", ritardo=0.025
    )
    _pausa()

    esito = _dado(6)
    if esito >= 4:
        stampa_lenta(
            f"{traditore} bianchisce. Capitola. Diventa il tuo doppio agente:\n"
            f"ti passerà informazioni sui nemici per ogni porto che toccate.",
            "green", ritardo=0.025
        )
        variazione_stat("▲ Oro       +15  (pagamento immediato per il silenzio)", "yellow")
        variazione_stat("▲ Fortuna   +5   (un alleato insospettabile)",            "green")
        stato["oro"]     = stato.get("oro",     0) + 15
        stato["fortuna"] = stato.get("fortuna", 0) +  5
        stato["doppio_agente"] = traditore
    else:
        stampa_lenta(
            f"{traditore} finge di cedere — poi urla all'equipaggio che stai impazzendo.\n"
            f"La confusione si diffonde come fumo tra le vele.",
            "red", ritardo=0.025
        )
        variazione_stat("▼ Morale      -15 (il capitano sembra instabile)",  "red")
        variazione_stat("▼ Reputazione -10 (il dubbio si insinua nell'equipaggio)", "red")
        stato["morale"]      = stato.get("morale",      0) - 15
        stato["reputazione"] = stato.get("reputazione", 0) - 10
        esito_eq = _controlla_equipaggio(stato, capitano)
        if esito_eq is not True:
            return esito_eq

    return True

# ------------------------------------------
# RAMO C — Fuga nella stiva
# ------------------------------------------

def _ramo_fuggi(stato, capitano, traditore):
    """Il capitano evita il confronto e si nasconde, perdendo il controllo temporaneo."""
    stampa_lenta(
        "Ti ritiri nell'ombra. Ogni gradino della scaletta sembra urlare.\n"
        "Raggiungi la stiva. Silenzio. Al sicuro — per adesso.",
        "white", ritardo=0.025
    )
    _pausa()
    stampa_lenta(
        f"Ma {traditore} agisce indisturbato per tutta la notte.\n"
        f"All'alba trovi la rotta cambiata e venti monete sparite dalla cassa.",
        "red", ritardo=0.025
    )
    print()

    variazione_stat("▼ Oro         -20 (razziato dalla cassa di bordo)",         "red")
    variazione_stat("▼ Reputazione -15 (la ciurma ha visto la tua assenza)",     "red")
    variazione_stat("▼ Morale      -10 (il capitano ha abbandonato il ponte)",   "red")
    stato["oro"]         = stato.get("oro",          0) - 20
    stato["reputazione"] = stato.get("reputazione",  0) - 15
    stato["morale"]      = stato.get("morale",       0) - 10

    stampa_lenta(
        "Tre marinai fedeli ti bussano alla stiva: aspettano i tuoi ordini.\n"
        "La finestra per agire si sta chiudendo.",
        "yellow", ritardo=0.025
    )
    print()

    cprint("Non è ancora finita. Cosa fai all'alba?", "cyan", attrs=["bold"])
    print()
    cprint("  [A] Contrattaccare — radunare i fedeli e bloccare il traditore",  "white")
    cprint("  [B] Sparire a terra al prossimo porto e ricominciare da zero",     "white")
    print()
    scelta = chiedi_scelta(
        colored("👉 La tua scelta (A/B): ", "cyan"),
        ["A", "B"]
    )

    if scelta == "A":
        return _contrattacco_tardivo(stato, capitano, traditore)
    else:
        return _abbandono_nave(stato, capitano, traditore)

def _contrattacco_tardivo(stato, capitano, traditore):
    """Il capitano tenta un recupero all'alba con i marinai rimasti fedeli."""
    stampa_lenta(
        "Tre contro molti. Hai sorpreso eserciti interi con meno.\n"
        "Ti issano sul ponte di prodiera. Tiri fuori la pistola.",
        "white", ritardo=0.025
    )
    _pausa()

    fedeli        = stato.get("equipaggio", 10)
    tiro_recupero = _dado(20) + (fedeli // 3)

    cprint(f"\n  🎲 Tiro di recupero: {tiro_recupero} (soglia 14)", "cyan")
    time.sleep(0.5)

    if tiro_recupero >= 14:
        stampa_lenta(
            f"Il colpo in aria basta. {traditore} viene sopraffatto.\n"
            f"I complici si arrendono uno a uno. Il galeone è tuo di nuovo.",
            "green", ritardo=0.025
        )
        variazione_stat("▲ Reputazione +10 (recupero eroico)",            "green")
        variazione_stat("▼ Equipaggio  -2  (scontri durante la ripresa)", "red")
        stato["reputazione"] = stato.get("reputazione", 0) + 10
        stato["equipaggio"]  = stato.get("equipaggio",  10) - 2
        esito_eq = _controlla_equipaggio(stato, capitano)
        if esito_eq is not True:
            return esito_eq
    else:
        stampa_lenta(
            f"Non basta. {traditore} ha già convinto metà ciurma.\n"
            f"Vieni disarmato e rinchiuso nella cella di prua.",
            "red", ritardo=0.025
        )
        variazione_stat("▼ Salute      -20 (percosse durante la cattura)", "red")
        variazione_stat("▼ Equipaggio  -4  (defezioni dopo la tua caduta)", "red")
        stato["salute"]      = stato.get("salute",      100) - 20
        stato["equipaggio"]  = stato.get("equipaggio",   10) - 4

        if stato.get("salute", 100) <= 0 or stato.get("equipaggio", 10) <= 1:
            return game_over(
                f"Rinchiuso e abbandonato.\n"
                f"{traditore} guida il tuo galeone verso acque che non rivedrai mai.",
                stato, capitano
            )

        stampa_lenta(
            "Un marinajo fidato ti lascia una limetta tra i legni della cella.\n"
            "La storia non è ancora finita.",
            "yellow", ritardo=0.025
        )

    return True

def _abbandono_nave(stato, capitano, traditore):
    """Il capitano sceglie di sbarcare e ricominciare, perdendo la nave."""
    stampa_lenta(
        "Prendi le poche monete rimaste e salti sulla scialuppa.\n"
        "Remi verso le luci lontane della costa. Non ti giri a guardare.",
        "white", ritardo=0.025
    )
    _pausa()

    if stato.get("oro", 0) < 10:
        return game_over(
            "Sei a terra, senza nave, senza oro, senza nome.\n"
            "I moli puzzano di pesce e umiliazione. Fine della corsa.",
            stato, capitano
        )

    stampa_lenta(
        f"Porti con te il diario di bordo e una mappa parziale.\n"
        f"Forse al porto di {random.choice(['San Cristóbal','Veracruz','Tortuga','Nassau'])} "
        f"qualcuno venderà una barca.",
        "yellow", ritardo=0.025
    )
    variazione_stat("▼ Oro         -40  (costo di una nuova imbarcazione)", "red")
    variazione_stat("▼ Reputazione -25  (hai abbandonato il tuo galeone)",  "red")
    variazione_stat("▲ Sopravvivenza   (il capitano respira ancora)",       "green")
    stato["oro"]         = stato.get("oro",         0) - 40
    stato["reputazione"] = stato.get("reputazione", 0) - 25
    stato["nave"]        = "scialuppa"

    if stato["oro"] < 0:
        return game_over(
            "I debiti ti divorano prima che tu possa salpare di nuovo.\n"
            "Finisci a lavare i ponti di navi altrui.",
            stato, capitano
        )

    return True

# ------------------------------------------
# EPILOGO COMUNE
# ------------------------------------------

def _epilogo(stato, capitano, traditore, esito_positivo=True):
    """Scena conclusiva condivisa da tutti i rami sopravvissuti."""
    _stampa_separatore("cyan")
    if esito_positivo:
        stampa_lenta(
            f"Il sole sorge sul mare. {capitano} è ancora in piedi.\n"
            f"Il nome di {traditore} sarà dimenticato; il tuo no.",
            "cyan", attrs=["bold"], ritardo=0.03
        )
    else:
        stampa_lenta(
            f"Le acque non dimenticano. {capitano} porta i segni\n"
            f"di questa notte per molto tempo ancora.",
            "yellow", ritardo=0.03
        )
    _stampa_separatore("cyan")
    print()
    input(colored("⚓  [Premi Invio per riprendere il viaggio] ", "dark_grey"))

# ------------------------------------------
# FUNZIONE PRINCIPALE
# ------------------------------------------

def evento_tradimento(stato, capitano):
    """
    Evento principale del tradimento a bordo.
    Gestisce tre rami narrativi (A/B/C) con sotto-scelte e dadi.
    Ritorna True se il capitano sopravvive, False in caso di game over.
    """
    _stampa_intestazione_evento()

    traditore, ruolo, arma = random.choice(TRADITORI)[:3]
    motivazione             = random.choice(MOTIVAZIONI)

    _fase_scoperta(capitano, traditore, ruolo, arma, motivazione)

    try:
        scelta = _fase_scelta_iniziale()
    except InterruptedError:
        stampa_lenta(
            "Torni a letto. Forse era solo il vento. Forse no.",
            "dark_grey", ritardo=0.02
        )
        variazione_stat("▼ Reputazione -5  (l'occasione perduta)", "red")
        stato["reputazione"] = stato.get("reputazione", 0) - 5
        return True

    esito = True

    if scelta == "A":
        esito = _ramo_affronta(stato, capitano, traditore, ruolo, arma)
    elif scelta == "B":
        esito = _ramo_spia(stato, capitano, traditore, ruolo, motivazione)
    elif scelta == "C":
        esito = _ramo_fuggi(stato, capitano, traditore)

    if esito is False:
        return False

    _epilogo(stato, capitano, traditore, esito_positivo=(scelta != "C"))
    return True