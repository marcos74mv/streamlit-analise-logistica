import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise de Dados - Exercício Prático", layout="wide")
st.title("📊 Análise de Dados - Exercício Prático")

@st.cache_data
def carregar_dados():
    xls = pd.ExcelFile("Exercício Prático - Base de dados.xlsx")
    df_entregas = pd.read_excel(xls, sheet_name="Entregas")
    df_vendas = pd.read_excel(xls, sheet_name="Base Vendas")

    if "Data Pedido" in df_entregas.columns:
        df_entregas["Data Pedido"] = pd.to_datetime(df_entregas["Data Pedido"])
    if "Data" in df_vendas.columns:
        df_vendas["Data"] = pd.to_datetime(df_vendas["Data"])
    return df_entregas, df_vendas

df_entregas, df_vendas = carregar_dados()
sns.set(style="whitegrid")
plt.rcParams.update({"axes.facecolor": "none", "figure.facecolor": "none"})

aba = st.sidebar.radio("Escolha a aba para análise:", ["Entregas", "Vendas"])

# ===== ABA ENTREGAS =====
if aba == "Entregas":
    st.header("🚚 Análise de Entregas")

    st.subheader("📌 Rota Mais Cara (Custo Médio por Km)")
    df_entregas["Custo por km"] = df_entregas["Custo Frete (R$)"] / df_entregas["Distância (km)"]
    custo_medio = df_entregas.groupby("Rota")["Custo por km"].mean().reset_index().sort_values("Custo por km", ascending=False)
    fig_rota = px.bar(custo_medio, x="Custo por km", y="Rota", orientation="h", color="Custo por km", color_continuous_scale="Blues")
    fig_rota.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_rota, use_container_width=True)
    st.markdown(f"A **rota mais cara** é **{custo_medio.iloc[0]['Rota']}**, com custo médio de **R$ {custo_medio.iloc[0]['Custo por km']:.2f}/km**.")

    st.subheader("📈 Eficiência das Entregas: Relações entre Variáveis")
    corr = df_entregas[["Distância (km)", "Custo Frete (R$)", "Tempo de Entrega (dias)"]].corr()
    fig_corr, ax = plt.subplots(figsize=(4, 3), facecolor='none')
    sns.heatmap(corr, annot=True, cmap="Blues", ax=ax, cbar=False)
    st.pyplot(fig_corr)
    st.markdown(
        "- **Distância e Custo** têm correlação forte (r > 0.8): esperado.\n"
        "- **Tempo de Entrega** não cresce proporcional à distância: há rotas curtas com entrega demorada.\n"
        "- **Possível gargalo logístico** em algumas entregas curtas com atrasos."
    )

    st.subheader("🔍 Oportunidades de Otimização")
    df_entregas["Eficiência"] = df_entregas["Distância (km)"] / df_entregas["Tempo de Entrega (dias)"]
    df_alerta = df_entregas[
        (df_entregas["Distância (km)"] < 600) &
        ((df_entregas["Custo Frete (R$)"] > 1000) | (df_entregas["Tempo de Entrega (dias)"] > 3))
    ][["Rota", "Distância (km)", "Custo Frete (R$)", "Tempo de Entrega (dias)", "Eficiência"]]
    st.dataframe(df_alerta, use_container_width=True)

    st.subheader("📊 Relação entre Custo de Frete e Distância")
    fig_disp = px.scatter(df_entregas, x="Distância (km)", y="Custo Frete (R$)", color="Rota", trendline="ols", color_discrete_sequence=px.colors.qualitative.Set1)
    fig_disp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_disp, use_container_width=True)

    st.subheader("✅ Recomendações para Logística")
    st.markdown('''
- 📦 Otimizar rotas de curto alcance com alto custo ou demora:
  **Como?** Identifique os pedidos com baixa eficiência e analise se há rotas alternativas ou agrupamento de entregas próximas para reduzir custos.

- 🚛 Avaliar parcerias logísticas locais ou redesenho de rotas:
  **Como?** Faça benchmarking com transportadoras da região e simule novos trajetos com ferramentas de roteirização como Google Maps ou APIs de logística.

- 📊 Monitorar eficiência por km com dashboards mensais:
  **Como?** Crie indicadores no Power BI ou Excel para acompanhar custo médio por km, tempo médio de entrega e pedidos fora do padrão mês a mês.

- ⏱️ Investir em soluções de previsão de entrega:
  **Como?** Utilize modelos simples de regressão ou machine learning baseados em distância, peso e histórico para estimar prazos mais realistas ao cliente.
''')

# ===== ABA VENDAS =====
elif aba == "Vendas":
    st.header("🛍️ Análise de Vendas")

    st.subheader("🎯 Análise Geral por Segmento de Cliente e Produto")

    # Valor médio por segmento e produto
    media_valores = df_vendas.groupby(["Segmento do cliente", "Produto"])["Valor"].mean().reset_index()
    fig_media = px.bar(media_valores, x="Segmento do cliente", y="Valor", color="Produto", barmode="group", text_auto=".2s", color_discrete_sequence=px.colors.qualitative.Set1)
    fig_media.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_media, use_container_width=True)
    st.markdown("📌 O gráfico mostra o **valor médio** dos produtos por segmento de cliente. É possível notar que o segmento **Empresarial** possui os valores médios mais altos, indicando maior poder de compra.")

    # Distribuição dos valores por produto
    st.subheader("📊 Distribuição de Valor dos Produtos (por Produto)")
    for produto in df_vendas["Produto"].unique():
        st.markdown(f"**Produto: {produto}**")
        fig = px.box(df_vendas[df_vendas["Produto"] == produto], x="Segmento do cliente", y="Valor", points="outliers", color_discrete_sequence=["#4682B4"])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"- Neste gráfico, observamos a distribuição de preços do **{produto}** por segmento.")
        st.markdown("  - O formato do boxplot mostra a **variação interna dos preços** (linha central = mediana).")
        st.markdown("  - Quanto mais espalhado, mais o preço varia entre clientes.")
        st.markdown("  - Pontos fora do padrão são **outliers** e podem representar promoções, descontos ou vendas acima da média.")
        st.markdown("---")

    st.subheader("📆 Evolução de Vendas por Ano e Mês")
    df_vendas["Ano"] = df_vendas["Data"].dt.year
    df_vendas["Mês"] = df_vendas["Data"].dt.to_period("M").astype(str)
    vendas_mensais = df_vendas.groupby(["Ano", "Mês"])["Valor"].sum().reset_index()
    fig_mes = px.bar(vendas_mensais, x="Mês", y="Valor", color="Ano", barmode="group")
    fig_mes.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_mes, use_container_width=True)
    st.markdown("📈 Aqui acompanhamos a evolução das vendas. Picos podem indicar **campanhas sazonais** e ajudam no planejamento de ações futuras.")

    st.subheader("🌎 Regiões Mais Rentáveis")
    regiao = df_vendas.groupby("Estado/País")["Valor"].sum().reset_index().sort_values("Valor", ascending=False)
    fig_reg = px.bar(regiao, x="Estado/País", y="Valor", color="Valor", color_continuous_scale="Blues")
    fig_reg.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_reg, use_container_width=True)
    st.markdown(f"🏆 A região mais rentável é **{regiao.iloc[0]['Estado/País']}**, com total de vendas de **R$ {regiao.iloc[0]['Valor']:.2f}**.")
    st.markdown("📌 Use essa informação para priorizar estratégias comerciais em regiões de maior retorno.")