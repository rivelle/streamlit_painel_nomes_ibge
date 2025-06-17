import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from pprint import pprint


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
        # print(dados)
        id_estado = int(dados['localidade'])
        frequencia = dados['res'][0]['proporcao']
        dict_frequencias[id_estado] = frequencia
    return dict_frequencias


def pegar_nome_por_decada(nome):
    url = f'https://servicodados.ibge.gov.br/api/v2/censos/nomes/{nome}'
    dados_decada = fazer_request(url=url)
    if not dados_decada:
        return {}
    # pprint(dados_decada)
    dict_decadas = {}
    for dados in dados_decada[0]['res']:
        decada = dados['periodo']
        quantidade = dados['frequencia']
        dict_decadas[decada] = quantidade
    return dict_decadas


def mapa(df):
    estados = json.load('brazil_geo.json')

    fig = px.choropleth_map(df,
                            geojson=estados,
                            locations='name',
                            color='Frequencia',
                            color_continuous_scale='Viridis',
                            map_style='carto-positron',
                            zoom=3,
                            center= {'lat':-12.619526, 'long':-50.662294},
                            opacity=0.5,
                            )
    fig.show()

    return fig



def main():

    st.set_page_config(layout='wide')
    st.title('Web App Nomes')
    st.write('Dados do IBGE')

    with st.sidebar:
        nome = st.text_input('Pesquise por um nome:').capitalize()
        if not nome:
            st.stop()

    dict_estados = pegar_ids_estados()
    if not dict_estados:
        st.warning(f'Nenhum dado encontrado para o nome {nome}')
        st.stop()

    dict_frequencia = pegar_frequencia_nome_por_estado(nome)
    if not dict_frequencia:
        st.warning(f'Nenhum dado encontrado para o nome {nome}')
        st.stop()
    # pprint(dict_estados)
    # print(f'Fequência do nome {nome} nos Estados (por 100.000 habitantes)')
    for id_estado, nome_estado in dict_estados.items():
        frequencia_estado = dict_frequencia[id_estado]
        # print(f'--> {nome_estado}: {frequencia_estado}')

    dict_decada = pegar_nome_por_decada(nome)
    if not dict_decada:
        st.warning(f'Nenhum dado encontrado para o nome {nome}')
        st.stop()
    # pprint(dict_decada)

    df = pd.DataFrame.from_dict(dict_decada, orient='index')

    df_localidades = pd.DataFrame.from_dict(dict_estados, orient='index')
    df_localidades = df_localidades.reset_index()
    df_localidades = df_localidades.rename(columns={0:'Estado', 'index':'UF-id'})

    df_frequencia = pd.DataFrame.from_dict(dict_frequencia, orient='index')
    df_frequencia = df_frequencia.reset_index()
    df_frequencia = df_frequencia.rename(columns={0:'Frequencia', 'index':'UF-id'})

    df_freq_loc = df_localidades.merge(df_frequencia, left_on='UF-id', right_on='UF-id', how='left')



    col01, col02 = st.columns([0.5, 0.7])

    with col01:
        st.subheader(f'Frequência do nome {nome} por década')
        st.dataframe(df)

    with col02:
        st.subheader(f'Evolução no tempo dos registros do {nome} por década')
        st.line_chart(df)

    # st.write(df_localidades)
    # st.write(df_frequencia)
    st.write(df_freq_loc)
    mapa(df=df_freq_loc)


if __name__=='__main__':
    main()