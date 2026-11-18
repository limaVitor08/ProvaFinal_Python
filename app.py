import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_excel("saeb_aprendizado_territorios-7-2023-EM.xlsx",
sheet_name="estados", engine="openpyxl")


ARQUIVO = "saeb_aprendizado_territorios-7-2023-EM.xlsx"

@st.cache_data
def carregar(caminho):
    if caminho.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(caminho) 
    for sep in [";", ","]:
        for enc in ["utf-8", "latin-1"]:
            try:
                d = pd.read_csv(caminho, sep=sep, encoding=enc, decimal=",")
                if d.shape[1] > 1:
                    return d
            except Exception:
                pass
    return pd.read_csv(caminho)

df = carregar(ARQUIVO)
df.columns = df.columns.str.strip()              

for col in ["uf", "lingua portuguesa adequado", "matematica adequado", "lingua portuguesa insuficiente", "lingua portuguesa basico", "lingua portuguesa proficiente", "lingua portuguesa avancado", "matematica insuficiente", "matematica basico", "matematica proeficiente", "matematica avancado "]:
    if col in df.columns and df[col].dtype == object:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

ESTADO_1 = "MG"
ESTADO_2 = "BA"
COR_1 = "#FF6B6B"
COR_2 = "#00F5D4"
CORES = {ESTADO_1: COR_1, ESTADO_2: COR_2}

df_filtrado = df[
    (df["uf"].isin([ESTADO_1, ESTADO_2]))
].copy()

df_tabela = df_filtrado[["uf"]]

st.title(f"Painel Streamlit do saeb aprendizado territorios — {ESTADO_1} e {ESTADO_2}")

st.sidebar.header("Controles")
opcao = st.sidebar.radio("Selecione a visualização:", ["Tabela", "Gráficos"])

if opcao == "Tabela":
    st.header("Tabela do saeb (Série Histórica)")
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)

elif opcao == "Gráficos":
    st.header(f"Gráficos do saeb — {ESTADO_1} e {ESTADO_2}")

    # ---------- 3. BARRAS AGRUPADAS ----------
    st.subheader("3. Gráfico de Barras Agrupadas")
    fig3 = px.bar(df_tabela, x="uf", y="uf", color="uf", barmode="group",
                  title="Comparativo Anual de saeb (Barras Agrupadas)",
                  color_discrete_map=CORES, template="plotly_dark")
    fig3.update_xaxes(type="category")
    st.plotly_chart(fig3, use_container_width=True)

    # ---------- 4. BARRAS EMPILHADAS (dimensões do último ano) ----------
    st.subheader("4. Gráfico de Barras Empilhadas")
    dimensoes = [c for c in ["lingua portuguesa adequado", "matematica adequado", "lingua portuguesa insuficiente", "lingua portuguesa basico", "lingua portuguesa proficiente", "lingua portuguesa avancado", "matematica insuficiente", "matematica basico", "matematica proeficiente", "matematica avancado "] if c in df_filtrado.columns]
    ultimo_ano = df_filtrado["uf"].max()
    dados_empilhado = df_filtrado[df_filtrado["uf"] == ultimo_ano].melt(
        id_vars="uf", value_vars=dimensoes, var_name="Dimensao", value_name="Valor"
    ).rename(columns={"uf": ""})
    fig4 = px.bar(dados_empilhado, x="", y="Valor", color="Dimensao", barmode="stack",
                  title=f"Composição do saeb por Dimensão — {ultimo_ano} (Barras Empilhadas)",
                  template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Fonte dos dados: dados abertos da Prefeitura de Belo Horizonte — https://www.gov.br/inep")
