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
from termcolor import colored, cprint


def varia_morale_tutti(stato, delta, motivo=""):    
    for k in stato["morale_individuale"]:
        stato["morale_individuale"][k] = stato["morale_individuale"][k] + delta
        if stato["morale_individuale"][k] > 100:
            stato["morale_individuale"][k] = 100
        elif stato["morale_individuale"][k] < 0:
            stato["morale_individuale"][k] = 0

    if motivo != "":
        if delta > 0:
            nuovo_mondo.variazione_stat(f"📈 Morale {delta} ({motivo})", "green")
        else:
            nuovo_mondo.variazione_stat(f"📉 Morale {delta} ({motivo})", "red")

    nuovo_mondo.controlla_morti_morale_zero(stato)

def controlla_morti_morale_zero(stato):
    morti = []
    for k, v in stato["morale_individuale"].items():
        if v <= 0:
            morti.append(k)

    for morto in morti:
        del stato["morale_individuale"][morto]

        for ruolo, nome_singolo in Stati_Ingaggio.NOMI_RUOLO.items():
            if morto.startswith(nome_singolo):
                stato["equipaggio"][ruolo] = stato["equipaggio"].get(ruolo, 0) - 1
                if stato["equipaggio"][ruolo] < 0:
                    stato["equipaggio"][ruolo] = 0
                nuovo_mondo.cprint("  💀 " + morto + " è morto per morale a zero!", "red", attrs=["bold"])
                break

def equipaggio_basso_morale(stato, soglia=30):
    morali = []
    for k, v in stato["morale_individuale"].items():
        morali.append(v)

    if len(morali) == 0:
        return False
    
    bassi = 0

    for m in morali:
        if m <= soglia:
            bassi = bassi + 1

    return bassi > len(morali) / 2