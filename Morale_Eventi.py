'''
Giorno 1 — 
Correggere EVT-I, EVT-J, EVT-K (3 funzioni da riscrivere completamente); 
correggere MORALE-2 (range venti favorevoli e verifica tutti i delta); 
correggere ALBATRO-1 (controllo armi prima di proporre la scelta) 

Giorno 2 — 
Correggere ALBATRO-2/3 (logica tentativi, carne guadagnata, rimozione armi usate); 
correggere SCIALUPPA-2/3 (ruolo casuale, morale casuale, bonus cassa merci); 
separare EVT-B/C/D/E in 4 funzioni distinte con frazioni corrette; 
attendere STATO-7 da P1 e integrare moltiplicatore in consuma_scorte_dettagliate() 

Giorno 3 — 
Riscrivere EPIDEMIA-1/2/3 (logica 70%, bottiglie per malato, report dettagliato); 
riscrivere PIRATA-1/2/3/4 (formula corretta, rimozione opzioni non previste); 
correggere TIMONE-1/2 (solo meccanico); 
correggere VENTO-1/2 (solo navigatore, rimuovere danno nave); 
riscrivere ISOLA-1/2/3/4 (logica completa con approdo, 50%/50%, bonus merci e albatro); 
consegnare a P3 le variabili di stato aggiornate (merci dopo eventi, settimane, flag albatro)

Giorno 4 — 
Implementare step2_controllo_scorte() completo con STEP2-1/2/3/4 e integrarlo nel loop _ciclo_viaggio(); 
implementare calcola_ammutinamento() da zero con i 7 criteri corretti e 
integrarla in _ciclo_viaggio() sostituendo il vecchio contatore cumulativo; 
test completo del loop di viaggio end-to-end 

'''

#Limonta
import Stati_Ingaggio
import nuovo_mondo
import random


def varia_morale_tutti(stato, delta, motivo=""):
# Valori standardizzati delta
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
        delta = delta_map[motivo]()

    for k in stato["morale_individuale"]:
        stato["morale_individuale"][k] = max(0,min(100, stato["morale_individuale"][k] + delta))

    if motivo:
        nuovo_mondo.variazione_stat(f"📊 Morale {delta:+} ({motivo})","green" if delta > 0 else "red")

    controlla_morti_morale_zero(stato)


def controlla_morti_morale_zero(stato):
    morti = [k for k, v in stato["morale_individuale"].items() if v <= 0]

    for morto in morti:
        del stato["morale_individuale"][morto]

        for ruolo, nome in Stati_Ingaggio.NOMI_RUOLO.items():
            if morto.startswith(nome):
                stato["equipaggio"][ruolo] = max(0, stato["equipaggio"].get(ruolo, 0) - 1)
                nuovo_mondo.cprint(f"💀 {morto} morto per morale zero", "red", attrs=["bold"])
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

    # +30 se almeno una razione in razioni_moltiplicatore < 1
    if any(v < 1 for v in stato["razioni_moltiplicatore"].values()):
        p += 30
        cause.append("Razioni ridotte")

    # +30 se nessun cuoco a bordo
    if stato["equipaggio"].get("cuochi", 0) == 0:
        p += 30
        cause.append("Nessun cuoco a bordo")

    # +30 se albatro ucciso (presagio di sfiga)
    if stato.get("albatro_ucciso"):
        p += 30
        cause.append("Presagio di sfiga (albatro ucciso)")

    # -20 se avvistamento albatro ma NON ucciso (ottimismo)
    if stato["avvistamenti_albatro"] > 0 and not stato.get("albatro_ucciso"):
        p -= 20
        cause.append("Ottimismo (avvistamento albatro)")

    # +30 se nave troppo affollata (equipaggio > 12)
    if Stati_Ingaggio.conta_equipaggio(stato) > 12:
        p += 30
        cause.append("Nave troppo affollata")

    # +10 per ogni settimana extra oltre le 8 stimate
    p += 10 * stato.get("settimane_extra", 0)

    # -10 per ogni settimana risparmiata
    p -= 10 * stato.get("settimane_risparmiate", 0)

    # Comunicazione e game over
    if p >= 100:
        nuovo_mondo.game_over("Ammutinamento totale")
    elif 1 <= p < 100:
        nuovo_mondo.stampa_lenta(f"⚠ Ammutinamento: {p}% | Cause: {', '.join(cause)}", "red" )

    return p, cause

