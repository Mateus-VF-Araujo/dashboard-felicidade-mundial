import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard da Felicidade Mundial",
    page_icon="🌍😁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funções de Carregamento de Dados (com Cache) ---
# O cache acelera o carregamento, salvando os dados na memória.
@st.cache_data
def load_data():
    """
    Carrega e consolida os dados de felicidade de 2015 a 2019,
    padronizando as colunas essenciais.
    """
    anos = [2015, 2016, 2017, 2018, 2019]
    df_list = []

    for ano in anos:
        df = pd.read_csv(f"{ano}.csv", encoding='utf-8')
        
        # Renomeação flexível das colunas
        rename_map = {
            'Country or region': 'Country', 'Country name': 'Country',
            'Happiness Score': 'Score', 'Happiness.Score': 'Score', 'Life Ladder': 'Score',
            'Happiness Rank': 'Rank', 'Overall rank': 'Rank', 'Happiness.Rank': 'Rank'
        }
        
        # Filtra o dicionário para conter apenas as colunas presentes no df
        cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(columns=cols_to_rename)
        
        df['Year'] = ano
        
        # Garante que as colunas essenciais existam
        if 'Rank' not in df.columns:
            df['Rank'] = df['Score'].rank(ascending=False).astype(int)

        df_list.append(df[['Country', 'Score', 'Rank', 'Year']])

    df_total = pd.concat(df_list, ignore_index=True)
    return df_total

@st.cache_data
def load_detailed_data():
    """
    Carrega e padroniza os dados detalhados (com fatores de felicidade)
    para os gráficos de radar e dispersão.
    """
    anos = [2015, 2016, 2017, 2018, 2019]
    dfs = []
    
    for ano in anos:
        df = pd.read_csv(f"{ano}.csv", encoding='utf-8')
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
        df['Year'] = ano
        dfs.append(df)
        
    df_completo = pd.concat(dfs, ignore_index=True)
    return df_completo

# --- Carregamento Inicial dos Dados ---
df_total = load_data()
df_detailed = load_detailed_data()
paises_disponiveis = sorted(df_total['Country'].unique())

# --- Barra Lateral (Sidebar) ---
st.sidebar.image("https://images.unsplash.com/photo-1494883542223-95c553934335?q=80&w=2940&auto=format&fit=crop", use_column_width=True)
st.sidebar.title("Painel de Controle")

