import streamlit as st
import pandas as pd

# Dados dos índices mínimos de aprovação (Extraídos do Anexo VII da NSCA 54-4)
# Os índices são por sexo e por tipo de exame/curso/estágio.
# A idade não é um critério de variação para os índices mínimos desta norma.
DADOS_INDICES = {
    # --- MASCULINO ---
    "CFOAV, CFOINT, CFOINF, CFS, CFT e EAGS (M)": {
        "FEMS": 26, "FTSC": 42, "SH": 1.8, "Corrida 12 min": 2250, "C. Cintura": None
    },
    "CAMAR, CADAR, CAFAR, EAOEAR, EAOT, CFOE, EIAC e EAOAP (M)": {
        "FEMS": 21, "FTSC": 34, "SH": None, "Corrida 12 min": 2200, "C. Cintura": None
    },
    "CPCAR (M)": {
        "FEMS": 21, "FTSC": 38, "SH": None, "Corrida 12 min": 2050, "C. Cintura": None
    },
    "EAOF (M)": {
        "FEMS": 17, "FTSC": 27, "SH": None, "Corrida 12 min": 2050, "C. Cintura": None
    },
    "EAT e EIT (Grad. Ed. Física) e EIT (Seg. e Defesa) (M)": {
        "FEMS": 19, "FTSC": 35, "SH": None, "Corrida 12 min": 2100, "C. Cintura": 98.0
    },
    "EAT, EIT, EAS, EIS, EAP, EIP e EAP CB (M)": {
        "FEMS": 13, "FTSC": 25, "SH": None, "Corrida 12 min": 1900, "C. Cintura": None
    },
    "EAOS e EIOS (M)": {
        "FEMS": 11, "FTSC": 20, "SH": None, "Corrida 12 min": 1890, "C. Cintura": None
    },
    
    # --- FEMININO ---
    "CFOAV, CFOINT, CFOINF, CFS, CFT e EAGS (F)": {
        "FEMS": 16, "FTSC": 34, "SH": 1.4, "Corrida 12 min": 1850, "C. Cintura": None
    },
    "CAMAR, CADAR, CAFAR, EAOEAR, EAOT, CFOE, EIAC e EAOAP (F)": {
        "FEMS": 12, "FTSC": 29, "SH": None, "Corrida 12 min": 1650, "C. Cintura": None
    },
    "CPCAR (F)": {
        "FEMS": 13, "FTSC": 30, "SH": None, "Corrida 12 min": 1650, "C. Cintura": None
    },
    "EAOF (F)": {
        "FEMS": 17, "FTSC": 18, "SH": None, "Corrida 12 min": 1650, "C. Cintura": None
    },
    "EAT e EIT (Grad. Ed. Física) (F)": {
        "FEMS": 17, "FTSC": 31, "SH": None, "Corrida 12 min": 1710, "C. Cintura": 89.0
    },
    "EAT, EIT, EAS, EIS, EAP, EIP e EAP CB (F)": {
        "FEMS": 9, "FTSC": 15, "SH": None, "Corrida 12 min": 1600, "C. Cintura": None
    },
    "EAOS e EIOS (F)": {
        "FEMS": 9, "FTSC": 11, "SH": None, "Corrida 12 min": 1540, "C. Cintura": None
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
    
    A avaliação segue o critério da NSCA 54-4: APTO (alcançar o mínimo) ou NÃO APTO (não alcançar).
    """
    indices_minimos = DADOS_INDICES.get(tipo_exame, {})
    resultados_avaliacao = {}
    aprovado_geral = True
    
    # 1. FEMS (Flexão e Extensão dos Membros Superiores)
    min_fems = indices_minimos.get("FEMS")
    res_fems = resultados_candidato["FEMS"]
    if min_fems is not None:
        if res_fems >= min_fems:
            resultados_avaliacao["FEMS"] = f"APTO ({res_fems} Repetições)"
        else:
            resultados_avaliacao["FEMS"] = f"NÃO APTO ({res_fems} Repetições). Mínimo exigido: {min_fems}."
            aprovado_geral = False

    # 2. FTSC (Flexão do Tronco Sobre as Coxas)
    min_ftsc = indices_minimos.get("FTSC")
    res_ftsc = resultados_candidato["FTSC"]
    if min_ftsc is not None:
        if res_ftsc >= min_ftsc:
            resultados_avaliacao["FTSC"] = f"APTO ({res_ftsc} Repetições)"
        else:
            resultados_avaliacao["FTSC"] = f"NÃO APTO ({res_ftsc} Repetições). Mínimo exigido: {min_ftsc}."
            aprovado_geral = False

    # 3. SH (Salto Horizontal)
    min_sh = indices_minimos.get("SH")
    res_sh = resultados_candidato["SH"]
    if min_sh is not None:
        if res_sh >= min_sh:
            resultados_avaliacao["SH"] = f"APTO ({res_sh} m)"
        else:
            resultados_avaliacao["SH"] = f"NÃO APTO ({res_sh} m). Mínimo exigido: {min_sh} m."
            aprovado_geral = False

    # 4. Corrida 12 min
    min_corrida = indices_minimos.get("Corrida 12 min")
    res_corrida = resultados_candidato["Corrida 12 min"]
    if min_corrida is not None:
        if res_corrida >= min_corrida:
            resultados_avaliacao["Corrida 12 min"] = f"APTO ({res_corrida} m)"
        else:
            resultados_avaliacao["Corrida 12 min"] = f"NÃO APTO ({res_corrida} m). Mínimo exigido: {min_corrida} m."
            aprovado_geral = False

    # 5. Circunferência da Cintura (C. Cintura)
    # Importante: O índice é o MÁXIMO (<=).
    max_cintura = indices_minimos.get("C. Cintura")
    res_cintura = resultados_candidato["C. Cintura"]
    if max_cintura is not None:
        if res_cintura <= max_cintura:
            resultados_avaliacao["C. Cintura"] = f"APTO ({res_cintura} cm)"
        else:
            resultados_avaliacao["C. Cintura"] = f"NÃO APTO ({res_cintura} cm). Máximo permitido: {max_cintura} cm."
            aprovado_geral = False
            
    # Resultado final
    resultado_final = "APTO" if aprovado_geral else "NÃO APTO"
    
    return resultado_final, resultados_avaliacao, indices_minimos

# --- Interface Streamlit ---

st.set_page_config(
    page_title="Calculadora TACF COMAER (NSCA 54-4)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Avaliação do Teste de Condicionamento Físico (TACF) COMAER")
st.subheader("Baseado na NSCA 54-4/2024 (Índices Mínimos de Aprovação)")
st.markdown("---")

# Seleção do Exame
st.sidebar.header("1. Selecione o Exame/Estágio")
opcoes_exame = sorted(list(DADOS_INDICES.keys()))
tipo_exame = st.sidebar.selectbox(
    "Tipo de Exame/Estágio",
    opcoes_exame,
    index=opcoes_exame.index("CFOAV, CFOINT, CFOINF, CFS, CFT e EAGS (M)") # Default
)

st.sidebar.markdown("---")
st.sidebar.header("2. Insira os Resultados")

# Obter os índices mínimos para o exame selecionado (para saber quais testes solicitar)
indices_necessarios = DADOS_INDICES[tipo_exame]

resultados = {}

# Campos de entrada de dados
for teste_curto, min_valor in indices_necessarios.items():
    if min_valor is not None:
        label = TRADUCAO_CAMPOS[teste_curto]
        
        if teste_curto in ["FEMS", "FTSC"]:
            # Repetições (número inteiro)
            resultados[teste_curto] = st.sidebar.number_input(
                label,
                min_value=0,
                value=min_valor,
                step=1,
                help=f"Mínimo exigido: {min_valor} repetições."
            )
        elif teste_curto == "Corrida 12 min":
            # Distância em metros (número inteiro)
            resultados[teste_curto] = st.sidebar.number_input(
                label,
                min_value=0,
                value=min_valor,
                step=10,
                help=f"Mínimo exigido: {min_valor} metros."
            )
        elif teste_curto == "SH":
            # Salto Horizontal (número decimal para metros)
            # O documento usa '1,8 m' e '1,4 m', então usaremos float.
            resultados[teste_curto] = st.sidebar.number_input(
                label,
                min_value=0.0,
                value=min_valor,
                step=0.1,
                format="%.2f",
                help=f"Mínimo exigido: {min_valor} metros."
            )
        elif teste_curto == "C. Cintura":
            # Circunferência da Cintura (número decimal para cm)
            # O documento usa '≤ 98,0 cm' e '≤ 89,0 cm'.
            resultados[teste_curto] = st.sidebar.number_input(
                label,
                min_value=0.0,
                value=min_valor - 1.0, # Valor um pouco abaixo do máximo para iniciar
                step=0.1,
                format="%.1f",
                help=f"Máximo permitido: {min_valor} cm."
            )

st.sidebar.markdown("---")

if st.sidebar.button("Calcular Resultado do TACF"):
    # Execução do cálculo
    resultado_final, resultados_avaliacao, indices_minimos = calcular_resultado(tipo_exame, resultados)
    
    st.header("Resultado da Avaliação")
    
    # Exibir o resultado final
    if resultado_final == "APTO":
        st.success(f"**Resultado Final: {resultado_final}**")
        st.balloons()
    else:
        st.error(f"**Resultado Final: {resultado_final}**")
        st.warning("O candidato não atingiu o índice mínimo exigido em um ou mais testes. Lembre-se que o critério é *APTO* ou *NÃO APTO* (NSCA 54-4/2024).")

    st.markdown("---")
    st.subheader("Desempenho por Teste")
    
    # Exibir o desempenho detalhado
    df_resultados = pd.DataFrame({
        "Teste": [TRADUCAO_CAMPOS.get(k) for k in resultados_avaliacao.keys()],
        "Resultado do Candidato": [v.split(" ")[1] for v in resultados_avaliacao.values()],
        "Índice Mínimo/Máximo": [
            f"{indices_minimos.get(k)} " + ("cm" if k == "C. Cintura" else ("m" if k in ["SH", "Corrida 12 min"] else "repetições"))
            for k in resultados_avaliacao.keys()
        ],
        "Avaliação": [v.split(" ")[0] for v in resultados_avaliacao.values()]
    })
    
    # Cor da célula na tabela (usando estilo HTML/CSS para o Streamlit)
    def color_status(val):
        color = 'background-color: #d4edda' if val == 'APTO' else 'background-color: #f8d7da'
        return color
    
    st.dataframe(
        df_resultados.style.applymap(
            color_status, 
            subset=['Avaliação']
        ),
        hide_index=True,
        use_container_width=True
    )

st.markdown("---")
st.caption("""
    **Observação sobre a avaliação (NSCA 54-4):** Esta calculadora utiliza apenas os critérios oficiais de **APTO** ou **NÃO APTO**
    (atingir ou não o índice mínimo). O documento fornecido **não** estabelece pontuações ou categorias de desempenho (como 'Bom', 'Excelente', etc.)
    acima dos mínimos exigidos.

    **Fontes:**
    * NSCA 54-4/2024, Anexo VII (Índices Mínimos de Aprovação)
    * NSCA 54-4/2024, Art. 18 (Condições de Aprovação)
""")