def aggiungi_punti_ammutinamento(stato, punti, motivo=""):
    stato['punti_ammutinamento'] = stato.get('punti_ammutinamento', 0) + punti
    if motivo:
        nuovo_mondo.variazione_stat(f"⚠️  +{punti} punti ammutinamento ({motivo})", "red")


# ==========================================
# UTILITÀ
# ==========================================

def perdita_frazione(valore):
    return int(valore * random.choice([0.5, 1/3, 0.25, 0.2]))


# ==========================================
# EVENTI
# ==========================================
def evento_uomo_in_mare(stato): #A
    nuovo_mondo.stampa_lenta("🌊 UOMO IN MARE! Un'onda gigantesca spazza il ponte senza preavviso.", "red", attrs=["bold"])
    ruoli_vivi = [r for r in stato['equipaggio'] if stato['equipaggio'][r] > 0]
    if ruoli_vivi:
        ruolo = random.choice(ruoli_vivi)
        vittima = Stati_Ingaggio.rimuovi_membro(stato, ruolo)
        varia_morale_tutti(stato, -15, "collega caduto in mare")
        nuovo_mondo.variazione_stat(f"💀 Hai perso {vittima or '1 membro'}!", "red")
        aggiungi_punti_ammutinamento(stato, 10, "morte in mare")
    else:
        nuovo_mondo.stampa_lenta("Miracolosamente, nessuno cade.", "green")


def evento_verdura_in_mare(stato): #B
    perdita = perdita_frazione(stato["merci"]["verdura"])
    stato["merci"]["verdura"] = max(0, stato["merci"]["verdura"] - perdita)
    nuovo_mondo.stampa_lenta(f"🌊 Un'onda strappa verdura dalla nave (-{perdita} verdura)", "yellow")
    varia_morale_tutti(stato, -10, "scorte esaurite")


def evento_frutta_in_mare(stato): #C
    perdita = perdita_frazione(stato["merci"]["frutta"])
    stato["merci"]["frutta"] = max(0, stato["merci"]["frutta"] - perdita)
    nuovo_mondo.stampa_lenta(f"🌊 Un'onda strappa frutta dalla nave (-{perdita} frutta)", "yellow")
    varia_morale_tutti(stato, -10, "scorte esaurite")


def evento_carne_in_mare(stato): #D
    perdita = perdita_frazione(stato["merci"]["carne"])
    stato["merci"]["carne"] = max(0, stato["merci"]["carne"] - perdita)
    nuovo_mondo.stampa_lenta(f"🌊 Un'onda strappa carne dalla nave (-{perdita} carne)", "yellow")
    varia_morale_tutti(stato, -10, "scorte esaurite")


def evento_acqua_in_mare(stato): #E
    perdita = perdita_frazione(stato["merci"]["acqua"])
    stato["merci"]["acqua"] = max(0, stato["merci"]["acqua"] - perdita)
    nuovo_mondo.stampa_lenta(f"🌊 Un'onda strappa acqua dalla nave (-{perdita} acqua)", "yellow")
    varia_morale_tutti(stato, -10, "scorte esaurite")


def evento_pesca_miracolosa(stato): #F
    nuovo_mondo.stampa_lenta("🎣 Un banco di pesci enormi circonda la nave. Pesca miracolosa!", "green", attrs=["bold"])
    carne_guadagnata = random.uniform(8, 20)
    stato['scorte']['carne'] += carne_guadagnata
    nuovo_mondo.variazione_stat(f"📈 +{carne_guadagnata:.1f} 🥩 Carne (pesca)", "green")
    varia_morale_tutti(stato, +5, "pesca miracolosa")


