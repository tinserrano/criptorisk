import streamlit as st
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import yfinance
import datetime

from PIL import Image

image = Image.open("harry.png")
st.image(image, caption = "Harry Markowitz")





'''
# Cartera de Inversion - Frontera de Eficiencia - Markowitz

## Un poco de teoría...

Suposiciones:
1. El riesgo de una cartera se basa en la variabilidad de los rendimientos de dicha cartera.

2. Un inversor es reacio al riesgo.

3. Un inversor prefiere aumentar el consumo.

4. La función de utilidad del inversor es convexa y creciente, debido a su aversión al riesgo y preferencia de consumo.

5. El análisis se basa en un modelo de inversión de un solo período.

6. Un inversor maximiza el rendimiento de su cartera para un nivel de riesgo dado o maximiza su rendimiento por el riesgo mínimo.7​

7. Un inversor es de naturaleza racional.

Para elegir el mejor portafolio entre una cantidad de portafolios posibles, cada uno con diferente rentabilidad y riesgo, se deben tomar dos decisiones por separado:

1. Determinación de un conjunto de carteras eficientes.

2. Selección de la mejor cartera del conjunto eficiente.

Si bien puedes elegir la cartera que desees, aqui te comentamos cuál sería la cartera eficiente en cuanto al Ratio Sharpe (rentabilidad / riesgo) 


&nbsp;&nbsp;&nbsp;&nbsp;



'''


'''
## Cartera de Inversion de CriptoActivos
### Te recomendaremos una cartera de inversión entre las 10 criptomonedas que mayor market cap poseen.
&nbsp;&nbsp;
'''
a = st.multiselect("Elige tus activos para el armado de la cartera (te mostrará datos de los ùltimos 900 dias)",["bitcoin", "ethereum", "binancecoin", "ripple", "usd-coin", "dogecoin", "solana", "cardano", "tether", "tron"])
q_sim = st.slider("Selecciona la cantidad de simulaciones", 4000, 12000,6000)
def precios(symbol):
    url = "https://api.coingecko.com/api/v3/coins/"+symbol+"/market_chart?vs_currency=usd&days=900&interval=daily"
    r = requests.get(url)
    js = r.json()
    df = pd.DataFrame(js)
    df = pd.DataFrame(df["prices"])
    columnas = df["prices"].apply(pd.Series)
    columnas.columns = ["timestamp", symbol]
    df_sep = pd.concat([df, columnas], axis=1)
    df_sep = df_sep.drop("prices", axis=1)
    df_sep["timestamp"] = pd.to_datetime(df_sep["timestamp"], unit="ms")
    return df_sep


