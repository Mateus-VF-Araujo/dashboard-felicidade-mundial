import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Dashboard da Felicidade Mundial",
    page_icon="🌍",
    layout="wide",
)

# --- 2. Funções de Carregamento e Processamento de Dados ---
# O cache do Streamlit acelera a aplicação, pois os dados não são recarregados a cada interação.
@st.cache_data
def carregar_dados_consolidados():
    """
    Carrega e consolida os dados de felicidade de 2015 a 2019,
    padronizando as colunas essenciais como 'Country', 'Score' e 'Rank'.
    """
    anos = [2015, 2016, 2017, 2018, 2019]
    df_list = []
    for ano in anos:
        df = pd.read_csv(f"{ano}.csv", encoding='utf-8')
        rename_map = {
            'Country or region': 'Country', 'Country name': 'Country',
            'Happiness Score': 'Score', 'Happiness.Score': 'Score', 'Life Ladder': 'Score',
            'Happiness Rank': 'Rank', 'Overall rank': 'Rank', 'Happiness.Rank': 'Rank'
        }
        cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(columns=cols_to_rename)
        df['Year'] = ano
        if 'Rank' not in df.columns:
            df['Rank'] = df['Score'].rank(ascending=False).astype(int)
        df_list.append(df)
    df_total = pd.concat(df_list, ignore_index=True)
    return df_total

@st.cache_data
def carregar_dados_detalhados():
    """
    Carrega e padroniza os dados detalhados com todos os fatores de felicidade
    (PIB, Suporte Social, etc.) para as análises de correlação.
    """
    anos = [2015, 2016, 2017, 2018, 2019]
    dfs = []
    for ano in anos:
        df = pd.read_csv(f"{ano}.csv")
        col_renomeadas = {
            'Country or region': 'Country', 'Country name': 'Country',
            'Happiness.Score': 'Score', 'Happiness Score': 'Score',
            'Economy (GDP per Capita)': 'GDP', 'Economy..GDP.per.Capita.': 'GDP', 'GDP per capita': 'GDP',
            'Health (Life Expectancy)': 'Life expectancy', 'Health..Life.Expectancy.': 'Life expectancy', 'Healthy life expectancy': 'Life expectancy',
            'Freedom': 'Freedom', 'Freedom to make life choices': 'Freedom',
            'Trust (Government Corruption)': 'Corruption', 'Trust..Government.Corruption.': 'Corruption', 'Perceptions of corruption': 'Corruption',
            'Family': 'Social support', 'Social support': 'Social support',
            'Generosity': 'Generosity'
        }
        df = df.rename(columns=col_renomeadas)
        colunas_necessarias = ['Country', 'Score', 'GDP', 'Social support', 'Life expectancy', 'Freedom', 'Generosity', 'Corruption']
        df = df[[col for col in colunas_necessarias if col in df.columns]]
        df['Year'] = ano
        dfs.append(df)
    df_completo = pd.concat(dfs, ignore_index=True).dropna()
    return df_completo

# Carrega os dados uma vez
df_total = carregar_dados_consolidados()
df_detailed = carregar_dados_detalhados()
paises_disponiveis = sorted(df_total['Country'].unique())

# --- 3. Layout do Dashboard (Título e Sidebar) ---
st.title("🌍 Dashboard Interativo do Relatório Mundial da Felicidade")
st.markdown("Análise dos dados de 2015 a 2019 com base no seu notebook `Projeto_2_.ipynb`.")

st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione a análise que deseja visualizar:",
                        ["Visão Geral e Mapa",
                         "Rankings Globais (Animado)",
                         "Análise por Continente (Animado)",
                         "Evolução e Comparação entre Países",
                         "Análise de Fatores (PIB, Liberdade, etc.)"])
st.sidebar.markdown("---")
st.sidebar.info("Este dashboard foi criado com base no notebook `Projeto_2_.ipynb`.")

# --- 4. Geração dos Gráficos (conteúdo de cada página) ---

