# the program takes data from server and shows plots and histograms about weather in Moscow
#все библиотеки

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import requests
import json
import numpy as np

""" инструкции к использованию 
    не вбивать слишком большой интервал 1-3 дня оптимально, т.к. долго грузит запрос
    не вбивать дату начала, большую даты конца иногда json не успевает загрузиться за интервал обновления (dcc.interval)
    """

"""функция которая далее будет округлять данные для графика нужным образом не обращать внимания, вернетесь потом"""

def okruglit(type, y_arr, x_arr):

    n = 40  # примерно 40 отметок прибор длеает в час
    if type == '1':
        # оставляем данные как есть
        return (y_arr, x_arr)
    if type == '2':
        # берем среднее из 40 отметок в час - оклругление за час
        return ([np.mean(y_arr[i:i+n]) for i in range(0, len(y_arr), n)],
                [x_arr[i] for i in range(0, len(x_arr), 12)])
    if type == '3':
        # то же самое только с промежуком в 3 раза больше
        return ([np.mean(y_arr[i:i + n*3]) for i in range(0, len(y_arr), n*3)],
                [x_arr[i] for i in range(0, len(x_arr), 36)])
    if type == '4':
        # в 24 раза больше - округление за день
        return ([np.mean(y_arr[i:i + n*24]) for i in range(0, len(y_arr), n*24)],
                [x_arr[i] for i in range(0, len(x_arr), 18*24)])
    if type == '5':
        # min то же самое
        return ([np.min(y_arr[i:i + n*24]) for i in range(0, len(y_arr), n*24)],
                [x_arr[i] for i in range(0, len(x_arr), 18*24)])
    if type == '6':
        # max то же самое
        return ([np.max(y_arr[i:i + n*24]) for i in range(0, len(y_arr), n*24)],
                [x_arr[i] for i in range(0, len(x_arr), 18 * 24)])


"""штука из методички которая как я понял берет данные с сервера"""

def get_html_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }

    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        html = None
    else:
        if r.ok:
            html = r.text
    return html


"""эти запросы нам дальше не пригодятся, но они нужны чтобы узнать все колонки у приборов, например температура влажность и тд"""

#  ссылка берет данные за последние 5 минут с прибора студия, можете забить в браузер и посмотреть что будет
URL = "http://webrobo.mgul.ac.ru:3000/db_api_REST/calibr/last5min/Тест%20Студии/schHome"
data_studio = get_html_page(URL)
data_studio = json.loads(data_studio)

#  то же самое только для роса
URL = "http://webrobo.mgul.ac.ru:3000/db_api_REST/calibr/last5min/РОСА%20К-2/01"
data_rosa = get_html_page(URL)
data_rosa = json.loads(data_rosa)


"""тоже штука из методички"""
"""состоит из визуальных элементов, которые отражаются на сервере(всё что в layout html) и то как они взаимодействуют
 с пользователем(callbacks)"""

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1(children='chart'),

                                html.H4(children='прибор'),
                                #  тут всё как в html, можете украсить, добавить своих надписей

                                #  меню для выбора прибора
                                dcc.Dropdown(
                                    options=[
                                        {'label': 'Тест студии', 'value': 'Тест%20Студии/schHome'},
                                        {'label': u'РОСА К-2', 'value': 'РОСА%20К-2/01'}
                                    ],
                                    value='',
                                    id='device'
                                ),

                                html.H4(children='выбрать параметры для росы'),

                                #  меню выбора параметров для росы, параметры генерируются автоматически из URL выше,
                                #  см. строка где-то 60я
                                dcc.Dropdown(
                                    id='rosa features',
                                    options=[{'label': i, 'value': i} for i in
                                             data_rosa[list(data_rosa.keys())[0]]['data'].keys()],
                                    value=''
                                ),

                                html.H4(children='выбрать параметры для студии'),

                                # меню выбора параметров для студии
                                dcc.Dropdown(
                                    id='studio features',
                                    options=[{'label': i, 'value': i} for i in
                                             data_studio[list(data_studio.keys())[0]]['data'].keys()],
                                    value=''
                                ),

                                html.H4(children='округление'),

                                #меню округления, выбирает тип округления, который передастся в метод okrugl см. выше
                                dcc.Dropdown(
                                    id='okrugl',
                                    options=[{'label': 'как есть', 'value': '1'},
                                             {'label': 'среднее за час', 'value': '2'},
                                             {'label': 'среднее за 3 часа', 'value': '3'},
                                             {'label': 'среднее за сутки', 'value': '4'},
                                             {'label': 'среднее за сутки', 'value': '4'},
                                             {'label': 'min за сутки', 'value': '5'},
                                             {'label': 'max за сутки', 'value': '6'}],
                                    value=''
                                ),

                                html.H4(children='даты начала и конца периода'),

                                #дата начала и конца нашего запроса подробнее далее
                                dcc.Input(id='date_start',
                                          placeholder='2020-12-12 13:12:24'),

                                dcc.Input(id='date_end',
                                          placeholder='2020-12-12 13:14:24'),

                                html.H4(children='год-месяц-день часы-минуты-секунды, например, 2019-08-19 13:12:24, 2019-08-20 14:45:24'),

                                #3 графика
                                dcc.Graph(
                                    id='chart',
                                ),

                                dcc.Graph(
                                    id='barplot',
                                ),

                                dcc.Graph(
                                    id='scatter',
                                ),

                                # интервал - период обновления, в данной версии раз в 3 секунды, можно менять,
                                # но смотрите чтобы данные успевали загрузиться

                                dcc.Interval(id='chart-update',
                                             interval=20 * 1000,
                                             max_intervals=-1)
                                ])

