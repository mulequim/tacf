
# tacf_functions.py (updated)
# Loads threshold JSONs and computes scores for TACF (NSCA 54-3) - Masculino e Feminino
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent / "tacf_data"

TRADUCAO_CAMPOS = {
    "C. Cintura": "Circunferência da Cintura (cm)",
    "FEMS": "Flexão e Extensão dos M. Superiores (Repetições)",
    "FTSC": "Flexão do Tronco Sobre as Coxas (Repetições)",
    "Corrida 12 min": "Corrida 12 Minutos (Metros)",
}

CONCEITUACAO_GLOBAL = {
    "E": (90.0, 100.0),
    "MB": (70.0, 89.9),
    "B": (40.0, 69.9),
    "S": (20.0, 39.9),
    "I": (0.0, 19.9),
}

PONTUACAO_MINIMA_APROVACAO = 20.0

# Weights (to sum to 100): OIC01 (cintura) 30, OIC02 30, OIC03 20, OIC04 20
OIC_WEIGHTS = {
    "C. Cintura": 30,
    "FEMS": 30,
    "FTSC": 20,
    "Corrida 12 min": 20
}

def _load_json(name):
    p = BASE_DIR / name
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

# Load all tables on import
OIC01_M = _load_json("oic01_m.json")
OIC01_F = _load_json("oic01_f.json")
OIC02_M = _load_json("oic02_m.json")
OIC02_F = _load_json("oic02_f.json")
OIC03_M = _load_json("oic03_m.json")
OIC03_F = _load_json("oic03_f.json")
OIC04_M = _load_json("oic04_m.json")
OIC04_F = _load_json("oic04_f.json")

def get_faixa_etaria(idade, sexo):
    if sexo == "Masculino":
        if idade <= 20: return "≤ 20"
        if 21 <= idade <= 30: return "21-30"
        if 31 <= idade <= 34: return "31-34"
        if 35 <= idade <= 38: return "35-38"
        if 39 <= idade <= 41: return "39-41"
        if 42 <= idade <= 43: return "42-43"
        if 44 <= idade <= 49: return "44-49"
        if 50 <= idade <= 52: return "50-52"
        return "≥ 53"
    else:
        if idade <= 21: return "≤ 21"
        if 22 <= idade <= 25: return "22-25"
        if 26 <= idade <= 29: return "26-29"
        if 30 <= idade <= 33: return "30-33"
        if 34 <= idade <= 37: return "34-37"
        if 38 <= idade <= 41: return "38-41"
        if 42 <= idade <= 45: return "42-45"
        return "≥ 46"

def get_faixa_estatura(est_cm, sexo):
    if sexo == "Masculino":
        if est_cm <= 166: return "≤ 166"
        if 167 <= est_cm <= 171: return "167-171"
        if 172 <= est_cm <= 175: return "172-175"
        if 176 <= est_cm <= 180: return "176-180"
        if 181 <= est_cm <= 188: return "181-188"
        return "≥ 189"
    else:
        if est_cm <= 161: return "≤ 161"
        if 162 <= est_cm <= 166: return "162-166"
        return "≥ 167"

def _interp_score(value, thresholds, better_higher=True):
    """
    Generic interpolation:
    thresholds is dict with keys: I, S_upper, B_upper, MB_upper, E_upper
    If better_higher==True (FEMS, FTSC, Corrida): larger value is better.
    If False (Cintura): smaller value is better.
    Returns normalized score between 0.0 and 1.0 representing performance within range from I..E.
    """
    I = thresholds.get("I")
    S = thresholds.get("S_upper")
    B = thresholds.get("B_upper")
    MB = thresholds.get("MB_upper")
    E = thresholds.get("E_upper")

    # Build ordered boundaries depending on better_higher
    if better_higher:
        # increasing order: I < S < B < MB < E
        bounds = [I, S, B, MB, E]
    else:
        # for measures where lower is better (cintura): reverse sense
        bounds = [E, MB, B, S, I]  # E is best (lowest)
    # If any bound missing, fallback to simple step logic
    if None in bounds:
        # fallback: return 0 if below I, 1 if >= E, linear else
        if better_higher:
            if value < I: return 0.0
            if value >= E: return 1.0
            # linear between I and E
            return float(value - I) / float(E - I)
        else:
            if value > I: return 0.0
            if value <= E: return 1.0
            return float(I - value) / float(I - E)

    # Determine category position
    if better_higher:
        if value <= I:
            return 0.0
        if value >= E:
            return 1.0
        # find which interval it is in
        intervals = [(I, S), (S, B), (B, MB), (MB, E)]
        for lo, hi in intervals:
            if lo <= value <= hi:
                # map lo-> fraction, hi-> fraction
                # fractions: I->0.0, S->0.25, B->0.5, MB->0.75, E->1.0
                base = {I:0.0, S:0.25, B:0.5, MB:0.75, E:1.0}
                lo_frac = base[lo]
                hi_frac = base[hi]
                if hi == lo:
                    return hi_frac
                frac = lo_frac + (hi_frac - lo_frac) * (value - lo) / (hi - lo)
                return frac
    else:
        # smaller is better
        if value >= I:
            return 0.0
        if value <= E:
            return 1.0
        intervals = [(I, MB), (MB, B), (B, S), (S, E)]  # descending actual performance
        base_vals = {I:0.0, "MB":0.25, "B":0.5, "S":0.75, "E":1.0}
        # but easier: treat as inverted linear between bounds
        # find where value lies between bounds from high to low
        desc_bounds = [I, S, B, MB, E]  # descending performance
        for i in range(len(desc_bounds)-1):
            hi = desc_bounds[i]
            lo = desc_bounds[i+1]
            if lo <= value <= hi:
                # hi -> lower fraction, lo -> higher fraction
                hi_frac = (i) * 0.25  # i=0 ->0.0, i=4->1.0
                lo_frac = (i+1) * 0.25
                if hi == lo:
                    return lo_frac
                frac = hi_frac + (lo_frac - hi_frac) * (hi - value) / (hi - lo)
                return frac

    return 0.0