if page == "Visão Geral e Mapa":
    st.header("Mapa Interativo da Felicidade")
    st.markdown("Selecione um ano para visualizar a distribuição da felicidade no mundo.")
    ano_mapa = st.slider("Selecione o Ano:", 2015, 2019, 2019)
    
    df_mapa = df_total[df_total['Year'] == ano_mapa]
    fig_mapa = px.choropleth(
        df_mapa, locations='Country', locationmode='country names',
        color='Score', hover_name='Country', color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Nível de Felicidade por País - {ano_mapa}", labels={'Score': 'Pontuação'}
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    # ADICIONADO: Gráfico da Média Global
    st.markdown("---")
    st.header("Média Global da Felicidade (2015-2019)")
    media_ano = df_total.groupby('Year')['Score'].mean().reset_index()
    fig_media_global = px.line(
        media_ano, x='Year', y='Score', markers=True,
        title='Evolução da Média Global da Pontuação de Felicidade'
    )
    fig_media_global.update_layout(xaxis=dict(tickmode='linear'))
    st.plotly_chart(fig_media_global, use_container_width=True)

elif page == "Rankings Globais (Animado)":
    st.header("Rankings dos Países Mais e Menos Felizes")
    st.markdown("Os gráficos abaixo mostram a evolução anual dos 10 países no topo e na base do ranking.")
    col1, col2 = st.columns(2)
    with col1:
        df_top10 = df_total[df_total['Rank'] <= 10]
        fig_top10 = px.bar(
            df_top10, x='Score', y='Country', color='Country', animation_frame='Year',
            orientation='h', title='Top 10 Países Mais Felizes por Ano', range_x=[df_top10['Score'].min() - 0.5, 8]
        )
        fig_top10.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2000
        fig_top10.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        st.plotly_chart(fig_top10, use_container_width=True)
    with col2:
        df_bottom10 = df_total.groupby('Year', group_keys=False).apply(lambda x: x.nsmallest(10, 'Score'))
        fig_bottom10 = px.bar(
            df_bottom10, x='Score', y='Country', color='Country', animation_frame='Year',
            orientation='h', title='Top 10 Países Menos Felizes por Ano', range_x=[0, df_bottom10['Score'].max() + 0.5]
        )
        fig_bottom10.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2000
        fig_bottom10.update_layout(yaxis={'categoryorder': 'total descending'}, showlegend=False)
        st.plotly_chart(fig_bottom10, use_container_width=True)

elif page == "Análise por Continente (Animado)":
    st.header("Média do Score de Felicidade por Continente")
    # Mapeamento de países para continentes
    continent_map = { 'Africa': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Ivory Coast', 'Djibouti', 'Egypt', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone', 'Somalia', 'Somaliland Region', 'Somaliland region', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'], 'Asia': ['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Cambodia', 'China', 'Hong Kong', 'Hong Kong S.A.R., China', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Mongolia', 'Myanmar', 'Nepal', 'Oman', 'Pakistan', 'Palestinian Territories', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Taiwan Province of China', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'], 'Europe': ['Albania', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Lithuania', 'Luxembourg', 'Macedonia', 'Malta', 'Moldova', 'Montenegro', 'Netherlands', 'North Cyprus', 'North Macedonia', 'Northern Cyprus', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom'], 'Americas': ['Argentina', 'Belize', 'Bolivia', 'Brazil', 'Canada', 'Chile', 'Colombia', 'Costa Rica', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Guatemala', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Puerto Rico', 'Suriname', 'Trinidad & Tobago', 'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela'], 'Oceania': ['Australia', 'New Zealand']}
    
    # Remapeando o continente 'North America' e 'South America' para 'Americas' para simplificar a visualização
    country_to_continent = {country: continent for continent, countries in continent_map.items() for country in countries}
    df_total['Continent'] = df_total['Country'].map(country_to_continent)
    
    # Agrupando os dados e calculando a média
    df_grouped = df_total.groupby(['Year', 'Continent'])['Score'].mean().reset_index()

    # ALTERADO: Filtrando para manter apenas os continentes desejados
    continentes_desejados = ['Oceania', 'Americas', 'Europe', 'Asia', 'Africa']
    df_filtrado_continentes = df_grouped[df_grouped['Continent'].isin(continentes_desejados)]

    fig_continent = px.bar(
        df_filtrado_continentes.sort_values(['Year', 'Score']), x='Score', y='Continent',
        orientation='h', color='Continent', animation_frame='Year',
        title='Média do Score de Felicidade por Continente',
        labels={'Score': 'Score Médio', 'Continent': 'Continente'},
        text=df_filtrado_continentes['Score'].round(2)
    )
    fig_continent.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2000
    st.plotly_chart(fig_continent, use_container_width=True)


elif page == "Evolução e Comparação entre Países":
    st.header("Evolução da Felicidade (Gráfico de Linha)")
    paises_linha = st.multiselect("Selecione os países para o gráfico de linha:", options=paises_disponiveis, default=['Brazil', 'Argentina', 'Portugal', 'Finland'])
    if paises_linha:
        df_filtrado = df_total[df_total['Country'].isin(paises_linha)]
        fig_linha = px.line(df_filtrado, x='Year', y='Score', color='Country', markers=True, title='Evolução da Felicidade por País (2015–2019)')
        fig_linha.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_linha, use_container_width=True)

    st.markdown("---")
    st.header("Comparativo de Indicadores (Gráfico de Radar)")
    ano_radar = st.slider("Selecione o Ano para o Radar:", 2015, 2019, 2019)
    paises_radar = st.multiselect("Selecione os países para o radar:", options=paises_disponiveis, default=['Brazil', 'Finland'])
    
    if paises_radar:
        indicadores = ['GDP', 'Social support', 'Life expectancy', 'Freedom', 'Generosity', 'Corruption']
        df_radar = df_detailed[(df_detailed['Year'] == ano_radar) & (df_detailed['Country'].isin(paises_radar))]
        
        fig_radar = go.Figure()
        for _, row in df_radar.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row.get(ind, 0) for ind in indicadores], theta=indicadores, fill='toself', name=row['Country']
            ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 2])), showlegend=True, title=f"Comparativo de Indicadores ({ano_radar})")
        st.plotly_chart(fig_radar, use_container_width=True)

elif page == "Análise de Fatores (PIB, Liberdade, etc.)":
    st.header("Relação entre Felicidade, PIB e Liberdade")
    st.markdown("Cada ponto representa um país. A cor representa o nível de liberdade de escolha e o tamanho, a pontuação de felicidade.")
    ano_scatter = st.slider("Selecione o Ano para o Gráfico de Dispersão:", 2015, 2019, 2019)
    
    df_scatter_ano = df_detailed[df_detailed['Year'] == ano_scatter]
    fig_scatter = px.scatter(
        df_scatter_ano, x='GDP', y='Score',
        size='Score', color='Freedom', hover_name='Country', size_max=20,
        title=f'Felicidade vs. PIB per Capita vs. Liberdade ({ano_scatter})',
        labels={'GDP': 'PIB per Capita', 'Score': 'Pontuação de Felicidade', 'Freedom': 'Liberdade de Escolha'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