page = st.sidebar.radio(
    "Selecione a Análise:",
    [
        "Visão Geral (Mapa)", 
        "Rankings Anuais (Animado)", 
        "Evolução por País",
        "Análise por Continente",
        "Análise dos Fatores de Felicidade"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Dashboard criado com base no World Happiness Report (2015-2019).")

# --- Conteúdo Principal ---
st.title("🌍 Dashboard da Felicidade Mundial")
st.markdown("Análise interativa dos dados do *World Happiness Report* de 2015 a 2019.")

# --- Seção: Visão Geral (Mapa) ---
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

# --- Seção: Rankings Anuais ---
elif page == "Rankings Anuais (Animado)":
    st.header("Rankings dos Países Mais e Menos Felizes")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Países Mais Felizes")
        fig_top10 = px.bar(
            df_total[df_total['Rank'] <= 10],
            x='Score', y='Country', color='Country',
            animation_frame='Year', orientation='h',
            title='Top 10 Países Mais Felizes por Ano',
            range_x=[df_total[df_total['Rank'] <= 10]['Score'].min() - 0.5, 8],
            text='Score'
        )
        fig_top10.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_top10.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
        fig_top10.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top10, use_container_width=True)

    with col2:
        st.subheader("Top 10 Países Menos Felizes")
        # Seleciona os 10 países com os menores scores para cada ano
        df_bottom10 = df_total.groupby('Year', group_keys=False).apply(lambda x: x.nsmallest(10, 'Score'))
        
        fig_bottom10 = px.bar(
            df_bottom10,
            x='Score', y='Country', color='Country',
            animation_frame='Year', orientation='h',
            title='Top 10 Países Menos Felizes por Ano',
            range_x=[0, df_bottom10['Score'].max() + 0.5],
            text='Score'
        )
        fig_bottom10.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_bottom10.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
        fig_bottom10.update_layout(yaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_bottom10, use_container_width=True)

# --- Seção: Evolução por País ---
elif page == "Evolução por País":
    st.header("Evolução da Felicidade por País")
    
    paises_selecionados = st.multiselect(
        "Selecione os países:",
        options=paises_disponiveis,
        default=['Brazil', 'Argentina', 'Finland', 'Afghanistan']
    )
    
    if paises_selecionados:
        df_filtrado = df_total[df_total['Country'].isin(paises_selecionados)]
        
        fig = px.line(
            df_filtrado,
            x='Year', y='Score', color='Country',
            markers=True,
            title='Evolução da Felicidade por País (2015–2019)',
            labels={'Year': 'Ano', 'Score': 'Pontuação de Felicidade'}
        )
        fig.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Por favor, selecione pelo menos um país.")

# --- Seção: Análise por Continente ---
elif page == "Análise por Continente":
    st.header("Média do Score de Felicidade por Continente")
    
    # Mapeamento simplificado de países para continentes
    # Em um projeto real, seria melhor usar uma biblioteca como pycountry_convert
    continent_map = {
        'Africa': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Ivory Coast', 'Djibouti', 'Egypt', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone', 'Somalia', 'Somaliland region', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'],
        'Asia': ['Afghanistan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Cambodia', 'China', 'Hong Kong', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Mongolia', 'Myanmar', 'Nepal', 'Oman', 'Pakistan', 'Palestinian Territories', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'],
        'Europe': ['Albania', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Lithuania', 'Luxembourg', 'Macedonia', 'Malta', 'Moldova', 'Montenegro', 'Netherlands', 'North Cyprus', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom'],
        'Americas': ['Belize', 'Canada', 'Costa Rica', 'Dominican Republic', 'El Salvador', 'Guatemala', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Puerto Rico', 'Trinidad & Tobago', 'United States', 'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela'],
        'Oceania': ['Australia', 'New Zealand']
    }

    df_total['Continent'] = df_total['Country'].apply(get_continent)
    df_grouped = df_total.groupby(['Year', 'Continent'])['Score'].mean().reset_index()

    fig_continent = px.bar(
        df_grouped.sort_values(['Year', 'Score']),
        x='Score', y='Continent',
        orientation='h', color='Score',
        animation_frame='Year',
        color_continuous_scale='Viridis',
        title='Média do Score de Felicidade por Continente',
        labels={'Score': 'Score Médio', 'Continent': 'Continente'},
        text=df_grouped['Score'].round(2)
    )
    fig_continent.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
    st.plotly_chart(fig_continent, use_container_width=True)

# --- Seção: Fatores de Felicidade ---
elif page == "Análise dos Fatores de Felicidade":
    st.header("Correlação entre Felicidade e Outros Fatores")

    st.subheader("Felicidade vs. PIB per Capita")
    
    # Filtro para colunas necessárias
    cols_necessarias = ['Country', 'Year', 'Score', 'GDP', 'Freedom']
    df_scatter = df_detailed.dropna(subset=cols_necessarias)
    
    ano_scatter = st.slider("Selecione o Ano para o Gráfico de Dispersão:", 2015, 2019, 2019)
    df_scatter_ano = df_scatter[df_scatter['Year'] == ano_scatter]

    fig_scatter = px.scatter(
        df_scatter_ano,
        x='GDP', y='Score',
        size='Score',
        color='Freedom',
        hover_name='Country',
        size_max=20,
        title=f'Felicidade vs. PIB per Capita ({ano_scatter})',
        labels={'GDP': 'PIB per Capita', 'Score': 'Pontuação de Felicidade', 'Freedom': 'Liberdade'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Radar de Indicadores por País")
    
    col1, col2 = st.columns(2)
    with col1:
        ano_radar = st.slider("Selecione o Ano para o Radar:", 2015, 2019, 2019)
        indicadores = ['GDP', 'Social support', 'Life expectancy', 'Freedom', 'Generosity', 'Corruption']
        df_radar = df_detailed.dropna(subset=indicadores + ['Country', 'Year'])

    with col2:
        paises_radar = st.multiselect(
            "Selecione os países para comparar no radar:",
            options=paises_disponiveis,
            default=['Brazil', 'Finland']
        )
    
    if paises_radar:
        df_radar_filtrado = df_radar[(df_radar['Year'] == ano_radar) & (df_radar['Country'].isin(paises_radar))]
        
        fig_radar = go.Figure()

        for _, row in df_radar_filtrado.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row[ind] for ind in indicadores],
                theta=indicadores,
                fill='toself',
                name=row['Country']
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, df_radar[indicadores].max().max()])),
            showlegend=True,
            title=f"Comparativo de Indicadores ({ano_radar})"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("Por favor, selecione pelo menos um país para o radar.")
