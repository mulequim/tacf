
# tacf_functions.py - Versão final usando JSONs extraídos do Anexo VI (NSCA 54-3)
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

# Official maxima per OIC (Anexo VI): OIC01=30, OIC02=30, OIC03=20, OIC04=20
OIC_MAX = {
    "C. Cintura": 30.0,
    "FEMS": 30.0,
    "FTSC": 20.0,
    "Corrida 12 min": 20.0
}

def _load_json(name):
    p = BASE_DIR / name
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

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
        if idade <= 20: return "≤20"
        if 21 <= idade <= 30: return "21–30"
        if 31 <= idade <= 34: return "31–34"
        if 35 <= idade <= 38: return "35–38"
        if 39 <= idade <= 41: return "39–41"
        if 42 <= idade <= 43: return "42–43"
        if 44 <= idade <= 49: return "44–49"
        if 50 <= idade <= 52: return "50–52"
        return "≥53"
    else:
        if idade <= 21: return "≤21"
        if 22 <= idade <= 25: return "22–25"
        if 26 <= idade <= 29: return "26–29"
        if 30 <= idade <= 33: return "30–33"
        if 34 <= idade <= 37: return "34–37"
        if 38 <= idade <= 41: return "38–41"
        if 42 <= idade <= 45: return "42–45"
        return "≥46"

def get_faixa_estatura(est, sexo):
    if sexo == "Masculino":
        if est <= 166: return "≤166"
        if 167 <= est <= 171: return "167–171"
        if 172 <= est <= 175: return "172–175"
        if 176 <= est <= 180: return "176–180"
        if 181 <= est <= 188: return "181–188"
        return "≥189"
    else:
        if est <= 161: return "≤161"
        if 162 <= est <= 166: return "162–166"
        return "≥167"

def _choose_table(oic, sexo):
    if oic == "C. Cintura":
        return OIC01_M if sexo == "Masculino" else OIC01_F
    if oic == "FEMS":
        return OIC02_M if sexo == "Masculino" else OIC02_F
    if oic == "FTSC":
        return OIC03_M if sexo == "Masculino" else OIC03_F
    if oic == "Corrida 12 min":
        return OIC04_M if sexo == "Masculino" else OIC04_F
    return {}

def _interp_points_cintura(valor, thresholds, max_points):
    # thresholds: dict with I, S_upper, B_upper, MB_upper, E_upper (numbers)
    # For cintura lower is better. If valor > I => 0; if valor <= E => max_points.
    if thresholds is None or not thresholds:
        return 0.0
    I = thresholds.get("I"); S = thresholds.get("S_upper"); B = thresholds.get("B_upper"); MB = thresholds.get("MB_upper"); E = thresholds.get("E_upper")
    # if valor > I -> 0
    if valor > I:
        return 0.0
    if valor <= E:
        return float(max_points)
    # Determine where between boundaries the valor sits; for cintura higher->worse, so invert mapping
    # Map ranges: I (worst) -> 0 ; S -> 0.25*max ; B -> 0.5*max ; MB -> 0.75*max ; E -> 1.0*max
    bounds = [I, S, B, MB, E]
    fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
    # Find interval where valor is between bounds[i] and bounds[i+1] (note bounds descending)
    for i in range(len(bounds)-1):
        hi = bounds[i]; lo = bounds[i+1]
        if lo < valor <= hi:
            # linear interpolate between hi(frac) and lo(frac)
            hi_frac = fracs[i]; lo_frac = fracs[i+1]
            if hi == lo:
                frac = lo_frac
            else:
                frac = hi_frac + (lo_frac - hi_frac) * (hi - valor) / (hi - lo)
            return round(frac * max_points, 2)
    return 0.0

