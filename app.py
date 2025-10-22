import streamlit as st
import pandas as pd

# Dados dos índices mínimos de aprovação (Simplificados para "TACF Anual" - Baseado nos menores índices do EAOS/EIOS da NSCA 54-4 e incluindo a Circunferência da Cintura do EAT/EIT)
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

def calcular_resultado(tipo_exame, resultados_candidato):
    """
    Calcula se o candidato está APTO ou NÃO APTO com base nos índices mínimos.
    Também calcula a Nota Máxima Simulada.
    """
    indices_minimos = DADOS_INDICES.get(tipo_exame, {})
    resultados_avaliacao = {}
    aprovado_geral = True
    
    # Dicionários para armazenar os índices de Referência (Mínimo e Máximo Simulado)
    indices_referencia = {}
    
    # Fator de Simulação para "Nota Máxima" (30% acima do mínimo para exercícios)
    FATOR_MAXIMO_SIMULADO = 1.3
    
    # Processamento dos testes
    
    # 1. FEMS (Flexão e Extensão dos Membros Superiores)
    min_fems = indices_minimos.get("FEMS")
    res_fems = resultados_candidato.get("FEMS", 0)
    if min_fems is not None:
        max_fems = int(min_fems * FATOR_MAXIMO_SIMULADO)
        indices_referencia["FEMS"] = {"Mínimo": min_fems, "Máximo": max_fems}
        if res_fems >= min_fems:
            resultados_avaliacao["FEMS"] = "APTO" 
        else:
            resultados_avaliacao["FEMS"] = "NÃO APTO"
            aprovado_geral = False

    # 2. FTSC (Flexão do Tronco Sobre as Coxas)
    min_ftsc = indices_minimos.get("FTSC")
    res_ftsc = resultados_candidato.get("FTSC", 0)
    if min_ftsc is not None:
        max_ftsc = int(min_ftsc * FATOR_MAXIMO_SIMULADO)
        indices_referencia["FTSC"] = {"Mínimo": min_ftsc, "Máximo": max_ftsc}
        if res_ftsc >= min_ftsc:
            resultados_avaliacao["FTSC"] = "APTO"
        else:
            resultados_avaliacao["FTSC"] = "NÃO APTO"
            aprovado_geral = False

    # 3. Corrida 12 min
    min_corrida = indices_minimos.get("Corrida 12 min")
    res_corrida = resultados_candidato.get("Corrida 12 min", 0)
    if min_corrida is not None:
        max_corrida = int(min_corrida * FATOR_MAXIMO_SIMULADO)
        indices_referencia["Corrida 12 min"] = {"Mínimo": min_corrida, "Máximo": max_corrida}
        if res_corrida >= min_corrida:
            resultados_avaliacao["Corrida 12 min"] = "APTO"
        else:
            resultados_avaliacao["Corrida 12 min"] = "NÃO APTO"
            aprovado_geral = False
            
    # 4. Circunferência da Cintura (C. Cintura)
    max_cintura_minimo = indices_minimos.get("C. Cintura") # Este é o valor MÁXIMO aceitável para aprovação
    res_cintura = resultados_candidato.get("C. Cintura", 999.0)
    if max_cintura_minimo is not None:
        # Para C. Cintura, o "máximo" para aprovação é o valor mínimo da NSCA 54-4 (ex: 98.0 cm)
        # E a nota máxima simulada deve ser um valor ainda menor (idealmente, um valor de referência de "excelente")
        # Usaremos 5% abaixo do limite como "Nota Máxima" (o menor valor é o melhor)
        max_cintura_simulado = round(max_cintura_minimo * 0.95, 1) # Ex: 98.0 * 0.95 = 93.1 cm
        indices_referencia["C. Cintura"] = {"Mínimo": max_cintura_minimo, "Máximo": max_cintura_simulado} # Onde "Máximo" é o melhor resultado para C.Cintura
        
        if res_cintura <= max_cintura_minimo:
            resultados_avaliacao["C. Cintura"] = "APTO"
        else:
            resultados_avaliacao["C. Cintura"] = "NÃO APTO"
            aprovado_geral = False
            
    # Resultado final e Nota Geral
    resultado_final = "APTO GERAL" if aprovado_geral else "NÃO APTO GERAL"
    
    # Lógica da Nota Geral Simulada (10)
    atingiu_nota_maxima_simulada = True
    
    for k, v in resultados_avaliacao.items():
        if v == "NÃO APTO":
            atingiu_nota_maxima_simulada = False
            break # Não precisa verificar mais
            
        referencias = indices_referencia.get(k)
        if referencias:
            if k == "C. Cintura":
                # Para C. Cintura, o resultado deve ser MENOR ou IGUAL ao Máximo Simulado
                if resultados_candidato[k] > referencias["Máximo"]:
                    atingiu_nota_maxima_simulada = False
            else:
                # Para exercícios (FEMS, FTSC, Corrida), o resultado deve ser MAIOR ou IGUAL ao Máximo Simulado
                if resultados_candidato[k] < referencias["Máximo"]:
                    atingiu_nota_maxima_simulada = False
    
    if atingiu_nota_maxima_simulada and aprovado_geral:
        nota_geral = "APROVADO (Nota Máxima Simulada)"
    elif aprovado_geral:
        nota_geral = "APROVADO (Mínimo Atingido)"
    else:
        nota_geral = "REPROVADO"
    
    return resultado_final, nota_geral, resultados_avaliacao, indices_referencia, resultados_candidato

