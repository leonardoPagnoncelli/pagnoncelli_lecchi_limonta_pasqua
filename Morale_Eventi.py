#Limonta
import Arrivo_GameOver
import Stati_Ingaggio
import nuovo_mondo


try:
    import msvcrt
    is_windows = True
except ImportError:
    import select
    is_windows = False


def varia_morale_tutti(stato, delta, motivo=""):
    """Varia morale di tutti i membri."""
    for k in stato['morale_individuale']:
        stato['morale_individuale'][k] = max(0, min(100, stato['morale_individuale'][k] + delta))
    if motivo:
        segno = "📈" if delta > 0 else "📉"
        nuovo_mondo.variazione_stat(f"{segno} Morale {'+' if delta>0 else ''}{delta} ({motivo})", "green" if delta > 0 else "red")
    nuovo_mondo.controlla_morti_morale_zero(stato)

def controlla_morti_morale_zero(stato):
    """TODO-11: morte automatica membri con morale = 0."""
    morti = [k for k, v in list(stato['morale_individuale'].items()) if v <= 0]
    for morto in morti:
        del stato['morale_individuale'][morto]
        for ruolo, nome_singolo in Stati_Ingaggio.NOMI_RUOLO.items():
            if morto.startswith(nome_singolo):
                stato['equipaggio'][ruolo] = max(0, stato['equipaggio'].get(ruolo, 0) - 1)
                nuovo_mondo.cprint(f"  💀 {morto} è morto per morale a zero!", "red", attrs=["bold"])
                break

def equipaggio_basso_morale(stato, soglia=30):
    """TODO-12: controlla se più della metà ha morale ≤ soglia."""
    morali = list(stato['morale_individuale'].values())
    if not morali:
        return False
    bassi = sum(1 for m in morali if m <= soglia)
    return bassi > len(morali) / 2