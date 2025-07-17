import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json
import requests
from io import BytesIO

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="Dashboard da Felicidade Mundial",
    page_icon="🌍",
    layout="wide",
)

# --- 2. Funções de Carregamento e Processamento de Dados (com Cache) ---
@st.cache_data
def carregar_dados_consolidados():
    """
    Carrega e consolida os dados de felicidade de 2015 a 2019.
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
        df_list.append(df[['Country', 'Score', 'Rank', 'Year']])
    df_total = pd.concat(df_list, ignore_index=True)
    return df_total

@st.cache_data
def carregar_dados_detalhados():
    """
    Carrega e padroniza os dados detalhados com todos os fatores de felicidade.
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
        colunas_necessarias = ['Country', 'Score', 'GDP', 'Social support', 'Life expectancy', 'Freedom', 'Generosity', 'Corruption']
        df = df[[col for col in colunas_necessarias if col in df.columns]]
        df['Year'] = ano
        dfs.append(df)
    df_completo = pd.concat(dfs, ignore_index=True).dropna()
    return df_completo

# Carrega os dados
df_total = carregar_dados_consolidados()
df_detailed = carregar_dados_detalhados()
paises_disponiveis = sorted(df_total['Country'].unique())

# --- 3. Layout do Dashboard ---
st.sidebar.title("Painel de Controle")
page = st.sidebar.radio(
    "Selecione a Análise:",
    [
        "Página Inicial",
        "Visão Geral e Mapa",
        "Rankings Anuais",
        "Análise por Continente",
        "Evolução por País",
        "Análise dos Fatores de Felicidade",
        "Aprendizado de Máquina"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Este dashboard foi criado com base no World Happiness Report (2015-2019).")

# --- 4. Conteúdo Principal ---

if page == "Página Inicial":
    st.title("Bem-vindo(a) ao Dashboard da Felicidade Mundial 🌍😁")
    st.markdown("---")
    
    st.image("https://cdn.pixabay.com/photo/2016/11/21/13/58/ball-1845546_640.jpg", use_container_width=True)
    
    st.subheader("Sobre este Projeto")
    st.markdown("""
    Este dashboard interativo foi criado para explorar os dados do **World Happiness Report** de 2015 a 2019. 
    A felicidade é um indicador fundamental do progresso social e do bem-estar humano. Através desta ferramenta, você pode:

    -   Visualizar a distribuição da felicidade no mundo.
    -   Analisar a evolução da pontuação dos países ao longo dos anos.
    -   Comparar o desempenho entre nações e continentes.
    -   Explorar os fatores que mais contribuem para uma vida feliz, como a economia, o suporte social e a percepção de corrupção.
    """)

    st.subheader("Como Navegar")
    st.info("Use o menu na barra lateral à esquerda para navegar entre as diferentes seções de análise.")

    st.subheader("Fonte dos Dados")
    st.markdown("""
    Os dados utilizados neste projeto foram obtidos do **World Happiness Report**, disponibilizados pela Sustainable Development Solutions Network (SDSN) na plataforma Kaggle.
    
    [🔗 Acesse o dataset original no Kaggle](https://www.kaggle.com/datasets/unsdsn/world-happiness)
    """)

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Autores")
        st.write("Maria Eduarda Silva da Costa")
        st.write("Mateus Vinicius Figueredo de Araújo")
    with col2:
        st.subheader("Contexto Acadêmico")
        st.write("**Disciplina:** Ciência de Dados (DCA-3501)")
        st.write("**Professor:** Dr. Luiz Affonso Guedes")
        st.write("**Instituição:** UFRN - Departamento de Engenharia de Computação e Automação")
        st.write("**Período**: 2025.1")

elif page == "Visão Geral e Mapa":
    st.header("Mapa Interativo da Felicidade")
    ano_selecionado = st.slider("Selecione o Ano:", 2015, 2019, 2019)
    df_mapa = df_total[df_total['Year'] == ano_selecionado]
    fig = px.choropleth(
        df_mapa, locations='Country', locationmode='country names',
        color='Score', hover_name='Country', color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Nível de Felicidade por País - {ano_selecionado}", labels={'Score': 'Pontuação de Felicidade'}
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Pontuação"))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.header("Média Global da Felicidade (2015-2019)")
    media_ano = df_total.groupby('Year')['Score'].mean().reset_index()
    fig_media_global = px.line(
        media_ano, x='Year', y='Score', markers=True,
        title='Evolução da Média Global da Pontuação de Felicidade',
        labels={'Year': 'Ano', 'Score': 'Pontuação Média'}
    )
    fig_media_global.update_layout(xaxis=dict(tickmode='linear'))
    st.plotly_chart(fig_media_global, use_container_width=True)

elif page == "Rankings Anuais":
    st.header("Rankings dos Países Mais e Menos Felizes")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Países Mais Felizes")
        df_top10 = df_total[df_total['Rank'] <= 10]
        fig_top10 = px.bar(
            df_top10, x='Score', y='Country', color='Country',
            animation_frame='Year', orientation='h', title='Top 10 Países Mais Felizes por Ano',
            range_x=[df_top10['Score'].min() - 0.5, 8], labels={'Score': 'Pontuação', 'Country': 'País'}
        )
        fig_top10.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
        fig_top10.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        st.plotly_chart(fig_top10, use_container_width=True)
    with col2:
        st.subheader("Top 10 Países Menos Felizes")
        df_bottom10 = df_total.groupby('Year', group_keys=False).apply(lambda x: x.nsmallest(10, 'Score'))
        fig_bottom10 = px.bar(
            df_bottom10, x='Score', y='Country', color='Country',
            animation_frame='Year', orientation='h', title='Top 10 Países Menos Felizes por Ano',
            range_x=[0, df_bottom10['Score'].max() + 0.5], labels={'Score': 'Pontuação', 'Country': 'País'}
        )
        fig_bottom10.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
        fig_bottom10.update_layout(yaxis={'categoryorder': 'total descending'}, showlegend=False)
        st.plotly_chart(fig_bottom10, use_container_width=True)

elif page == "Análise por Continente":
    st.header("Média do Score de Felicidade por Continente")
    continent_map = { 'Africa': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Ivory Coast', 'Djibouti', 'Egypt', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone', 'Somalia', 'Somaliland Region', 'Somaliland region', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'], 'Asia': ['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Cambodia', 'China', 'Hong Kong', 'Hong Kong S.A.R., China', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Mongolia', 'Myanmar', 'Nepal', 'Oman', 'Pakistan', 'Palestinian Territories', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Taiwan Province of China', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'], 'Europe': ['Albania', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Lithuania', 'Luxembourg', 'Macedonia', 'Malta', 'Moldova', 'Montenegro', 'Netherlands', 'North Cyprus', 'North Macedonia', 'Northern Cyprus', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom'], 'Americas': ['Argentina', 'Belize', 'Bolivia', 'Brazil', 'Canada', 'Chile', 'Colombia', 'Costa Rica', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Guatemala', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Puerto Rico', 'Suriname', 'Trinidad & Tobago', 'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela'], 'Oceania': ['Australia', 'New Zealand']}
    country_to_continent = {country: continent for continent, countries in continent_map.items() for country in countries}
    df_total['Continent'] = df_total['Country'].map(country_to_continent)
    df_continente_filtrado = df_total.dropna(subset=['Continent'])
    df_grouped = df_continente_filtrado.groupby(['Year', 'Continent'])['Score'].mean().reset_index()

    fig_continent = px.bar(
        df_grouped.sort_values(['Year', 'Score']),
        x='Score', y='Continent',
        orientation='h', color='Continent',
        animation_frame='Year', title='Média do Score de Felicidade por Continente',
        labels={'Score': 'Pontuação Média', 'Continent': 'Continente'}, text=df_grouped['Score'].round(2)
    )
    fig_continent.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
    st.plotly_chart(fig_continent, use_container_width=True)

elif page == "Evolução por País":
    st.header("Evolução da Felicidade por País")
    paises_selecionados = st.multiselect("Selecione os países:", options=paises_disponiveis, default=['Brazil', 'Argentina', 'Portugal', 'Finland'])
    if paises_selecionados:
        df_filtrado = df_total[df_total['Country'].isin(paises_selecionados)]
        fig = px.line(
            df_filtrado, x='Year', y='Score', color='Country',
            markers=True, title='Evolução da Felicidade por País (2015–2019)',
            labels={'Year': 'Ano', 'Score': 'Pontuação de Felicidade', 'Country': 'País'}
        )
        fig.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig, use_container_width=True)

elif page == "Análise dos Fatores de Felicidade":
    st.header("Análise dos Fatores que Compõem a Felicidade")
    
    st.subheader("Felicidade vs. PIB e Liberdade")
    ano_scatter = st.slider("Selecione o Ano:", 2015, 2019, 2019, key='slider_scatter')
    df_scatter_ano = df_detailed[df_detailed['Year'] == ano_scatter]
    fig_scatter = px.scatter(
        df_scatter_ano, x='GDP', y='Score',
        size='Score', color='Freedom', hover_name='Country', size_max=20,
        title=f'Felicidade vs. PIB e Liberdade ({ano_scatter})',
        labels={'GDP': 'PIB per Capita', 'Score': 'Pontuação de Felicidade', 'Freedom': 'Nível de Liberdade'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Radar de Indicadores por País")
    col1, col2 = st.columns(2)
    with col1:
        ano_radar = st.slider("Selecione o Ano:", 2015, 2019, 2019, key='slider_radar')
    with col2:
        paises_radar = st.multiselect("Selecione os países para comparar:", options=paises_disponiveis, default=['Brazil', 'Finland'])
    
    if paises_radar:
        indicadores_map = { 'GDP': 'PIB', 'Social support': 'Suporte Social', 'Life expectancy': 'Expectativa de Vida', 'Freedom': 'Liberdade', 'Generosity': 'Generosidade', 'Corruption': 'Percepção de Corrupção' }
        indicadores_originais = list(indicadores_map.keys())
        indicadores_pt = list(indicadores_map.values())
        
        df_radar_filtrado = df_detailed[(df_detailed['Year'] == ano_radar) & (df_detailed['Country'].isin(paises_radar))]
        fig_radar = go.Figure()
        for _, row in df_radar_filtrado.iterrows():
            valores = [row.get(col, 0) for col in indicadores_originais]
            fig_radar.add_trace(go.Scatterpolar(r=valores, theta=indicadores_pt, fill='toself', name=row['Country']))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, df_detailed[indicadores_originais].max().max()])),
            showlegend=True, title=f"Comparativo de Indicadores ({ano_radar})"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