def buscar_pontos_oic(oic_nome, sexo, valor_candidato, faixa_idade=None, faixa_estatura=None):
    """
    Returns: points (scaled to weight later), min_allowed (I boundary), max_boundary (E boundary)
    """
    if oic_nome == "C. Cintura":
        tabela = OIC01_M if sexo == "Masculino" else OIC01_F
        faixa = faixa_estatura
        if faixa not in tabela:
            return 0.0, None, None
        thresholds = tabela[faixa]
        score_norm = _interp_score(valor_candidato, thresholds, better_higher=False)
        # Scale to OIC weight (30)
        weight = OIC_WEIGHTS[oic_nome]
        points = score_norm * weight
        return points, thresholds.get("I"), thresholds.get("E")
    else:
        if oic_nome == "FEMS":
            tabela = OIC02_M if sexo == "Masculino" else OIC02_F
        elif oic_nome == "FTSC":
            tabela = OIC03_M if sexo == "Masculino" else OIC03_F
        elif oic_nome == "Corrida 12 min":
            tabela = OIC04_M if sexo == "Masculino" else OIC04_F
        else:
            tabela = {}

        faixa = faixa_idade
        if faixa not in tabela:
            return 0.0, None, None
        thresholds = tabela[faixa]
        score_norm = _interp_score(valor_candidato, thresholds, better_higher=True)
        weight = OIC_WEIGHTS[oic_nome]
        points = score_norm * weight
        return points, thresholds.get("I"), thresholds.get("E")

def calcular_resultado(sexo, idade, estatura, resultados_candidato):
    faixa_idade = get_faixa_etaria(idade, sexo)
    faixa_estatura = get_faixa_estatura(estatura, sexo)

    dados_detalhados = []
    aprovado_em_todos_oic = True
    pontuacao_total = 0.0

    testes_aplicaveis = ["C. Cintura", "FEMS", "FTSC", "Corrida 12 min"]

    for oic in testes_aplicaveis:
        valor = resultados_candidato.get(oic)
        if valor is None:
            pontos, min_b, max_b = 0.0, None, None
            status = "NÃO APTO"
            aprovado_em_todos_oic = False
        else:
            if oic == "C. Cintura":
                pontos, min_b, max_b = buscar_pontos_oic(oic, sexo, valor, faixa_estatura=faixa_estatura)
            else:
                pontos, min_b, max_b = buscar_pontos_oic(oic, sexo, valor, faixa_idade=faixa_idade)
            # An OIC is "NÃO APTO" (insatisfatório) if candidate is below or equal to I boundary (or above for cintura)
            if min_b is None:
                status = "NÃO APTO"
                aprovado_em_todos_oic = False
            else:
                if oic == "C. Cintura":
                    if valor > min_b:
                        status = "NÃO APTO"
                        aprovado_em_todos_oic = False
                    else:
                        status = "APTO"
                else:
                    if valor <= min_b:
                        status = "NÃO APTO"
                        aprovado_em_todos_oic = False
                    else:
                        status = "APTO"

        pontuacao_total += round(pontos,1)
        dados_detalhados.append({
            "Teste": TRADUCAO_CAMPOS[oic],
            "Resultado Candidato": valor if valor is not None else "-",
            "Pontos (peso aplicado)": round(pontos,1),
            "Pontos Máximos (peso)": OIC_WEIGHTS[oic],
            "Limite I (elim.)": min_b,
            "Limite E (ótimo)": max_b,
            "Situação": status
        })

    grau_final = round(pontuacao_total,1)

    # Conceituação global
    conceitacao = "I (Insatisfatório)"
    for k,(mn,mx) in CONCEITUACAO_GLOBAL.items():
        if mn <= grau_final <= mx:
            conceitacao = f"{k} ({mn:.1f}-{mx:.1f})"
            break

    if aprovado_em_todos_oic and grau_final >= PONTUACAO_MINIMA_APROVACAO:
        status_geral = "APTO"
        situacao_final = f"APROVADO: {conceitacao}"
    else:
        status_geral = "NÃO APTO"
        situacao_final = f"REPROVADO: {conceitacao}"

    return status_geral, situacao_final, grau_final, dados_detalhados, faixa_idade, faixa_estatura
