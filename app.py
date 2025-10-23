
import streamlit as st
import pandas as pd
from tacf_functions import calcular_resultado, TRADUCAO_CAMPOS

st.set_page_config(page_title="Calculadora TACF (NSCA 54-3) - Final", layout="wide")
st.title("Calculadora TACF - NSCA 54-3 (COMAER) - Masculino e Feminino")

st.sidebar.header("Dados Pessoais")
sexo = st.sidebar.selectbox("Sexo", ["Masculino", "Feminino"])
idade = st.sidebar.number_input("Idade", min_value=18, max_value=80, value=30)
estatura = st.sidebar.number_input("Estatura (cm)", min_value=140, max_value=210, value=175)

st.sidebar.markdown("---")
st.sidebar.header("Resultados (preencha os testes que realizou)")

fems = st.sidebar.number_input("FEMS (repetições)", min_value=0, value=20, step=1)
ftsc = st.sidebar.number_input("FTSC (repetições)", min_value=0, value=30, step=1)
corrida = st.sidebar.number_input("Corrida 12 min (metros)", min_value=0, value=2400, step=10)
cintura = st.sidebar.number_input("C. Cintura (cm)", min_value=0.0, value=90.0, step=0.1, format="%.1f")

resultados = {"FEMS": fems, "FTSC": ftsc, "Corrida 12 min": corrida, "C. Cintura": cintura}

if st.button("Calcular TACF"):
    status_geral, situacao_final, grau_final, dados_detalhados, faixa_idade, faixa_estatura = calcular_resultado(
        sexo, idade, estatura, resultados
    )
    st.subheader("Resumo")
    df_resumo = pd.DataFrame({
        "Critério": ["Grau Final", "Status Geral", "Conceituação Global"],
        "Resultado": [f"{grau_final:.1f} Pts", status_geral, situacao_final.split(': ')[1] if ':' in situacao_final else situacao_final]
    })
    st.table(df_resumo)

    st.markdown("### Detalhes por OIC")
    df_det = pd.DataFrame(dados_detalhados)
    st.dataframe(df_det, use_container_width=True)

    st.markdown("### Tabelas de Referência (Limites I e E) - Faixas usadas")
    st.caption(f"Faixa etária usada: {faixa_idade} — Faixa estatura usada: {faixa_estatura}")
    ref = df_det[["Teste", "Limite I (elim.)", "Limite E (ótimo)"]].rename(columns={
        "Teste": "OIC",
        "Limite I (elim.)": "Limite I (elim.)",
        "Limite E (ótimo)": "Limite E (ótimo)"
    })
    st.table(ref)

    if status_geral == "APTO":
        st.success("APTO — Parabéns!")
    else:
        st.error("NÃO APTO — Atenção aos OIC eliminatórios.")