# --- Interface Streamlit ---

st.set_page_config(
    page_title="Calculadora TACF COMAER (NSCA 54-4)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Avaliação do Teste de Condicionamento Físico (TACF) COMAER")
st.subheader("Baseado nos Índices Mínimos da NSCA 54-4/2024 (Exames de Admissão)")
st.markdown("---")

# --- Lógica do Menu ---

st.sidebar.header("1. Seleção da Opção")
opcoes_base = ["TACF GERAL (Tabelas de Índices)", "Calcular TACF Anual (Simplificado)"]
opcao_selecionada = st.sidebar.radio("Escolha a funcionalidade:", opcoes_base)

st.sidebar.markdown("---")

if opcao_selecionada == "TACF GERAL (Tabelas de Índices)":
    
    st.header("TACF GERAL: Tabela de Índices Mínimos por Exame")
    st.markdown("Abaixo estão todos os índices mínimos de aprovação exigidos para os diferentes exames, cursos e estágios, conforme o Anexo VII da NSCA 54-4/2024.")

    # Reconstroi o DataFrame completo para a exibição (usando dados do Anexo VII original)
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

    df_geral_m = []
    df_geral_f = []
    
    for nome_exame, indices in DADOS_COMPLETOS_ANEXO_VII.items():
        if "(M)" in nome_exame:
            df_geral_m.append({
                "Exame/Estágio": nome_exame.replace(" (M)", ""),
                TRADUCAO_CAMPOS["FEMS"]: indices["FEMS"] if indices["FEMS"] is not None else "-",
                TRADUCAO_CAMPOS["FTSC"]: indices["FTSC"] if indices["FTSC"] is not None else "-",
                TRADUCAO_CAMPOS["SH"]: indices["SH"] if indices["SH"] is not None else "-",
                TRADUCAO_CAMPOS["Corrida 12 min"]: indices["Corrida 12 min"] if indices["Corrida 12 min"] is not None else "-",
                TRADUCAO_CAMPOS["C. Cintura"]: f"≤ {indices['C. Cintura']} cm" if indices["C. Cintura"] is not None else "-",
            })
        elif "(F)" in nome_exame:
            df_geral_f.append({
                "Exame/Estágio": nome_exame.replace(" (F)", ""),
                TRADUCAO_CAMPOS["FEMS"]: indices["FEMS"] if indices["FEMS"] is not None else "-",
                TRADUCAO_CAMPOS["FTSC"]: indices["FTSC"] if indices["FTSC"] is not None else "-",
                TRADUCAO_CAMPOS["SH"]: indices["SH"] if indices["SH"] is not None else "-",
                TRADUCAO_CAMPOS["Corrida 12 min"]: indices["Corrida 12 min"] if indices["Corrida 12 min"] is not None else "-",
                TRADUCAO_CAMPOS["C. Cintura"]: f"≤ {indices['C. Cintura']} cm" if indices["C. Cintura"] is not None else "-",
            })

    st.subheader("Índices Mínimos - Sexo MASCULINO")
    st.dataframe(pd.DataFrame(df_geral_m), hide_index=True, use_container_width=True)

    st.subheader("Índices Mínimos - Sexo FEMININO")
    st.dataframe(pd.DataFrame(df_geral_f), hide_index=True, use_container_width=True)

    st.caption("FEMS (Flexão e Extensão de Membros Superiores), FTSC (Flexão do Tronco Sobre as Coxas), SH (Salto Horizontal), C. Cintura (Circunferência da Cintura).")
    