def _interp_points_pos(valor, thresholds, max_points):
    # For measures where higher is better (FEMS, FTSC, Corrida)
    if thresholds is None or not thresholds:
        return 0.0
    I = thresholds.get("I"); S = thresholds.get("S_upper"); B = thresholds.get("B_upper"); MB = thresholds.get("MB_upper"); E = thresholds.get("E_upper")
    if valor <= I:
        return 0.0
    if valor >= E:
        return float(max_points)
    bounds = [I, S, B, MB, E]
    fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
    for i in range(len(bounds)-1):
        lo = bounds[i]; hi = bounds[i+1]
        if lo <= valor < hi:
            lo_frac = fracs[i]; hi_frac = fracs[i+1]
            if hi == lo:
                frac = lo_frac
            else:
                frac = lo_frac + (hi_frac - lo_frac) * (valor - lo) / (hi - lo)
            return round(frac * max_points, 2)
    return 0.0

def buscar_pontos_oic(oic_nome, sexo, valor_candidato, faixa_idade=None, faixa_estatura=None):
    tabela = _choose_table(oic_nome, sexo)
    if not tabela:
        return 0.0, None, None
    if oic_nome == "C. Cintura":
        faixa = faixa_estatura
    else:
        faixa = faixa_idade
    if faixa not in tabela:
        return 0.0, None, None
    thresholds = tabela[faixa]
    max_points = OIC_MAX[oic_nome]
    if oic_nome == "C. Cintura":
        pts = _interp_points_cintura(valor_candidato, thresholds, max_points)
    else:
        pts = _interp_points_pos(valor_candidato, thresholds, max_points)
    return pts, thresholds.get("I"), thresholds.get("E")

def calcular_resultado(sexo, idade, estatura, resultados_candidato):
    faixa_idade = get_faixa_etaria(idade, sexo)
    faixa_estatura = get_faixa_estatura(estatura, sexo)

    dados_detalhados = []
    aprovado_em_todos_oic = True
    pontuacao_total = 0.0

    testes = ["C. Cintura", "FEMS", "FTSC", "Corrida 12 min"]
    for oic in testes:
        val = resultados_candidato.get(oic)
        if val is None:
            pts, min_b, max_b = 0.0, None, None
            status = "NÃO APTO"
            aprovado_em_todos_oic = False
        else:
            if oic == "C. Cintura":
                pts, min_b, max_b = buscar_pontos_oic(oic, sexo, val, faixa_estatura=faixa_estatura)
                # elimination: if val > min_b => NOT APTO
                if min_b is None:
                    status = "NÃO APTO"; aprovado_em_todos_oic = False
                else:
                    status = "APTO" if val <= min_b else "NÃO APTO"
                    if status == "NÃO APTO":
                        aprovado_em_todos_oic = False
            else:
                pts, min_b, max_b = buscar_pontos_oic(oic, sexo, val, faixa_idade=faixa_idade)
                if min_b is None:
                    status = "NÃO APTO"; aprovado_em_todos_oic = False
                else:
                    status = "APTO" if val > min_b else "NÃO APTO"
                    if status == "NÃO APTO":
                        aprovado_em_todos_oic = False

        pontuacao_total += float(pts)
        dados_detalhados.append({
            "Teste": TRADUCAO_CAMPOS[oic],
            "Resultado Candidato": val if val is not None else "-",
            "Pontuação Candidato": round(float(pts),2),
            "Pontuação Máxima OIC": OIC_MAX[oic],
            "Limite I (elim.)": min_b,
            "Limite E (ótimo)": max_b,
            "Situação": status
        })

    grau_final = round(pontuacao_total,2)
    conceit = "I (Insatisfatório)"
    for k,(mn,mx) in CONCEITUACAO_GLOBAL.items():
        if mn <= grau_final <= mx:
            conceit = f"{k} ({mn:.1f}-{mx:.1f})"
            break
    if aprovado_em_todos_oic and grau_final >= PONTUACAO_MINIMA_APROVACAO:
        status_geral = "APTO"
        situacao_final = f"APROVADO: {conceit}"
    else:
        status_geral = "NÃO APTO"
        situacao_final = f"REPROVADO: {conceit}"
    return status_geral, situacao_final, grau_final, dados_detalhados, faixa_idade, faixa_estatura
