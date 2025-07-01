# Web App Nomes

App desenvolvido em Streamlit à partir de exercício prático durante curso Criando Aplicativos Web com Streamlit realizado pela Asimov Academy.

Originalmente a atividade prática de desenvolvimento tinha como objetivo desenvolver um painel para apresentação dos dados da API Nomes do IBGE. À partir daí, optei por complementar o projeto com a geração de um mapa que ilustrasse a distribuição espacial das freqências dos nomes obitdos na pesquisa realizada pelo IBGE.

O app está estruturado basicamente à partir da integração com a API Nomes e Localidades do IBGE, onde são feitas as consultas. Os dados consultados são tratados e apresentados em dois gráficos (Frequência por Década e Rank por Estado), além do mapa mostrando a distribuição total da frequência por Estado.

O projeto foi todo desenvolvido em Python com uso das bibliotecas:
- Streamlit
- Pandas
- Geopandas
- Plotly
- Folium