else:
    # --- CALCULAR DESEMPENHO TACF ANUAL SIMPLIFICADO ---
    
    st.header("Calcular Desempenho no TACF Anual (Simplificado)")
    st.warning("⚠️ **AVISO: Base Normativa e Idade:** Esta ferramenta utiliza a **NSCA 54-4 (Exames de Admissão)**. Os índices mínimos **NÃO variam por Idade**. O cálculo de pontuação (Nota 10) é uma **Simulação**.")
    
    st.sidebar.header("2. Padrão e Idade")
    opcoes_exame = sorted(list(DADOS_INDICES.keys()))
    tipo_exame = st.sidebar.selectbox(
        "Selecione o Sexo/Padrão de Cálculo:",
        opcoes_exame,
        index=0 # Default para Masculino
    )
    
    # Campo Idade (apenas para referência, não afeta o cálculo APTO/NÃO APTO)
    idade_candidato = st.sidebar.number_input(
        "Idade do Candidato (Apenas para Referência)",
        min_value=16,
        value=25,
        step=1,
        help="A idade não altera os índices desta avaliação (NSCA 54-4)."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("3. Insira os Resultados")

    indices_necessarios = DADOS_INDICES[tipo_exame]

    resultados = {"Idade": idade_candidato}

    # Campos de entrada de dados
    for teste_curto, min_valor in indices_necessarios.items():
        if min_valor is not None:
            label = TRADUCAO_CAMPOS[teste_curto]
            
            # Define o valor inicial para o input
            if teste_curto == "C. Cintura":
                initial_value = min_valor - 1.0 
                step_val = 0.1
                input_format = "%.1f"
                help_text = f"Máximo permitido: {min_valor} cm."
            elif teste_curto == "Corrida 12 min":
                initial_value = int(min_valor)
                step_val = 10
                input_format = "%d"
                help_text = f"Mínimo exigido: {min_valor} m."
            else:
                initial_value = int(min_valor)
                step_val = 1
                input_format = "%d"
                help_text = f"Mínimo exigido: {min_valor} repetições."

            # Repetições, Distância ou Circunferência
            if teste_curto == "C. Cintura":
                resultados[teste_curto] = st.sidebar.number_input(
                    label,
                    min_value=0.0,
                    value=initial_value,
                    step=step_val,
                    format=input_format,
                    help=help_text
                )
            else:
                resultados[teste_curto] = st.sidebar.number_input(
                    label,
                    min_value=0,
                    value=initial_value,
                    step=step_val,
                    format=input_format,
                    help=help_text
                )
        
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Calcular Resultado do TACF"):
        # Execução do cálculo
        resultado_final, nota_geral, resultados_avaliacao, indices_referencia, resultados_candidato = calcular_resultado(tipo_exame, resultados)
        
        st.header("Resultado da Avaliação")
        
        # --- EXIBIÇÃO DA NOTA E STATUS GERAL ---
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Padrão de Cálculo", tipo_exame)
        col2.metric("Idade (Referência)", f"{idade_candidato} anos")
        
        if resultado_final == "APTO GERAL":
            col3.success(f"**STATUS GERAL: {resultado_final}**")
            st.balloons()
        else:
            col3.error(f"**STATUS GERAL: {resultado_final}**")

        st.markdown("---")
        
        st.subheader(f"Nota Final: {nota_geral}")
        if nota_geral == "REPROVADO":
            st.error("A reprovação em qualquer teste implica em 'NÃO APTO GERAL' (REPROVADO) no TACF.")
        elif nota_geral == "APROVADO (Nota Máxima Simulada)":
            st.success("Parabéns! Você atingiu o critério para a Nota Máxima Simulada.")
        
        st.markdown("---")
        st.subheader("Desempenho por Teste")
        
        # Prepara a lista de resultados e índices para exibição
        display_data = []
        for k in ["FEMS", "FTSC", "Corrida 12 min", "C. Cintura"]:
            if k in resultados_avaliacao:
                
                valor_limite_min = indices_referencia[k]["Mínimo"]
                valor_limite_max = indices_referencia[k]["Máximo"]
                valor_candidato = resultados_candidato.get(k)
                avaliacao = resultados_avaliacao[k]
                
                # Unidade e Texto de Referência
                if k == "C. Cintura":
                    unidade = "cm"
                    limite_texto = f"Mín. Aprovação: ≤ {valor_limite_min} {unidade} | Máx. Simulada: ≤ {valor_limite_max} {unidade}"
                    resultado_texto = f"{valor_candidato} {unidade}"
                elif k == "Corrida 12 min":
                    unidade = "m"
                    limite_texto = f"Mín. Aprovação: ≥ {valor_limite_min} {unidade} | Máx. Simulada: ≥ {valor_limite_max} {unidade}"
                    resultado_texto = f"{valor_candidato} {unidade}"
                else:
                    unidade = "repetições"
                    limite_texto = f"Mín. Aprovação: ≥ {valor_limite_min} {unidade} | Máx. Simulada: ≥ {valor_limite_max} {unidade}"
                    resultado_texto = f"{valor_candidato} {unidade}"
                
                display_data.append({
                    "Teste": TRADUCAO_CAMPOS[k],
                    "Resultado do Candidato": resultado_texto,
                    "Referência (Simulada)": limite_texto,
                    "Status": avaliacao
                })

        df_resultados = pd.DataFrame(display_data)
        
        # Cor da célula na tabela (usando estilo HTML/CSS para o Streamlit)
        def color_status(val):
            color = 'background-color: #d4edda; color: black' if val == 'APTO' else 'background-color: #f8d7da; color: black'
            return color
        
        st.dataframe(
            df_resultados.style.applymap(
                color_status, 
                subset=['Status']
            ),
            hide_index=True,
            use_container_width=True
        )

st.markdown("---")
st.caption("""
    **[span_0](start_span)NOTA SOBRE A SIMULAÇÃO:** A **NSCA 54-4** (base desta calculadora) apenas define o índice mínimo ("APTO")[span_0](end_span). A coluna "Máx. Simulada" foi criada para fins didáticos, representando um desempenho 30% superior ao mínimo (ou 5% inferior ao máximo no caso da C. Cintura), **NÃO sendo um valor oficial do COMAER** para a nota 10.
""")
