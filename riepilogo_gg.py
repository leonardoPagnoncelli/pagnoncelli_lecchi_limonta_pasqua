# ==========================================
# EPILOGO - PROFITTI, ASTA NAVE, FINALI
# ==========================================

import random
from termcolor import colored

import Stati_Ingaggio


# ==========================================
# CALCOLO PROFITTI
# ==========================================

def calcola_profitto_finale(stato):

    profitto = 0

    # RISORSE OTTENUTE DAL BARATTO
    profitto = profitto + (stato["risorse_baratto"]["perle"] * 180)

    profitto = profitto + (
        stato["risorse_baratto"]["manufatti"] * 250
    )

    profitto = profitto + (
        stato["risorse_baratto"]["spezie"] * 140
    )

    # DIAMANTI EVENTUALI
    profitto = profitto + (
        stato["merci"]["diamanti"] * 500
    )

    return int(profitto)


# ==========================================
# RESOCONTO SPEDIZIONE
# ==========================================

def mostra_resoconto(capitano, stato, profitto):

    pulisci_schermo()

    stampa_lenta(
        "=" * 60,
        "cyan",
        attrs=["bold"]
    )

    stampa_lenta(
        " 🏴‍☠️ RESOCONTO DELLA SPEDIZIONE 🏴‍☠️ ",
        "yellow",
        attrs=["bold"]
    )

    stampa_lenta(
        "=" * 60,
        "cyan",
        attrs=["bold"]
    )

    print()

    stampa_lenta(
        "⚓ Capitano: " + capitano,
        "yellow"
    )

    print()

    # EQUIPAGGIO
    vivi = Stati_Ingaggio.conta_equipaggio(stato)

    print(
        "👥 Equipaggio sopravvissuto: "
        + colored(str(vivi), "green")
    )

    print(
        "🗓️ Settimane di viaggio: "
        + colored(
            str(stato["settimane_percorse"]),
            "cyan"
        )
    )

    print(
        "🛡️ Integrità nave: "
        + colored(
            str(stato["integrita"]) + "%",
            "yellow"
        )
    )

    print(
        "⚠️ Ammutinamento finale: "
        + colored(
            str(stato["punti_ammutinamento"]),
            "red"
        )
    )

    print()

    # RISORSE OTTENUTE
    stampa_lenta(
        "💰 RISORSE OTTENUTE:",
        "green",
        attrs=["bold"]
    )

    for r in stato["risorse_baratto"]:

        qty = stato["risorse_baratto"][r]

        if qty > 0:

            print(
                "  "
                + r.capitalize()
                + ": "
                + str(round(qty, 1))
            )

    print()

    stampa_lenta(
        "💎 Profitto totale: "
        + str(int(profitto))
        + " monete",
        "green",
        attrs=["bold"]
    )

    print()


# ==========================================
# ASTA DELLA NAVE
# ==========================================

def asta_nave(debito):

    offerte = [
        50,
        300,
        350,
        400,
        450,
        500,
        550,
        600,
        650,
        700,
        750,
        800,
        850,
        1200
    ]

    # offerte infinite
    ripetibili = [50, 300, 400, 450]

    usate = {}

    stampa_lenta(
        "\n⚖️ Il galeone viene messo all'asta...",
        "yellow",
        attrs=["bold"]
    )

    while True:

        offerta = random.choice(offerte)

        if offerta not in ripetibili:

            if offerta in usate:

                if usate[offerta] >= 2:
                    continue

        usate[offerta] = usate.get(offerta, 0) + 1

        print()

        stampa_lenta(
            "💰 Offerta ricevuta: "
            + str(offerta)
            + " monete",
            "cyan",
            attrs=["bold"]
        )

        scelta = chiedi_opzione(
            "Accetti l'offerta?"
        )

        if scelta:

            if offerta >= debito:

                stampa_lenta(
                    "\n⚖️ Il debito viene saldato.",
                    "green",
                    attrs=["bold"]
                )

                return True

            else:

                stampa_lenta(
                    "\n❌ Il denaro non basta.",
                    "red"
                )

                return False


# ==========================================
# FINALE COMPLETO
# ==========================================

def conclusione(capitano, stato):

    profitto = calcola_profitto_finale(stato)

    soldi_finali = stato["budget"]

    debito = stato["debito_equipaggio"]

    saldo = profitto + soldi_finali - debito

    mostra_resoconto(
        capitano,
        stato,
        profitto
    )

    print(
        "🪙 Denaro residuo: "
        + colored(
            str(int(soldi_finali)),
            "yellow"
        )
    )

    print(
        "👥 Debiti equipaggio: "
        + colored(
            str(int(debito)),
            "red"
        )
    )

    print()

    stampa_lenta(
        "📊 Saldo finale: "
        + str(int(saldo))
        + " monete",
        "cyan",
        attrs=["bold"]
    )

    print()

    # ==========================================
    # VITTORIA EPICA
    # ==========================================

    if saldo > 0:

        stampa_lenta(
            "👑 La spedizione è stata un enorme successo.",
            "green",
            attrs=["bold"]
        )

        stampa_lenta(
            "Il tuo nome verrà ricordato nei porti di tutta Europa.",
            "green"
        )

        dati = carica_dati()

        dati["stats"]["vittorie_epiche"] += 1

        salva_dati(dati)

        archivia_partita(
            capitano,
            stato,
            "Vittoria Epica"
        )

        input(
            colored(
                "\n📖 Premi Invio per continuare ",
                "dark_grey"
            )
        )

        return True

    # ==========================================
    # VITTORIA DI PIRRO
    # ==========================================

    elif saldo == 0:

        stampa_lenta(
            "⚖️ Sei sopravvissuto...",
            "yellow",
            attrs=["bold"]
        )

        stampa_lenta(
            "Ma non hai guadagnato nulla.",
            "yellow"
        )

        dati = carica_dati()

        dati["stats"]["vittorie_pirro"] += 1

        salva_dati(dati)

        archivia_partita(
            capitano,
            stato,
            "Vittoria di Pirro"
        )

        input(
            colored(
                "\n📖 Premi Invio per continuare ",
                "dark_grey"
            )
        )

        return True

    # ==========================================
    # ROVINA ECONOMICA
    # ==========================================

    else:

        stampa_lenta(
            "⛓️ I debiti superano i profitti.",
            "red",
            attrs=["bold"]
        )

        scelta = chiedi_opzione(
            "Vuoi mettere all'asta il galeone?"
        )

        if scelta:

            esito = asta_nave(abs(saldo))

            if esito:

                stampa_lenta(
                    "\n⚖️ Riesci a evitare la rovina.",
                    "yellow",
                    attrs=["bold"]
                )

                archivia_partita(
                    capitano,
                    stato,
                    "Nave Venduta"
                )

                input(
                    colored(
                        "\n📖 Premi Invio per continuare ",
                        "dark_grey"
                    )
                )

                return True

        stampa_lenta(
            "\n💀 Nessuno vuole salvarti.",
            "red"
        )

        stampa_lenta(
            "L'equipaggio ti abbandona.",
            "red"
        )

        stampa_lenta(
            "I creditori reclamano tutto ciò che possiedi.",
            "red"
        )

        dati = carica_dati()

        dati["stats"]["rovine"] += 1

        salva_dati(dati)

        archivia_partita(
            capitano,
            stato,
            "Rovina Totale"
        )

        input(
            colored(
                "\n📖 Premi Invio per continuare ",
                "dark_grey"
            )
        )

        return False