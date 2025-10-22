# tacf_functions.py

# DADOS OFICIAIS NSCA 54-3 (TACF ANUAL DO EFETIVO)
# NOTA: O dicionário completo com todas as faixas etárias/alturas é extenso.
# Incluiremos APENAS um pequeno exemplo de dados e a estrutura de busca.

TRADUCAO_CAMPOS = {
    "C. Cintura": "Circunferência da Cintura (cm)",
    "FEMS": "Flexão e Extensão dos M. Superiores (Repetições)",
    "FTSC": "Flexão do Tronco Sobre as Coxas (Repetições)",
    "Corrida 12 min": "Corrida 12 Minutos (Metros)",
}

# Estrutura para os testes de resistência (dependem de IDADE)
# Exemplo de dados: OIC 02 - MASCULINO (Baseado nas repetições e Faixa Etária)
# Formato: {Faixa Etária: {Pontos: Valor Mínimo para Pontuação}}
OIC_02_MASCULINO_PONTOS = {
    "≤ 20": {0.0: 24, 2.0: 25, 10.0: 60}, # Exemplo: 25 rep = 2.0 pts
    "21-30": {0.0: 21, 2.0: 22, 10.0: 58},
    "31-34": {0.0: 19, 2.0: 20, 10.0: 55},
    # ... aqui viriam todas as outras faixas etárias
}

# Estrutura para C. Cintura (depende de ALTURA e valor MEDIDO)
# Exemplo de dados: OIC 01 - MASCULINO (Baseado na Circunferência e Estatura)
# Formato: {Estatura: {Circunferência: Pontos}}
OIC_01_MASCULINO_PONTOS = {
    "≤ 166": {99.0: 0.0, 98.5: 6.0, 82.5: 30.0}, # Exemplo: 98.5 cm = 6.0 pts
    "172-175": {99.0: 0.0, 98.5: 6.0, 87.5: 18.4, 86.5: 21.0, 85.0: 25.5, 82.5: 30.0},
    # ... aqui viriam todas as outras faixas de altura
}

# Critérios para Apreciação de Suficiência (Conceituação Global)
CONCEITUACAO_GLOBAL = {
    "E": [90.0, 100.0],  # Excelente
    "MB": [70.0, 89.9], # Muito Bom
    "B": [40.0, 69.9],  # Bom
    "S": [20.0, 39.9],  # Satisfatório
    "I": [0.0, 19.9],   # Insatisfatório
}

# Critérios para APTO/NÃO APTO (Mínimo em "Satisfatório")
# A pontuação MÍNIMA para APTO é 20.0 (Grau Final) E Satisfatório (S) em TODOS os OIC.
PONTUACAO_MINIMA_APROVACAO = 20.0

# --- FUNÇÕES DE BUSCA ---

def get_faixa_etaria(idade, sexo):
    """Função de exemplo para obter a faixa etária correta para os testes."""
    # Como as faixas etárias variam por teste, simplificaremos aqui para fins de demonstração
    # Em um sistema completo, essa lógica seria complexa.
    if sexo == "Masculino":
        if idade <= 30: return "21-30"
        if idade <= 38: return "35-38"
        if idade >= 53: return "≥ 53"
        return "Faixa Padrão M"
    else:
        if idade <= 29: return "≤ 29"
        if idade >= 45: return "≥ 45"
        return "Faixa Padrão F"

def get_faixa_estatura(estatura):
    """Função de exemplo para obter a faixa de estatura para C. Cintura."""
    if estatura <= 166: return "≤ 166"
    if estatura <= 175: return "172-175"
    return "176-180" # Exemplo simplificado