"""далее вы увидите 3 примерно одинаковых куска кода, это нужно для обновления трех графиков,
    т.к. dash поддерживает только один output в callback"""

"""Callback это такая штука которая описывает событие при работе кода,
    например мы выбрали дату начала и конца, прибор и параметр, который хотим отобразить,
    это всё вы можете увидеть в графе Input, обратите внимание, что в инпуте прописаны id всех элементов представленных 
    выше в html"""

"""1"""

@app.callback(Output('chart', 'figure'),
              [Input('device', 'value'),
               Input('rosa features', 'value'),
               Input('studio features', 'value'),
               Input('date_start', 'value'),
               Input('date_end', 'value'),
               Input('okrugl', 'value')])
#  параметры Input передаются в функцию по порядку в виде выбранного текста
def update_graph(device, rosa_features, studio_features, date_start, date_end, okr):
    #например выведем один параметр
    print(date_start)

    # device - выбранный прибор
    # исходя из двух вариантов (роса или студия) нужно выбрать параметры для росы или студии, пригодятся позже
    # параметр берется из выпадающего меню

    if device == 'РОСА%20К-2/01':
        feature = rosa_features

    if device == 'Тест%20Студии/schHome':
        feature = studio_features

    # далее создадим запрос в систему(см. документацию из методички), получаем кусок данных в формате json прямо с сайта
    # для указанной даты и нужного прибора
    URL = "http://webrobo.mgul.ac.ru:3000/db_api_REST/calibr/log/" + date_start.replace(' ', '%20') + '/' + date_end.replace(' ', '%20') + '/' + device
    # на всякий случай выведем, можете вставить в браузер
    print(URL)

    # преобразуем из текста в json(табличка с данными) грубо говоря
    data = get_html_page(URL)
    data = json.loads(data)

    # график будет строиться на основе двух осей y - значение, x - дата
    x_arr = []
    y_arr = []

    for item in data:
        # добавляем дату в один столбец, нужный нам параметр feature в другой см. выше
        x_arr.append(data[item]['Date'])
        y_arr.append(float(data[item]['data'][feature]))

    # после того как оси готовы, (можете вывести и посмотреть), займемся округлением за нужный период
    # okruglit см. самое начало
    y_arr , x_arr = okruglit(okr, y_arr, x_arr)

    # строим график с помощью специальной библиотеки

    traces = list()
    traces.append(plotly.graph_objs.Scatter(
        x=x_arr,
        y=y_arr,
        name='Scatter',
        mode='lines+markers'
    ))

    return {'data': traces}

# остальные 2 графика сделаны по такому же принципу и меняется только сам тип

"""2"""

@app.callback(Output('barplot', 'figure'),
              [Input('device', 'value'),
               Input('rosa features', 'value'),
               Input('studio features', 'value'),
               Input('date_start', 'value'),
               Input('date_end', 'value'),
               Input('okrugl', 'value')])
def update_barplot(device, rosa_features, studio_features, date_start, date_end, okr):
    print(date_start)

    if device == 'РОСА%20К-2/01':
        feature = rosa_features

    if device == 'Тест%20Студии/schHome':
        feature = studio_features

    URL = "http://webrobo.mgul.ac.ru:3000/db_api_REST/calibr/log/" + date_start.replace(' ', '%20') + '/' + date_end.replace(' ', '%20') + '/' + device
    print(URL)

    data = get_html_page(URL)
    data = json.loads(data)

    x_arr = []
    y_arr = []

    for item in data:
        x_arr.append(data[item]['Date'])
        y_arr.append(float(data[item]['data'][feature]))

    y_arr, x_arr = okruglit(okr, y_arr, x_arr)

    traces = list()
    traces.append(plotly.graph_objs.Bar(
        x=x_arr,
        y=y_arr
    ))
    return {'data': traces}


"""3"""


@app.callback(Output('scatter', 'figure'),
              [Input('device', 'value'),
               Input('rosa features', 'value'),
               Input('studio features', 'value'),
               Input('date_start', 'value'),
               Input('date_end', 'value'),
               Input('okrugl', 'value')])
def update_scatter(device, rosa_features, studio_features, date_start, date_end, okr):
    print(date_start)

    if device == 'РОСА%20К-2/01':
        feature = rosa_features

    if device == 'Тест%20Студии/schHome':
        feature = studio_features

    URL = "http://webrobo.mgul.ac.ru:3000/db_api_REST/calibr/log/" + date_start.replace(' ', '%20') + '/' + date_end.replace(' ', '%20') + '/' + device
    print(URL)

    data = get_html_page(URL)
    data = json.loads(data)

    x_arr = []
    y_arr = []

    for item in data:
        x_arr.append(data[item]['Date'])
        y_arr.append(float(data[item]['data'][feature]))

    y_arr, x_arr = okruglit(okr, y_arr, x_arr)

    traces = list()
    traces.append(plotly.graph_objs.Scatter(
        x=x_arr,
        y=y_arr,
        name='Scatter',
        mode='markers'
    ))
    return {'data': traces}

if __name__ == '__main__':
    app.run_server(debug=True)