elif page == "Aprendizado de Máquina":
    
    @st.cache_resource
    def load_model_and_columns():
        model_url = "https://github.com/Mateus-VF-Araujo/dashboard-felicidade-mundial/raw/main/extra_trees_model.joblib"
        columns_url = "https://github.com/Mateus-VF-Araujo/dashboard-felicidade-mundial/raw/main/model_columns.json"
        
        try:
            response_model = requests.get(model_url)
            response_model.raise_for_status()
            model_file = BytesIO(response_model.content)
            model = joblib.load(model_file)
            
            response_columns = requests.get(columns_url)
            response_columns.raise_for_status()
            model_columns = json.loads(response_columns.text)
            
            return model, model_columns
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar os arquivos do modelo: {e}")
            return None, None
            
    def create_gauge_chart(value):
        """Cria e retorna um gráfico de medidor."""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            title = {'text': "Score de Felicidade", 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [2, 8], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "black", 'thickness': 0.2},
                'bgcolor': "white",
                'borderwidth': 4,
                'bordercolor': "black",
                'steps': [
                    {'range': [2, 4], 'color': '#970700'}, # Vermelho
                    {'range': [4, 6], 'color': '#FFC222'}, # Amarelo
                    {'range': [6, 8], 'color': '#006400'}  # Verde
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }))
        
        fig.update_layout(
            paper_bgcolor = "rgba(0,0,0,0)",
            font = {'color': "white", 'family': "Arial"}
        )
        return fig

    # Carrega o modelo e as colunas
    model, model_columns = load_model_and_columns()

    # INTERFACE DO USUÁRIO
    st.title("😊 Previsor de Pontuação de Felicidade")
    st.markdown("Use os seletores abaixo para inserir os dados de um país e prever sua pontuação de felicidade com base em um modelo de Machine Learning.")

    if model and model_columns:
        st.sidebar.header("Insira os Dados do País:")

        def user_input_features():
            gdp = st.sidebar.slider('PIB per capita (GDP)', 0.0, 2.0, 1.1, 0.01)
            social_support = st.sidebar.slider('Apoio Social (Social support)', 0.0, 2.0, 1.2, 0.01)
            life_expectancy = st.sidebar.slider('Expectativa de Vida (Life expectancy)', 0.0, 1.5, 0.8, 0.01)
            freedom = st.sidebar.slider('Liberdade (Freedom)', 0.0, 1.0, 0.5, 0.01)
            generosity = st.sidebar.slider('Generosidade (Generosity)', 0.0, 1.0, 0.2, 0.01)
            corruption = st.sidebar.slider('Percepção de Corrupção (Corruption)', 0.0, 0.6, 0.15, 0.01)
            
            data = {
                'GDP': gdp, 'Social support': social_support, 'Life expectancy': life_expectancy,
                'Freedom': freedom, 'Generosity': generosity, 'Corruption': corruption
            }
            
            features = pd.DataFrame(data, index=[0])
            return features[model_columns]

        input_df = user_input_features()
        st.subheader("Dados Inseridos:")
        st.write(input_df.style.hide(axis="index"))

        if st.button("Prever Pontuação de Felicidade"):
            prediction = model.predict(input_df)
            score = prediction[0]
            
            st.subheader("Resultado da Previsão:")
            
            fig = create_gauge_chart(score)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("Esta previsão é baseada no modelo ExtraTreesRegressor treinado com dados do World Happiness Report (2015-2019).")

    else:
        st.warning("O modelo não pôde ser carregado.")

