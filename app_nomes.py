import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import folium
from streamlit_folium import st_folium

from utils import pegar_ids_estados, pegar_nome_por_decada, pegar_frequencia_nome_por_estado, mapa_brasil



def main():
    st.set_page_config(layout='wide')
       
    with st.sidebar:
        
        st.image(image='logo.png', use_container_width=100)
        
        
        st.divider()
        st.subheader('Faça sua pesquisa:')
        nome = st.text_input('Digite o nome desejado:', placeholder='Nome').capitalize()
        
    
    main_container = st.empty()
    if not nome:
        with main_container.container():
            # st.title("Bem-vindo ao Web App Nomes")
            st.markdown("""
                <div style='text-align: center; margin-top: 100px;'>
                    <h1>Bem-vindo(a) ao Web App Nomes</h1>
                    <h2>Digite um nome no campo de pesquisa à esquerda para ver estatísticas e distribuição geográfica*</h2>
                    <p>Os dados apresentados neste App foram coletados à partir da API Nomes forneceida pelo IBGE</p>
                    <p></p>
                    <p></p>
                    <p> a) O resultado apresentado para frequência do nome pesquisado é em relação à proporção por 100.000 habitantes.</p>
                    <p> b) O Censo Demográfico 2010 não considerou nos questionários nomes compostos, apenas o primeiro nome e o último sobrenome. Por essa razão, esta API não retorna resultados ao consultar nomes compostos.</p>
                    <p> c) Quando a quantidade de ocorrências for suficientemente pequena a ponto de permitir a identificação delas, o IBGE não informa essa quantidade. <br> No caso da API de Nomes, a quantidade mínima de ocorrências para que seja divulgado os resultados é de 10 por município, 15 por Unidade da Federação e 20 no Brasil.</p>
                </div>
            """, unsafe_allow_html=True)
            

            if not nome:
                st.stop()
    
        

# Carregando dados da API Nomes---------------------------------------------------------------
    dict_estados = pegar_ids_estados()
    if not dict_estados:
        st.warning(f'Nenhum dado encontrado para o nome {nome}')
        st.stop()
    dict_frequencia = pegar_frequencia_nome_por_estado(nome)
    if not dict_frequencia:
        st.warning(f'Nenhum dado encontrado para o nome {nome}')
        st.stop()
   
    for id_estado, nome_estado in dict_estados.items():
        if not dict_estados:
            st.warning(f'Nenhum dado encontrado para o nome {nome}')
            st.stop()
        
    dict_decada = pegar_nome_por_decada(nome)
    if not dict_decada:
        st.warning(f'Nenhum dado encontrado para o nome {nome}')
        st.stop()
    
    df = pd.DataFrame.from_dict(dict_decada, orient='index')

    df_localidades = pd.DataFrame.from_dict(dict_estados, orient='index')
    df_localidades = df_localidades.reset_index(drop=False)
    df_localidades = df_localidades.rename(columns={0:'Estado', 'index':'UF-id'})
    
    df_frequencia = pd.DataFrame.from_dict(dict_frequencia, orient='index')
    df_frequencia = df_frequencia.reset_index(drop=False)
    df_frequencia = df_frequencia.rename(columns={0:'Frequencia', 'index':'UF-id'})
    
    df_freq_loc = df_localidades.merge(df_frequencia, left_on='UF-id', right_on='UF-id', how='left')
    # df_freq_loc.to_csv('df.csv')
    df_freq_loc_top10 = df_freq_loc.sort_values(by='Frequencia', ascending=False).head(10)


    
# Carregando dados da API Nomes---------------------------------------------------------------
    st.title('Web App Nomes')
    
    col01, col02 = st.columns([0.6, 0.8])
    
    with col01:
            
        st.subheader(f'Resultados da pesquisa para o nome {nome}')
        tit_graph_freq = (f'Frequência do nome {nome} por Década')
        df_decada = df
        df_decada = df_decada.reset_index(drop=False)
        df_decada = df_decada.rename(columns={
            'index':'Decadas',
            0:'Frequencia'
        })
        fig_freq_decada = go.Figure()
        fig_freq_decada.add_trace(go.Bar(
            x=df_decada['Decadas'],
            y=df_decada['Frequencia'],
            marker_color=  "#F87407",
        ))
        fig_freq_decada.update_layout(title = tit_graph_freq)
        st.plotly_chart(fig_freq_decada)
            
        tit_graph_rank = (f'Top 10 Frequência do {nome} por Estado')
        fig_chart_bar = go.Figure()
        fig_chart_bar.add_trace(go.Bar(
            x = df_freq_loc_top10['Estado'],
            y = df_freq_loc_top10['Frequencia'],
            marker_color = "#F87407",
            textangle=45,
            ))
        fig_chart_bar.update_layout(title = tit_graph_rank)
        st.plotly_chart(fig_chart_bar)
            

        
    with col02:

        map_container = st.empty()    
        with st.spinner('Gerando mapa...'):
            mapa = mapa_brasil(df_freq_loc, nome)
            map_container.empty()  # Limpa container antes de renderizar
            st_folium(mapa, width=2000, height=970)

    
if __name__=='__main__':
    main()