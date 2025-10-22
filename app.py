# app.py

import streamlit as st
import pandas as pd
from tacf_functions import (
    TRADUCAO_CAMPOS, 
    DADOS_COMPLETOS_ANEXO_VII, # Apenas para o TACF GERAL, que se mantém
    calcular_resultado,
    DADOS_INDICES, # Usado para os campos de entrada
    CONCEITUACAO_GLOBAL
)

# --- Interface Streamlit ---

st.set_page_config(
    page_title="Calculadora TACF COMAER (NSCA 54-3)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Avaliação do Teste de Condicionamento Físico (TACF) COMAER")
st.subheader("Baseado na NSCA 54-3/2024 (TACF Anual - Oficiais e Praças)")
st.markdown("---")

# --- Lógica do Menu ---

st.sidebar.header("1. Seleção da Opção")
opcoes_base = ["TACF GERAL (Tabelas de Índices - NSCA 54-4)", "Calcular TACF ANUAL (NSCA 54-3 - Pontuação Oficial)"]
opcao_selecionada = st.sidebar.radio("Escolha a funcionalidade:", opcoes_base)

st.sidebar.markdown("---")

if opcao_selecionada == "TACF GERAL (Tabelas de Índices - NSCA 54-4)":
    
    st.header("TACF GERAL: Tabela de Índices Mínimos por Exame (Base NSCA 54-4)")
    st.markdown("Esta tabela é baseada na **NSCA 54-4 (Exames de Admissão)** e mostra apenas o mínimo de aprovação por curso/estágio, **sem variação de idade ou pontuação**.")

    df_geral_m = []
    df_geral_f = []
    
    for nome_exame, indices in DADOS_COMPLETOS_ANEXO_VII.items():
        if "(M)" in nome_exame:
            df_geral_m.append({
                "Exame/Estágio": nome_exame.replace(" (M)", ""),
                TRADUCAO_CAMPOS["FEMS"]: indices["FEMS"] if indices["FEMS"] is not None else "-",
                TRADUCAO_CAMPOS["FTSC"]: indices["FTSC"] if indices["FTSC"] is not None else "-",
                "SH (Salto Horizontal)": indices["SH"] if indices["SH"] is not None else "-",
                TRADUCAO_CAMPOS["Corrida 12 min"]: indices["Corrida 12 min"] if indices["Corrida 12 min"] is not None else "-",
                TRADUCAO_CAMPOS["C. Cintura"]: f"≤ {indices['C. Cintura']} cm" if indices["C. Cintura"] is not None else "-",
            })
        elif "(F)" in nome_exame:
            df_geral_f.append({
                "Exame/Estágio": nome_exame.replace(" (F)", ""),
                TRADUCAO_CAMPOS["FEMS"]: indices["FEMS"] if indices["FEMS"] is not None else "-",
                TRADUCAO_CAMPOS["FTSC"]: indices["FTSC"] if indices["FTSC"] is not None else "-",
                "SH (Salto Horizontal)": indices["SH"] if indices["SH"] is not None else "-",
                TRADUCAO_CAMPOS["Corrida 12 min"]: indices["Corrida 12 min"] if indices["Corrida 12 min"] is not None else "-",
                TRADUCAO_CAMPOS["C. Cintura"]: f"≤ {indices['C. Cintura']} cm" if indices["Cintura"] is not None else "-",
            })

    st.subheader("Índices Mínimos - Sexo MASCULINO (NSCA 54-4)")
    st.dataframe(pd.DataFrame(df_geral_m), hide_index=True, use_container_width=True)

    st.subheader("Índices Mínimos - Sexo FEMININO (NSCA 54-4)")
    st.dataframe(pd.DataFrame(df_geral_f), hide_index=True, use_container_width=True)

    st.caption("A NSCA 54-4 trata apenas da aprovação mínima (APTO/NÃO APTO) para Exames de Admissão.")
    
