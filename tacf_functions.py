# tacf_functions.py
# Implementação alinhada com NSCA 54-3 (Anexo IV e VI) - versão funcional para M & F
# Nota: para manter o arquivo razoável coloquei trechos representativos das tabelas.
# Se quiser, eu faço um script para importar o Anexo VI inteiro a partir de CSV/JSON.

from bisect import bisect_right

TRADUCAO_CAMPOS = {
    "C. Cintura": "Circunferência da Cintura (cm)",
    "FEMS": "Flexão e Extensão dos M. Superiores (Repetições)",
    "FTSC": "Flexão do Tronco Sobre as Coxas (Repetições)",
    "Corrida 12 min": "Corrida 12 Minutos (Metros)",
}

# Conceituação global (Quadro 4 - Anexo IV)
CONCEITUACAO_GLOBAL = {
    "E": (90.0, 100.0),
    "MB": (70.0, 89.9),
    "B": (40.0, 69.9),
    "S": (20.0, 39.9),
    "I": (0.0, 19.9),
}

PONTUACAO_MINIMA_APROVACAO = 20.0  # necessária + S em todos os OIC

# ---------------------------
# Dados reduzidos de exemplo (trechos extraídos do Anexo VI)
# Para uso real recomenda-se carregar o Anexo VI completo via CSV/JSON.
# ---------------------------

# OIC 01 - Circunferência da Cintura: MATRIZES POR ESTATURA (masc)
# Formato: {estatura_faixa_label: {circ_cm: pontos}}
OIC_01_MASCULINO_PONTOS = {
    "≤ 166": {
        102.0: 0.0, 99.0: 0.0, 98.5: 6.0, 98.0: 6.4, 97.5: 6.7,
        97.0: 7.1, 96.5: 7.4, 96.0: 7.8, 95.5: 8.1, 95.0: 8.5,
        94.5: 8.8, 94.0: 9.2, 93.5: 9.5, 93.0: 9.9, 92.5: 10.2,
        92.0: 10.6, 91.5: 10.9, 91.0: 11.3, 90.5: 11.7, 90.0: 12.0,
        89.5: 13.3, 89.0: 14.6, 88.5: 15.9, 88.0: 17.1, 87.5: 18.4,
        87.0: 19.7, 86.5: 21.0, 86.0: 22.5, 85.5: 24.0, 85.0: 25.5,
        84.5: 27.0, 84.0: 27.8, 83.5: 28.2, 83.0: 28.6, 82.5: 30.0
    },
    "172-175": {
        # exemplo reduzido (preencha/importe o resto se quiser)
        99.0: 0.0, 98.5: 6.0, 87.5: 18.4, 86.5: 21.0, 85.0: 25.5, 82.5: 30.0
    },
    # adicione as demais faixas de estatura conforme o Anexo VI
}

# OIC 01 - Feminino (exemplo)
OIC_01_FEMININO_PONTOS = {
    "≤ 161": {
        92.0: 0.0, 89.5: 6.0, 89.0: 6.7, 88.5: 7.3, 88.0: 8.0, 87.5: 8.7,
        87.0: 9.3, 86.5: 10.0, 86.0: 10.7, 85.5: 11.3, 85.0: 12.0,
        84.5: 13.5, 84.0: 15.0, 83.5: 16.5, 83.0: 18.0, 82.5: 19.5,
        82.0: 21.0, 81.5: 23.0, 81.0: 25.0, 80.5: 27.0, 80.0: 27.8,
        79.5: 28.2, 79.0: 28.6, 78.5: 30.0
    },
    # adicione outras faixas (162-166, ≥167)
}

# OIC 02 - Flexões (masc) -> tabela representativa (repetições -> pontos por faixa etária)
# Estrutura: {faixa_etaria_label: {repeticoes: pontos}}
OIC_02_MASCULINO_PONTOS = {
    "≤ 20": {24: 0.0, 25: 2.0, 33: 4.0, 44: 7.0, 45: 8.0, 60: 10.0},
    "21-30": {21: 0.0, 22: 2.0, 30: 4.0, 41: 7.0, 42: 8.0, 58: 10.0},
    "31-34": {19: 0.0, 20: 2.0, 28: 4.0, 38: 7.0, 39: 8.0, 55: 10.0},
    # ... completar
}

# OIC 02 - Feminino (tabela representativa)
OIC_02_FEMININO_PONTOS = {
    "≤ 29": {16: 0.0, 17: 2.0, 25: 4.0, 34: 7.0, 35: 8.0, 41: 10.0},
    "30-40": {14: 0.0, 15: 2.0, 24: 4.0, 33: 7.0, 34: 8.0, 40: 10.0},
    # ... completar
}

# OIC 03 - Flexão do tronco (masc) - tabela reduzida (faixa etária -> repetições -> pontos)
OIC_03_MASCULINO_PONTOS = {
    "≤ 27": {36: 0.0, 37: 2.0, 44: 4.0, 54: 7.0, 55: 8.0, 62: 10.0},
    "28-30": {34: 0.0, 35: 2.0, 44: 4.0, 52: 7.0, 53: 8.0, 61: 10.0},
    # ... completar
}

# OIC 04 - Corrida 12 min (masc) - tabela reduzida (distância -> pontos por faixa etária)
OIC_04_MASCULINO_PONTOS = {
    "≤ 29": {2120: 