def evento_tempesta_miracolosa(stato): #G
    nuovo_mondo.stampa_lenta("⛈️ Una tempesta provvidenziale! La pioggia riempie ogni contenitore e lava i malati.", "cyan", attrs=["bold"])
    acqua_guadagnata = random.uniform(10, 25)
    stato['scorte']['acqua'] += acqua_guadagnata
    varia_morale_tutti(stato, +15, "tempesta miracolosa")
    nuovo_mondo.variazione_stat(f"📈 +{acqua_guadagnata:.1f} 💧 Acqua", "green")


def evento_venti_favorevoli(stato): #H
    nuovo_mondo.stampa_lenta("💨 VENTI FAVOREVOLI! Le vele si gonfiano al massimo. Avanzate di settimane in giorni!", "green", attrs=["bold"])
    stato['settimane_risparmiate'] = stato.get('settimane_risparmiate', 0) + 1
    bonus = random.randint(5, 15)  
    varia_morale_tutti(stato, bonus, f"venti favorevoli (+{bonus})")
    nuovo_mondo.variazione_stat("📈 Viaggio accorciato di 1 settimana!", "green")      


def evento_cattivo_tempo(stato): #I
    perdita = perdita_frazione(stato["merci"]["bottiglie_medicinale"])
    stato["merci"]["bottiglie_medicinale"] = max(0, stato["merci"]["bottiglie_medicinale"] - perdita)
    nuovo_mondo.stampa_lenta(f"⛈️  Cattivo tempo: bottiglie di medicinale danneggiate (-{perdita})", "yellow")


def evento_ondata(stato): #J
    perdita = perdita_frazione(stato["merci"]["armi"])
    stato["merci"]["armi"] = max(0, stato["merci"]["armi"] - perdita)
    nuovo_mondo.stampa_lenta(f"🌊 Ondata gigantesca: armi danneggiate dall'acqua (-{perdita})", "yellow")


def evento_infestazione_ratti(stato): #K
    perdita = perdita_frazione(stato["merci"]["stoffa"])
    stato["merci"]["stoffa"] = max(0, stato["merci"]["stoffa"] - perdita)
    nuovo_mondo.stampa_lenta(f"🐭 Infestazione di ratti: stoffa danneggiata (-{perdita})", "yellow")


def evento_albatro(stato): #ALBATRO-1
    if stato["merci"]["armi"] <= 0:
        nuovo_mondo.stampa_lenta("🐦 Un albatro maestoso vola vicino... ma senza armi, non puoi fare nulla.", "cyan")
        stato["avvistamenti_albatro"] += 1
        return

    vivi = Stati_Ingaggio.conta_equipaggio(stato)
    
    # ALBATRO-2 
    max_tiri = min(stato["merci"]["armi"], vivi)
    
    nuovo_mondo.stampa_lenta(f"🐦 Un albatro gigantesco appare! {max_tiri} membri dell'equipaggio prendono le armi!", "cyan")
    
    armi_usate = 0
    abbattuto = False

    for tentativo in range(1, max_tiri + 1):
        armi_usate += 1
        if random.random() < 0.5:
            abbattuto = True
            nuovo_mondo.stampa_lenta(f"  🎯 Tentativo {tentativo}: COLPITO!", "green")
            break
        else:
            nuovo_mondo.stampa_lenta(f"  ❌ Tentativo {tentativo}: mancato", "yellow")

    stato["merci"]["armi"] -= armi_usate

    if abbattuto:
        # ALBATRO-3 
        carne_aggiunta = random.randint(10, 15)
        stato["merci"]["carne"] += carne_aggiunta
        stato["albatro_ucciso"] = True
        stato["avvistamenti_albatro"] += 1
        nuovo_mondo.stampa_lenta(
            f"☠️  Albatro abbattuto! +{carne_aggiunta} kg di carne fresca","red",attrs=["bold"])
        varia_morale_tutti(stato, +10, "albatro abbattuto (caccia di successo)")
    else:
        stato["avvistamenti_albatro"] += 1
        nuovo_mondo.stampa_lenta("🐦 L'albatro scappa dopo il fuoco. Cattivo presagio...", "cyan")