else:
    # --- CALCULAR DESEMPENHO TACF ANUAL (NSCA 54-3) ---
    
    st.header("Calcular TACF ANUAL (NSCA 54-3)")
    st.warning("A avaliação abaixo utiliza a lógica da **NSCA 54-3** (Grau Final por somatório de pontos) e **CONSIDERA A IDADE** e **ESTATURA** para buscar as pontuações. Os dados de pontuação na demonstração são SIMPLIFICADOS para fins de prova de conceito.")
    
    st.sidebar.header("2. Dados Pessoais para Pontuação")
    
    col_s, col_i, col_e = st.sidebar.columns(3)
    
    tipo_exame = col_s.selectbox(
        "Sexo/Padrão:",
        sorted(list(DADOS_INDICES.keys())),
        index=0
    )
    sexo = "Masculino" if "MASCULINO" in tipo_exame else "Feminino"

    idade_candidato = col_i.number_input(
        "Idade:",
        min_value=18,
        max_value=60,
        value=30,
        step=1,
        help="Critério fundamental para as tabelas de pontuação da NSCA 54-3."
    )
    
    estatura_candidato = col_e.number_input(
        "Estatura (cm):",
        min_value=150,
        max_value=200,
        value=175,
        step=1,
        help="Necessário para a pontuação da Circunferência da Cintura (OIC 01/05)."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.header("3. Resultados dos Testes")

    indices_necessarios = DADOS_INDICES[tipo_exame]

    resultados = {
        "Idade": idade_candidato, 
        "Estatura": estatura_candidato
    }

    # Campos de entrada de dados
    for teste_curto in ["FEMS", "FTSC", "Corrida 12 min", "C. Cintura"]:
        if teste_curto in indices_necessarios:
            min_valor = indices_necessarios[teste_curto]
            label = TRADUCAO_CAMPOS[teste_curto]
            
            # Define o valor inicial para o input
            if teste_curto == "C. Cintura":
                initial_value = min_valor - 1.0 
                step_val = 0.1
                input_format = "%.1f"
            elif teste_curto == "Corrida 12 min":
                initial_value = int(min_valor)
                step_val = 10
                input_format = "%d"
            else:
                initial_value = int(min_valor)
                step_val = 1
                input_format = "%d"

            # Repetições, Distância ou Circunferência
            if teste_curto == "C. Cintura":
                resultados[teste_curto] = st.sidebar.number_input(
                    label,
                    min_value=0.0,
                    value=initial_value,
                    step=step_val,
                    format=input_format,
                    help=f"Medição da cintura (cm)."
                )
            else:
                resultados[teste_curto] = st.sidebar.number_input(
                    label,
                    min_value=0,
                    value=initial_value,
                    step=step_val,
                    format=input_format,
                    help=f"Número de repetições/metros."
                )
        
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Calcular Resultado Oficial NSCA 54-3"):
        # Execução do cálculo
        status_geral, situacao_final, grau_final, dados_detalhados, faixa_idade, faixa_estatura = calcular_resultado(
            sexo, idade_candidato, estatura_candidato, resultados
        )
        
        st.header("Resultado da Avaliação Oficial (NSCA 54-3)")
        
        # --- TABELA RESUMO GERAL ---
        st.subheader("Resumo da Situação e Grau Final")
        
        # Cria a tabela de resumo
        df_resumo = pd.DataFrame({
            "Critério": ["Grau Final (Soma dos Pontos)", "STATUS GERAL (Eliminatório)", "Conceituação Global"],
            "Resultado": [f"{grau_final:.1f} Pts", status_geral, situacao_final.split(": ")[1] if ":" in situacao_final else situacao_final],
            "Referência": ["Grau Mínimo p/ Aprovação: 20 Pts", "Aprovação Requer Grau Final ≥ 20 E APTO em todos os OIC", "I (0-19.9) | S (20-39.9) | B (40-69.9) | MB (70-89.9) | E (90-100)"]
        })
        
        # Define a cor para a Situação Final
        def color_situacao(val):
            if "APTO" in val:
                return 'background-color: #d4edda; color: black'
            elif "NÃO APTO" in val:
                return 'background-color: #f8d7da; color: black'
            return ''
        
        # Aplicar o estilo SOMENTE à célula STATUS GERAL (índice 1) na coluna 'Resultado'
        st.dataframe(
            df_resumo.style.applymap(
                color_situacao,
                subset=([1], ['Resultado']) 
            ),
            hide_index=True,
            use_container_width=True
        )
        
        # Exibe as faixas de referência (para fins de debug e clareza)
        st.caption(f"Faixa Etária de Pontuação (simulada): **{faixa_idade}**")
        st.caption(f"Faixa de Estatura de Pontuação (simulada): **{faixa_estatura}**")
        if status_geral == "APTO":
            st.balloons()

        st.markdown("---")
        
        # --- TABELA DE DESEMPENHO DETALHADO ---
        st.subheader("Pontuação Detalhada por OIC")
        
        df_resultados = pd.DataFrame(dados_detalhados)
        
        # Cor da célula na tabela
        def color_status_detalhe(val):
            color = 'background-color: #d4edda; color: black' if val == 'APTO' else 'background-color: #f8d7da; color: black'
            return color
        
        st.dataframe(
            df_resultados.style.applymap(
                color_status_detalhe, 
                subset=['Situação']
            ).format({
                'Pontuação Candidato': "{:.1f}",
                'Pontuação Mínima (S)': "{:.1f}",
                'Pontuação Máxima (E)': "{:.1f}",
            }),
            hide_index=True,
            use_container_width=True
        )

st.markdown("---")
st.caption("""
    **NOTA IMPORTANTE SOBRE A PONTUAÇÃO (NSCA 54-3):** As tabelas de pontuação (Anexo VI) são complexas, com variações por idade e altura.
    Nesta demonstração, as funções de busca (`buscar_pontos_oic`) utilizam **apenas um subconjunto de dados** das tabelas oficiais para provar a lógica de cálculo (Soma dos Pontos e Grau Final).
    Para uma calculadora oficial, seria necessária a transcrição completa de **todas** as tabelas do Anexo VI.
""")
