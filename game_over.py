# ==========================================
# GAME OVER E FINALI
# ==========================================

import random
from termcolor import colored

import Stati_Ingaggio
import nuovo_mondo


# ==========================================
# GAME OVER GENERICO
# ==========================================

def game_over(messaggio, stato, capitano):

    dati = nuovo_mondo.carica_dati()

    dati["stats"]["morti"] += 1

    nuovo_mondo.salva_dati(dati)

    print()

    nuovo_mondo.stampa_lenta("=" * 60, "red", attrs=["bold"])

    nuovo_mondo.stampa_lenta(messaggio, "red")

    nuovo_mondo.stampa_lenta(
        "\n💀 === GAME OVER === 💀\n",
        "red",
        attrs=["bold", "blink"]
    )

    nuovo_mondo.stampa_lenta("=" * 60, "red", attrs=["bold"])

    nuovo_mondo.archivia_partita(capitano, stato, "Morto in mare")

    return False


# ==========================================
# CONTROLLO EQUIPAGGIO
# ==========================================

def controlla_equipaggio_vivo(stato, capitano):

    vivi = Stati_Ingaggio.conta_equipaggio(stato)

    if vivi <= 0:

        return game_over(
            "☠️ Tutto l'equipaggio è morto.\n"
            "La spedizione termina nelle profondità dell'oceano.",
            stato,
            capitano
        )

    return True


# ==========================================
# GAME OVER EPIDEMIA
# ==========================================

def game_over_epidemia(stato, capitano):

    if Stati_Ingaggio.conta_equipaggio(stato) <= 0:

        return game_over(
            "☣️ L'epidemia ha sterminato l'intero equipaggio.",
            stato,
            capitano
        )

    return True


# ==========================================
# GAME OVER PIRATI
# ==========================================

def game_over_pirati(stato, capitano):

    if Stati_Ingaggio.conta_equipaggio(stato) <= 0:

        return game_over(
            "🏴‍☠️ I pirati hanno massacrato l'intero equipaggio.",
            stato,
            capitano
        )

    return True


# ==========================================
# CONTROLLO MORALE
# ==========================================

def aggiorna_morale_e_controlla_morti(stato, capitano):

    morti = []

    for membro in list(stato["morale_individuale"]):

        morale = stato["morale_individuale"][membro]

        if morale <= 0:
            morti.append(membro)

    for membro in morti:

        del stato["morale_individuale"][membro]

        ruolo = membro.split("_")[0]

        if ruolo in stato["equipaggio"]:
            stato["equipaggio"][ruolo] -= 1

        nuovo_mondo.stampa_lenta(
            "💀 " + membro + " muore di disperazione.",
            "red"
        )

    if Stati_Ingaggio.conta_equipaggio(stato) <= 0:

        return game_over(
            "☠️ Il morale dell'equipaggio è collassato.\n"
            "Nessuno è sopravvissuto alla spedizione.",
            stato,
            capitano
        )

    return True


# ==========================================
# ATTACCO INDIGENI
# ==========================================

def game_over_indigeni(stato, capitano):

    return game_over(
        "🪶 Gli indigeni reagiscono immediatamente.\n"
        "L'equipaggio viene circondato e massacrato.",
        stato,
        capitano
    )


# ==========================================
# TRADIMENTO SCOPERTO
# ==========================================

def game_over_tradimento(stato, capitano):

    return game_over(
        "⚔️ Il capo tribù scopre il tuo tradimento.\n"
        "L'intero equipaggio viene giustiziato.",
        stato,
        capitano
    )


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

    ripetibili = [50, 300, 400, 450]

    usate = {}

    while True:

        offerta = random.choice(offerte)

        if offerta not in ripetibili:

            if offerta in usate:

                if usate[offerta] >= 2:
                    continue

        usate[offerta] = usate.get(offerta, 0) + 1

        print()

        nuovo_mondo.stampa_lenta(
            "💰 Offerta ricevuta: " + str(offerta) + " monete",
            "yellow",
            attrs=["bold"]
        )

        scelta = nuovo_mondo.chiedi_opzione("Accetti l'offerta?")

        if scelta:

            if offerta >= debito:
                return True

            return False


# ==========================================
# FINALE ECONOMICO
# ==========================================

def valuta_finale(
    capitano,
    stato,
    profitto,
    soldi_residui
):

    debito = stato["debito_equipaggio"]

    totale = soldi_residui + profitto

    saldo = totale - debito

    print()

    nuovo_mondo.stampa_lenta(
        "=" * 60,
        "cyan",
        attrs=["bold"]
    )

    nuovo_mondo.stampa_lenta(
        " 💰 RESOCONTO FINALE DELLA SPEDIZIONE 💰 ",
        "yellow",
        attrs=["bold"]
    )

    nuovo_mondo.stampa_lenta(
        "=" * 60,
        "cyan",
        attrs=["bold"]
    )

    print(
        "💎 Profitto merci: "
        + colored(str(int(profitto)), "green")
    )

    print(
        "🪙 Denaro residuo: "
        + colored(str(int(soldi_residui)), "yellow")
    )

    print(
        "👥 Debito equipaggio: "
        + colored(str(int(debito)), "red")
    )

    print(
        "📊 Saldo finale: "
        + colored(str(int(saldo)), "cyan", attrs=["bold"])
    )

    print()

    # ==========================================
    # VITTORIA
    # ==========================================

    if saldo > 0:

        nuovo_mondo.stampa_lenta(
            "👑 La spedizione è stata un successo!",
            "green",
            attrs=["bold"]
        )

        dati = nuovo_mondo.carica_dati()

        dati["stats"]["vittorie_epiche"] += 1

        nuovo_mondo.salva_dati(dati)

        nuovo_mondo.archivia_partita(
            capitano,
            stato,
            "Vittoria Epica"
        )

        return True

    # ==========================================
    # PAREGGIO
    # ==========================================

    elif saldo == 0:

        nuovo_mondo.stampa_lenta(
            "⚖️ Sei sopravvissuto...\n"
            "ma senza alcun guadagno.",
            "yellow",
            attrs=["bold"]
        )

        dati = nuovo_mondo.carica_dati()

        dati["stats"]["vittorie_pirro"] += 1

        nuovo_mondo.salva_dati(dati)

        nuovo_mondo.archivia_partita(
            capitano,
            stato,
            "Vittoria di Pirro"
        )

        return True

    # ==========================================
    # ROVINA
    # ==========================================

    else:

        nuovo_mondo.stampa_lenta(
            "⛓️ Non riesci a pagare l'equipaggio.",
            "red",
            attrs=["bold"]
        )

        scelta = nuovo_mondo.chiedi_opzione(
            "Vuoi mettere all'asta il galeone?"
        )

        if scelta:

            esito = asta_nave(abs(saldo))

            if esito:

                nuovo_mondo.stampa_lenta(
                    "⚖️ Riesci a saldare i debiti\n"
                    "vendendo la nave.",
                    "yellow",
                    attrs=["bold"]
                )

                nuovo_mondo.archivia_partita(
                    capitano,
                    stato,
                    "Nave Venduta"
                )

                return True

        dati = nuovo_mondo.carica_dati()

        dati["stats"]["rovine"] += 1

        nuovo_mondo.salva_dati(dati)

        nuovo_mondo.archivia_partita(
            capitano,
            stato,
            "Rovina Totale"
        )

        nuovo_mondo.stampa_lenta(
            "\n💀 Finisci sommerso dai debiti.\n"
            "L'equipaggio ti abbandona.\n"
            "La tua leggenda termina qui.",
            "red",
            attrs=["bold"]
        )

        return False