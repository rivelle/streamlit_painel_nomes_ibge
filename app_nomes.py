import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import requests


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


def mapa_brasil(df, nome):
    estados = gpd.read_file('br_limites_estados.geojson')
    estados = estados.rename(columns={
        'CD_UF':'UF-id',
        'NM_UF':'Estado'
    })
    m = folium.Map(
        location=[-14.619526, -36.662294],
        tiles='cartodbpositron',
        zoom_start=4.5
    )
    folium.Choropleth(
        geo_data=estados,
        data=df,
        columns=['Estado', 'Frequencia'],
        key_on='feature.properties.Estado',
        fill_color='OrRd',
        fill_opacity=0.8,
        legend_name=f'Frequência do nome {nome}',
    ).add_to(m)    

    st_map = st_folium(m, width=2000, height=970)

    return st_map
    

def main():

    st.set_page_config(layout='wide')   

    with st.sidebar:
        st.title('Web App Nomes')
        st.markdown('Os dados apresentados neste App foram coletados à partir da API Nomes forneceida pelo IBGE*.')
        st.divider()
        st.subheader('Faça sua pesquisa:')
        nome = st.text_input('Digite o nome desejado:', placeholder='Nome').capitalize()
        st.markdown('''**Notas:**  
                    **a)** O resultado apresentado para frequência do nome pesquisado é em relação à proporção por 100.000 habitantes.  
                    **b)** O Censo Demográfico 2010 não considerou nos questionários nomes compostos, apenas o primeiro nome e o último sobrenome. Por essa razão, esta API não retorna resultados ao consultar nomes compostos.  
                    **c)** Quando a quantidade de ocorrências for suficientemente pequena a ponto de permitir a identificação delas, o IBGE não informa essa quantidade. No caso da API de Nomes, a quantidade mínima de ocorrências para que seja divulgado os resultados é de 10 por município, 15 por Unidade da Federação e 20 no Brasil.  
                    -------------------------------  
                    ***Mais informações:** <https://servicodados.ibge.gov.br/api/docs/nomes?versao=2>
                    ''')
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
    df_freq_loc_top10 = df_freq_loc.sort_values(by='Frequencia', ascending=False).head(10)
    

    col01, col02 = st.columns([0.4, 0.8])

    with col01:
        st.subheader(f'Gráficos de Frequência e Rank por Estado para o nome {nome}')
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
        st.subheader(f'Mapa de Frequência do nome {nome} por Estado')
        mapa_brasil(df_freq_loc, nome)
        
        
if __name__=='__main__':
    main()