if st.button("Ya elegí mis cripto favoritas"):

    bar = st.progress(30)
    time.sleep(2)
    bar.progress(50)
    time.sleep(3)
    bar.progress(95)


    symbols =  a

    # Obtener los datos de Bitcoin como punto de partida
    result_df = precios(symbols[0])

    # Iterar sobre los símbolos (excluyendo Bitcoin) y agregar los valores dentro de las fechas existentes
    for symbol in symbols[1:]:
        df = precios(symbol)
        df = df.rename(columns={"C": symbol})  # Renombrar la columna 'C' con el símbolo correspondiente
        result_df = pd.merge(result_df, df, on="timestamp", how="left")


    #st.dataframe(result_df)

    df_final = result_df.drop("timestamp", axis=1)

    rportafolio = []
    sdportafolio = []
    pesosportafolio = []

    #rendimientos = (df_final - df_final.shift(1)) / df_final.shift(1)
    rendimientos = np.log(df_final / df_final.shift(1))

    import numpy as np

    numero_activos = len(rendimientos.columns)
    numero_activos

    q = q_sim

    for x in range(q):
        pesos = np.random.random(numero_activos)
        pesos /= np.sum(pesos)
        pesosportafolio.append(pesos)
        rportafolio.append(np.dot(rendimientos.mean(), pesos))
        sdportafolio.append(np.dot(pesos.T, np.dot(rendimientos.cov(), pesos)))

    diccionario = {"Rendimientos":rportafolio, "Volatilidad":sdportafolio}
    for contador, ticker in enumerate(rendimientos.columns.tolist()):
        diccionario["Peso Relativo -" + ticker] = [w[contador] for w in pesosportafolio]

    matrizportafolio = pd.DataFrame(diccionario)
    matrizportafolio["sharpe_ratio"] = matrizportafolio["Rendimientos"] / matrizportafolio["Volatilidad"]

    maxvol = matrizportafolio["Volatilidad"].loc[matrizportafolio["sharpe_ratio"].argmax(),]
    maxrend = matrizportafolio["Rendimientos"].loc[matrizportafolio["sharpe_ratio"].argmax(),]

    fig4 = go.Figure(data=go.Scatter(
        x=matrizportafolio["Volatilidad"],
        y=matrizportafolio["Rendimientos"],
        mode='markers',
        marker=dict(
            size=5,
            color= matrizportafolio["sharpe_ratio"], #set color equal to a variable
            colorscale='Viridis', # one of plotly colorscales
            showscale=True
        )
    ))
    
    fig4.add_trace(go.Scatter(
        x = [maxvol],
        y = [maxrend],
        mode = "markers", 
        marker = dict(color="red", symbol="star", size=12),
        name = "Cartera"

    ))

    fig4.update_layout(
        title = "Cartera Eficiente Markowitz",
        width = 2200,
        height = 800
    )
    st.plotly_chart(fig4, theme="streamlit", use_container_width=True)



    optimo = matrizportafolio.loc[matrizportafolio["sharpe_ratio"].argmax()]
    optimochart = optimo.drop(["Rendimientos", "Volatilidad", "sharpe_ratio"], axis=0)
    optimochart = pd.DataFrame(optimochart)
    optimochart = optimochart.T
    
    plt.pie(optimochart.iloc[0,:], labels=optimochart.columns, autopct='%1.1f%%', startangle=140)

    fig3 = px.pie(values=optimochart.iloc[0,:], names=optimochart.columns, title="Distribucion de Inversion según ratio Sharpe")
    st.plotly_chart(fig3, theme="streamlit")



    result_df.set_index('timestamp', inplace=True) 
    # st.write(result_df)
    initial_values = result_df.iloc[0]  # Valores iniciales de todas las criptomonedas
    df_percentage = (((result_df / initial_values)) - 1) * 100
    df_percentage_columns = df_percentage.columns
    
    # st.write("columns")
    # st.write(df_percentage_columns)


    df_partes_iguales = pd.DataFrame(df_percentage[df_percentage_columns].sum(axis=1) / len(df_percentage_columns), columns=["partes_iguales"])
    #st.write(df_partes_iguales.tail())

    pesos = optimochart.values
    df_cartera_optima = df_percentage[df_percentage_columns].mul(pesos)
    df_cartera_optima_sum = pd.DataFrame(df_cartera_optima.sum(axis=1), columns=["cartera_optima"])

    df_partes_iguales = df_partes_iguales.iloc[:-1]
    df_cartera_optima_sum = df_cartera_optima_sum.iloc[:-1]
    #st.write(df_cartera_optima_sum.tail())


    merged_df = df_partes_iguales.merge(df_cartera_optima_sum, left_index=True, right_index=True, suffixes=('_partes_iguales', '_optima'))



    start = merged_df.index[0]
    finish = merged_df.index[-1]

    data = yfinance.download('spy', start=start, end=finish)
    dataClose = pd.DataFrame(data["Close"])

    merged_df.index = pd.to_datetime(merged_df.index)
    dataClose.index = pd.to_datetime(dataClose.index)

    dataClose_aligned = dataClose.reindex(merged_df.index)

    merged_df = merged_df.merge(dataClose_aligned, left_index=True, right_index=True, how="left")

    merged_df.dropna(inplace=True)

    merged_df["RendimientoSPY"] = (merged_df["Close"] / merged_df["Close"].iloc[0]) - 1
    merged_df = merged_df.drop(['Close'], axis=1)

    fig5 = px.line(merged_df, x=merged_df.index, y=['partes_iguales', 'cartera_optima', 'RendimientoSPY'],
              labels={'value': 'Rendimiento', 'variable': 'Tipo de Rendimiento'},
              title='Comparación de Rendimientos a lo largo del tiempo')

    # Personaliza el diseño del gráfico si lo deseas
    fig5.update_layout(xaxis_title='Fecha', 
                       yaxis_title='Rendimiento',
                        width = 2700, height = 600)
    st.plotly_chart(fig5, theme="streamlit", use_container_width=True)

    
    rendimientoSPY = merged_df['RendimientoSPY'].iloc[-1]
    volspy = np.sqrt(np.sum(np.square(merged_df['RendimientoSPY'].std())))

    st.write(f"Rendimiento SPY: :red[{rendimientoSPY:.2f}]")
    st.write(f"Vol Rendimiento SPY: :red[{volspy:.2f}]")

    rendimientoigual = merged_df['partes_iguales'].iloc[-1]
    voligual = np.sqrt(np.sum(np.square(merged_df['partes_iguales'].std())))
    
    st.write(f"Rendimiento Pesos Iguales: :blue[{rendimientoigual:.2f}]")
    st.write(f"Vol Cartera con Pesos Iguales: :blue[{voligual:.2f}]")

    rendimientooptima = merged_df['cartera_optima'].iloc[-1]
    volop = np.sqrt(np.sum(np.square(merged_df['cartera_optima'].std())))
    st.write(f"Rendimiento Cartera Optima: :green[{rendimientooptima:.2f}]")
    st.write(f"Vol Cartera Optima: :green[{volop:.2f}]")

    st.title("")
    st.title("")
    '''
    ### Si quieres llevarte los % de cartera, te lo dejamos en formato tabla para que lo copies y pegues en tu excel, googlesheets, papelito, en la mano :smirk: "
    &nbsp;&nbsp;
    '''
    st.dataframe(optimochart, use_container_width=True)

    
    '''
    &nbsp;
    #### Disclaimer
    ##### Disclaimer: La presente sólo tiene fines didácticos. No es para nada una recomendación de compra. Has tu propia investigación. DYOR
    &nbsp;&nbsp;
    '''


    st.title("")



    st.title("Contáctame")
    '''
        [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/tinserrano) 

        [![Medium](https://badgen.net/badge/Medium/Link?icon=https://simpleicons.now.sh/medium&label?color=black)](https://medium.com/@tinsonico) 
        
        [![Linkedin](https://badgen.net/badge/Linkedin/Here?icon=https://simpleicons.now.sh/linkedin&label?color=black)](https://www.linkedin.com/in/martinepenas/)
    '''
    st.markdown("<br>",unsafe_allow_html=True)



else:
    st.write("Aqui aparecerá tu recomendación de cartera")



