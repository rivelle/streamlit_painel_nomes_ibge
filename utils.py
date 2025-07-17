import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import folium
import streamlit as st
from streamlit_folium import st_folium
import requests


# Consultas APIs IBGE ---------------------------------------------------------------------
def fazer_request(url, params=None):
    resposta = requests.get(url, params=params)
    try:
        resposta.raise_for_status()
    except requests.HTTPError as e:
        print(f'Erro no request: {e}')
        resultado = None
    else:
        resultado = resposta.json()
    return resultado


def pegar_ids_estados():
    url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
    params = {
        'view':'nivelado',
    }
    dados_estados = fazer_request(url=url, params=params)
    if not dados_estados:
        return {}
    dict_estado = {}
    for dados in dados_estados:
        id_estado = dados['UF-id']
        nome_estado = dados['UF-nome']
        dict_estado[id_estado] = nome_estado
    return dict_estado


def pegar_frequencia_nome_por_estado(nome):
    url = f'https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}'
    params = {
        'groupby':'UF',
    }
    dados_frequencias = fazer_request(url=url, params=params)
    if not dados_frequencias:
        return {}
    
    dict_frequencias = {}
    for dados in dados_frequencias:
        id_estado = int(dados['localidade'])
        frequencia = dados['res'][0]['proporcao']
        dict_frequencias[id_estado] = frequencia
    return dict_frequencias


def pegar_nome_por_decada(nome):
    url = f'https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}'
    dados_decada = fazer_request(url=url)
    if not dados_decada:
        return {}
    
    dict_decadas = {}
    for dados in dados_decada[0]['res']:
        decada = dados['periodo']
        quantidade = dados['frequencia']
        dict_decadas[decada] = quantidade
    return dict_decadas


# Mapas e Figuras ---------------------------------------------------------------------

# df = pd.read_csv('df.csv')

@st.cache_data
def figura_mapa_brasil(df, nome):
    #Dados---------------------------------
    brasil = gpd.read_file('brasil.gpkg', layer='limites_estados')
    brasil = brasil.rename(columns={
        'CD_UF':'UF-id',
        'NM_UF':'Estado'
    })
    brasil['UF-id'] = brasil['UF-id'].astype('Int64')
    st.session_state['df_brasil'] = brasil
    

    brasil_freq = brasil.join(df['Frequencia'], on='UF-id', how='left')
    st.session_state['df_brasil_freq'] = brasil_freq

    #Plot------------------------------------
    fig, eixo = plt.subplots(figsize=(10,10))
    st.session_state['df_brasil'].plot(ax=eixo, color='lightgray', alpha=0.3, edgecolor='black', linewidth=0.3)
    st.session_state['df_brasil_freq'].plot(ax=eixo,
                column='Frequencia',
                cmap='YlOrRd',
                edgecolor='black',
                linewidth=0.5,
                legend=False,
                )


    fig.suptitle(f'Mapa de Frequência do nome {nome} por Estado', fontsize=10)
    fig.tight_layout()
    return fig
    
@st.cache_data
def load_geojson():
    brasil = gpd.read_file('brasil.gpkg', layer='limites_estados')
    brasil = brasil.rename(columns={
        'CD_UF':'UF-id',
        'NM_UF':'Estado'
    })
    brasil['geometry'] = brasil['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    return brasil


def mapa_brasil(df, nome):
    geojson = load_geojson()
    m = folium.Map(
        location=[-14.619526, -53.662294],
        tiles='cartodbpositron',
        zoom_start=4.7
    )
    folium.Choropleth(
        geo_data=geojson,
        data=df,
        columns=['Estado', 'Frequencia'],
        key_on='feature.properties.Estado',
        fill_color='OrRd',
        fill_opacity=0.8,
        legend_name=f'Frequência do nome {nome}',
        smooth_factor=0.1
    ).add_to(m)

    return m