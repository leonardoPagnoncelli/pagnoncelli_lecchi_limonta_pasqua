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