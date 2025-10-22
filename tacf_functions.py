# tacf_functions.py

# Dados dos índices mínimos de aprovação (Simplificados para "TACF Anual" - Baseado nos menores índices do EAOS/EIOS da NSCA 54-4 e incluindo a Circunferência da Cintura do EAT/EIT)
# NOTA: Estes índices são de APTO MÍNIMO e NÃO variam por IDADE na NSCA 54-4.
DADOS_INDICES = {
    # Usando índices do EAOS/EIOS + C. Cintura do EAT/EIT (Grad. Ed. Física)
    "TACF ANUAL MASCULINO (Base EAOS/EIOS)": {
        "FEMS": 11, "FTSC": 20, "SH": None, "Corrida 12 min": 1890, "C. Cintura": 98.0 
    },
    "TACF ANUAL FEMININO (Base EAOS/EIOS)": {
        "FEMS": 9, "FTSC": 11, "SH": None, "Corrida 12 min": 1540, "C. Cintura": 89.0
    },
}

# Tradução dos campos para exibição
TRADUCAO_CAMPOS = {
    "FEMS": "Flexão e Extensão dos M. Superiores (Repetições)",
    "FTSC": "Flexão do Tronco Sobre as Coxas (Repetições)",
    "SH": "Salto Horizontal (Metros)",
    "Corrida 12 min": "Corrida 12 Minutos (Metros)",
    "C. Cintura": "Circunferência da Cintura (cm)",
}

# Dados Completos para a Tabela Geral (Exibição)
DADOS_COMPLETOS_ANEXO_VII = {
    # --- MASCULINO ---
    "CFOAV, CFOINT, CFOINF, CFS, CFT e EAGS (M)": {"FEMS": 26, "FTSC": 42, "SH": 1.8, "Corrida 12 min": 2250, "C. Cintura": None},
    "CAMAR, CADAR, CAFAR, EAOEAR, EAOT, CFOE, EIAC e EAOAP (M)": {"FEMS": 21, "FTSC": 34, "SH": None, "Corrida 12 min": 2200, "C. Cintura": None},
    "CPCAR (M)": {"FEMS": 21, "FTSC": 38, "SH": None, "Corrida 12 min": 2050, "C. Cintura": None},
    "EAOF (M)": {"FEMS": 17, "FTSC": 27, "SH": None, "Corrida 12 min": 2050, "C. Cintura": None},
    "EAT e EIT (Grad. Ed. Física) e EIT (Seg. e Defesa) (M)": {"FEMS": 19, "FTSC": 35, "SH": None, "Corrida 12 min": 2100, "C. Cintura": 98.0},
    "EAT, EIT, EAS, EIS, EAP, EIP e EAP CB (M)": {"FEMS": 13, "FTSC": 25, "SH": None, "Corrida 12 min": 1900, "C. Cintura": None},
    "EAOS e EIOS (M)": {"FEMS": 11, "FTSC": 20, "SH": None, "Corrida 12 min": 1890, "C. Cintura": None},
    # --- FEMININO ---
    "CFOAV, CFOINT, CFOINF, CFS, CFT e EAGS (F)": {"FEMS": 16, "FTSC": 34, "SH": 1.4, "Corrida 12 min": 1850, "C. Cintura": None},
    "CAMAR, CADAR, CAFAR, EAOEAR, EAOT, CFOE, EIAC e EAOAP (F)": {"FEMS": 12, "FTSC": 29, "SH": None, "Corrida 12 min": 1650, "C. Cintura": None},
    "CPCAR (F)": {"FEMS": 13, "FTSC": 30, "SH": None, "Corrida 12 min": 1650, "C. Cintura": None},
    "EAOF (F)": {"FEMS": 17, "FTSC": 18, "SH": None, "Corrida 12 min": 1650, "C. Cintura": None},
    "EAT e EIT (Grad. Ed. Física) (F)": {"FEMS": 17, "FTSC": 31, "SH": None, "Corrida 12 min": 1710, "C. Cintura": 89.0},
    "EAT, EIT, EAS, EIS, EAP, EIP e EAP CB (F)": {"FEMS": 9, "FTSC": 15, "SH": None, "Corrida 12 min": 1600, "C. Cintura": None},
    "EAOS e EIOS (F)": {"FEMS": 9, "FTSC": 11, "SH": None, "Corrida 12 min": 1540, "C. Cintura": None},
}