def buscar_pontos_oic(oic_nome, sexo, valor_candidato, faixa_idade=None, faixa_estatura=None):
    """
    Função (simplificada) para buscar a pontuação oficial do candidato.
    Em um sistema real, esta função faria interpolação linear ou busca precisa.
    """
    if oic_nome == "C. Cintura":
        tabela = OIC_01_MASCULINO_PONTOS if sexo == "Masculino" else {}
        faixa = faixa_estatura
        # Para C. Cintura, procuramos o valor mais próximo igual ou INFERIOR ao do candidato
        if faixa in tabela:
            for circ, pontos in sorted(tabela[faixa].items()):
                if valor_candidato <= circ:
                    return pontos, max(tabela[faixa].keys()) # Retorna Pontos e o limite MÁXIMO de aprovação
            return 0.0, max(tabela[faixa].keys())
        return 0.0, 999.0 
        
    else: # FEMS, FTSC, Corrida 12 min
        tabela = OIC_02_MASCULINO_PONTOS if sexo == "Masculino" and oic_nome == "FEMS" else {}
        faixa = faixa_idade
        # Para Exercícios, procuramos o valor mais próximo igual ou INFERIOR ao do candidato
        if faixa in tabela:
            # Converte a lista de pontos para ser fácil de buscar
            pontos_possiveis = sorted(tabela[faixa].keys(), reverse=True)
            
            # 1. Tenta achar o ponto exato ou o ponto mais alto não ultrapassado
            for ponto, min_rep in tabela[faixa].items():
                if valor_candidato >= min_rep:
                    # Em um sistema real, faria interpolação aqui. Para o exemplo, pegamos o ponto mais alto.
                    return 10.0, 10.0 # Simplifica: se atingiu o mínimo de 10.0, retorna 10.0.
            
            # Se não atingiu o mínimo para 2.0 pontos (I), retorna 0.0
            return 0.0, 10.0 
        return 0.0, 10.0 # Ponto máximo 10.0

def calcular_resultado(sexo, idade, estatura, resultados_candidato):
    """
    Calcula o Grau Final e a Conceituação Global usando os critérios oficiais da NSCA 54-3.
    """
    
    faixa_idade = get_faixa_etaria(idade, sexo)
    faixa_estatura = get_faixa_estatura(estatura)
    
    # 1. Coleta de Dados e Cálculo de Pontuação
    dados_detalhados = []
    aprovado_em_todos_oic = True
    pontuacao_total = 0.0
    
    # Simula quais testes são aplicáveis para o nosso exemplo simplificado
    testes_aplicaveis = [k for k in TRADUCAO_CAMPOS.keys()]
    
    for oic_nome in testes_aplicaveis:
        
        valor_candidato = resultados_candidato.get(oic_nome)
        
        # Busca a Pontuação e o limite MÁXIMO de aprovação (I -> S)
        if oic_nome in ["FEMS", "FTSC", "Corrida 12 min"]:
            pontuacao_candidato, pontuacao_maxima_oic = buscar_pontos_oic(oic_nome, sexo, valor_candidato, faixa_idade=faixa_idade)
        elif oic_nome == "C. Cintura":
             pontuacao_candidato, limite_max_aprovacao = buscar_pontos_oic(oic_nome, sexo, valor_candidato, faixa_estatura=faixa_estatura)
             pontuacao_maxima_oic = 10.0 # O máximo possível para este OIC é 30.0 no Anexo VI, mas usaremos 10.0 para simplificar a média
        else:
            continue

        # Verifica se atingiu o mínimo para o conceito "Satisfatório" (que é o limite de 0.0 pts)
        status_aprovacao = "APTO" if pontuacao_candidato > 0.0 else "NÃO APTO"
        if status_aprovacao == "NÃO APTO":
            aprovado_em_todos_oic = False
        
        pontuacao_total += pontuacao_candidato

        dados_detalhados.append({
            "Teste": TRADUCAO_CAMPOS[oic_nome],
            "Pontuação Mínima (S)": 0.0, # Em um sistema real, seria o valor do limite 'S' da tabela
            "Pontuação Máxima (E)": 10.0, # Simplificado para 10.0
            "Resultado Candidato": valor_candidato,
            "Pontuação Candidato": pontuacao_candidato,
            "Situação": status_aprovacao
        })

    # 2. Cálculo do Grau Final e Conceituação Global
    num_oic = len(testes_aplicaveis)
    grau_final = pontuacao_total
    
    # 3. Definição da Conceituação Global e Status Final
    conceituacao_global = "I (Insatisfatório)"
    for conceito, (min_grau, max_grau) in CONCEITUACAO_GLOBAL.items():
        if min_grau <= grau_final <= max_grau:
            conceituacao_global = f"{conceito} ({min_grau:.1f} - {max_grau:.1f})"
            break

    # 4. Situação Final
    # Serão considerados APTOS (A) os militares que obtiverem Grau Final >= 20 E Satisfatório (S) em todos os OIC.
    if aprovado_em_todos_oic and grau_final >= PONTUACAO_MINIMA_APROVACAO:
        status_geral = "APTO"
        situacao_final = f"APROVADO: {conceituacao_global}"
    else:
        status_geral = "NÃO APTO"
        situacao_final = f"REPROVADO: {conceituacao_global}"
        
    return status_geral, situacao_final, grau_final, dados_detalhados, faixa_idade, faixa_estatura