def calcular_resultado(tipo_exame, resultados_candidato):
    """
    Calcula se o candidato está APTO ou NÃO APTO com base nos índices mínimos.
    Também calcula a Nota Máxima Simulada e a Pontuação Geral.
    """
    indices_minimos = DADOS_INDICES.get(tipo_exame, {})
    resultados_avaliacao = {}
    aprovado_geral = True
    
    # Dicionários para armazenar os índices de Referência (Mínimo e Máximo Simulado)
    indices_referencia = {}
    
    # Fator de Simulação para "Nota Máxima" (30% acima do mínimo para exercícios)
    FATOR_MAXIMO_SIMULADO = 1.3
    
    # Pontuação Total
    pontuacao_total = 0.0
    pontuacao_maxima_possivel = 0.0
    
    # Processamento dos testes
    
    for teste_curto, min_valor in indices_minimos.items():
        if min_valor is None:
            continue
            
        pontuacao_maxima_possivel += 100.0
        # Use .get() para valores numéricos e forneça um valor padrão apropriado (0 ou 0.0)
        valor_candidato = resultados_candidato.get(teste_curto, 0.0 if teste_curto == "C. Cintura" else 0) 
        
        # 1. Define Mínimo e Máximo Simulado
        if teste_curto == "C. Cintura":
            min_aprovacao = min_valor 
            max_simulado = round(min_aprovacao * 0.95, 1) # Mínimo para Nota Máxima (5% abaixo)
        else:
            min_aprovacao = min_valor
            max_simulado = int(min_aprovacao * FATOR_MAXIMO_SIMULADO)
            
        indices_referencia[teste_curto] = {"Mínimo": min_aprovacao, "Máximo": max_simulado, "Pontuação Candidato": 0.0}
        
        # 2. Avaliação APTO/NÃO APTO (Critério Eliminatório)
        if teste_curto == "C. Cintura":
            if valor_candidato <= min_aprovacao:
                resultados_avaliacao[teste_curto] = "APTO"
            else:
                resultados_avaliacao[teste_curto] = "NÃO APTO"
                aprovado_geral = False
        else:
            if valor_candidato >= min_aprovacao:
                resultados_avaliacao[teste_curto] = "APTO"
            else:
                resultados_avaliacao[teste_curto] = "NÃO APTO"
                aprovado_geral = False
        
        # 3. Cálculo da Pontuação Individual (Se for APTO)
        if resultados_avaliacao[teste_curto] == "APTO":
            ponto_min = min_aprovacao
            ponto_max = max_simulado
            
            if teste_curto == "C. Cintura":
                # C. Cintura: Menor valor é melhor. Pontuação de 50 (Mínimo) a 100 (Máximo Simulado)
                if valor_candidato <= ponto_max:
                    pontuacao_teste = 100.0
                else:
                    # Calcula a progressão linear de 50 a 100
                    pontuacao_teste = 50.0 + (50.0 * (ponto_min - valor_candidato) / (ponto_min - ponto_max))
                    pontuacao_teste = max(50.0, min(100.0, pontuacao_teste))
            else:
                # Exercícios: Maior valor é melhor. Pontuação de 50 (Mínimo) a 100 (Máximo Simulado)
                if valor_candidato >= ponto_max:
                    pontuacao_teste = 100.0
                else:
                    # Calcula a progressão linear de 50 a 100
                    pontuacao_teste = 50.0 + (50.0 * (valor_candidato - ponto_min) / (ponto_max - ponto_min))
                    pontuacao_teste = max(50.0, min(100.0, pontuacao_teste))

            indices_referencia[teste_curto]["Pontuação Candidato"] = pontuacao_teste
            pontuacao_total += pontuacao_teste

    # 4. Resultado Final e Nota Geral
    resultado_final = "APTO GERAL" if aprovado_geral else "NÃO APTO GERAL"
    
    if resultado_final == "NÃO APTO GERAL":
        pontuacao_geral_final = 0.0
        nota_geral = "REPROVADO"
    else:
        # Média da pontuação dos testes (Máximo 100 Pts)
        pontuacao_geral_final = pontuacao_total / len(resultados_avaliacao) if len(resultados_avaliacao) > 0 else 0.0
        
        if pontuacao_geral_final >= 90:
            nota_geral = "EXCELENTE (Nota Máxima Simulada)"
        elif pontuacao_geral_final >= 70:
            nota_geral = "BOM"
        else:
            nota_geral = "REGULAR (Mínimo Atingido)"
    
    return resultado_final, nota_geral, pontuacao_geral_final, resultados_avaliacao, indices_referencia, resultados_candidato
