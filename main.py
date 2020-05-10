import streamlit as st
import pandas as pd
import json
import time

import base64

TKS_TEXT = 'Укажите ТКС'
ERROR_TEXT = 'Укажите погрешность старения'
MASK = 0.3
LITHOGRAPHY = 0.05
method = ...
start_x_point = 0



def data_for_table(data_to_change):
    keys = data_to_change.keys()
    res = []
    for i in keys:
        res.append(data_to_change[i])
    return res


def spawn_resistors_table():
    table = pd.DataFrame({
        'Сопротивление': data_for_table(data[0]),
        'Мощность': data_for_table(data[1]),
        'Погрешность': data_for_table(data[2]),
        'Макc. температура': [max_temperature] * len(data[0])},
        index=[i for i in range(1, len(data[0]) + 1)])
    st.table(table)
    return table


def spawn_field(number, name):
    x = st.sidebar.number_input('{} резистора {}'.format(name, number), 1)
    return x


def spawn_fields():
    st.sidebar.subheader('Параметры резисторов')
    resistances = {}
    powers = {}
    user_errors = {}
    for i in range(number_of_resistors):
        resistance = spawn_field(i + 1, 'Сопротивление')
        resistances[i + 1] = resistance
        power = spawn_field(i + 1, 'Мощность')
        powers[i + 1] = power
        error = spawn_field(i + 1, 'Погрешность')
        user_errors[i + 1] = error
    return [resistances, powers, user_errors]


def spawn_ro_opt():
    global ro_square
    if 0 not in data_for_table(data[0]):
        ro_opt = round((sum(data_for_table(data[0])) / sum([1 / i for i in data_for_table(data[0])])) ** 0.5) // 10 * 10
        st.sidebar.subheader(f'Введите ро квадрат (рекомендуется {ro_opt})')
        ro_square = st.sidebar.number_input('', step=10.0)
    return ro_square


def get_materials():
    with open('materials.json', 'r', encoding='utf-8') as file:
        return json.loads(file.read())


def get_materials_with_r():
    materials = get_materials()
    numbers_of_materials = materials.keys()
    suitable_materials = []
    for number in numbers_of_materials:
        next_material = materials[number]
        if next_material['min_res'] <= ro_square <= next_material['max_res'] and ro_square:
            suitable_materials.append(next_material)
    return suitable_materials


def spawn_material_choice():
    if fit_materials:
        names_of_fit = []
        for i in fit_materials:
            names_of_fit.append(i['name'])
        st.subheader('Выберите подходящий вам материал')
        main_material = st.selectbox('Допустимые материалы:',names_of_fit)
        for i in fit_materials:
            if i['name'] == main_material:
                return i


def check_for_double(min_value, max_value):
    if min_value == max_value:
        return str(min_value)
    else:
        return f'({min_value})-({max_value})'

def spawn_materials_table():
    df = pd.read_json('materials.json')
    df_new = df.rename(index={'name':'Название', 'max_tks':'Макс. ТКС',
                              'min_tks':'Мин. ТКС', 'min_res':'Мин. R',
                              'power':'Удельная мощность', 'max_res':'Макс. R',
                              'min_error':'Мин. погрешность', 'max_error':'Макс. погрешность'})
    st.dataframe(df_new)



def spawn_material_info():

    if ro_square >= 3:
        st.header('Параметры выбранного материала')
        st.text('Сопротивление квадрата резистивной пленки (Ом/кв) - {}'.
                format(check_for_double(material['min_res'], material['max_res'])))
        st.text('Удельная допустимая мощность рассеивания (Вт/См2)- {}'.
                format(material['power']))
        st.text('ТКС - {}'.
                format(check_for_double(material['min_tks'], material['max_tks'])))
        st.text('Погрешность старения -  {}'.
                format(material['min_error'], material['max_error']))


def spawn_some_choice(min_value, max_value, text):
    if ro_square >= 3:
        if min_value != max_value:
            st.sidebar.subheader(text)
            value = st.sidebar.slider('',
                              float(min_value),
                              float(max_value),
                              float(min_value),
                              0.1)
        else:
            value = min_value
        return value


def calc_errors():
    if ro_square >= 3:
        full_errors = []
        for resistor in data_for_table(data[2]):
            error = resistor - 5 - old_error - (tks * 0.01 * (max_temperature - 20)) - contact_error
            full_errors.append(round(error,2))
        return full_errors


def calc_forms_coefs():
    if ro_square >= 3:
        coefs = []
        for resistor in data_for_table(data[0]):
            coefficient = round(resistor / ro_square, 1)
            coefs.append(coefficient)
        return coefs


def spawn_coefficients_and_errors_info():
    if ro_square >= 3:
        st.title('Погрешности и формы')
        forms = []
        for i in form_coefs:
            if 0 < i <= 0.1:
                form = 'ЦКП'
            elif 0.1 < i < 1:
                form = 'Прямоугольный (l<b)'
            elif 1 <= i <= 10:
                form = 'Прямоугольный (l>b)'
            elif 10 < i <= 50:
                form = 'Меандр'
            else:
                form = 'Проводящие перемычки'
            forms.append(form)
        fits = []
        for i in errors:
            if i >= 0:
                fit = 'Нет'
            else:
                fit = 'Да'
            fits.append(fit)
        st.write(pd.DataFrame(
            {'Кф': form_coefs,
             'Рекомендуемая форма': forms,
             'Погрешность': errors,
             'Пригонка': fits},
            index=[i for i in range(1, len(data[0]) + 1)]
        ))
        return [forms, fits]


def rectangle(p, r, p0, kf, ykf, side):
    global start_x_point
    global autocad_text
    bp = ((ro_square * p * 0.001) / (r * p0 * 0.01)) ** 0.5
    b_delta = (0.01 + kf + 0.01) / ykf
    b = round(max(bp, b_delta),2)
    length = round(b * kf, 2)

    if side != 'b':
        b,length = length,b
    st.text(f'Ширина - {b}мм, Длина - {length}мм')
    text_to_add = f'COLOR ByLayer\n' \
                  f'RECTANG {start_x_point},0 {round(b+start_x_point,1)},{length}\n' \
                  f'COLOR RED\n' \
                  f'LINE {round(start_x_point+0.09,2)},0 {round(start_x_point+0.09,2)},{length}\n' \
                  f'X\n' \
                  f'LINE {round(start_x_point+b-0.09,2)},0 {round(start_x_point+b-0.09,2)},{length}\n' \
                  f'X\n'
    # st.text(text_to_add)
    autocad_text += text_to_add
    start_x_point += b+1


def meander(p, r, p0, kf, ykf):
    global start_x_point
    global autocad_text
    start_x_point = round(start_x_point,1)
    bp = ((ro_square * p * 0.001) / (r * p0 * 0.01)) ** 0.5
    b_delta = (0.01 + 0.01 / kf) / ykf
    b = round(max(b_delta, bp), 1)
    l_average = b * kf
    t = b * 2
    n_optimal = int((l_average / t) ** 0.5 + 1)
    # n = st.slider('Укажите количество звеньев. Оптимальное количество: {}'.format(n_optimal),
    #               0, 10, n_optimal)
    length_meandr = round(n_optimal * t, 1)
    width_meandr = round((l_average - b * n_optimal) / 3,1)
    st.text(f'Количество звеньев – {n_optimal}')
    st.text('Длина меандра - {}'.format(length_meandr))
    st.text('Ширина меандра - {}'.format(width_meandr))
    text_to_add = f'COLOR ByLayer\n' \
                  f'LINE {round(start_x_point + b, 1)},0' \
                  f' {round(start_x_point + b,1)},{round(-2*b,1)}' \
                  f' {start_x_point},{round(-2*b,1)}' \
                  f' {start_x_point},{b}\n' \
                  f'X\n' \
                  f'COLOR RED\n' \
                  f'LINE {start_x_point},{-b}' \
                  f' {round(start_x_point+b,1)},{-b}\n' \
                  f'X\n' \
                  f'COLOR ByLayer\n'
    for i in range(n_optimal):
        if i % 2 == 0:
            text_to_add += f'LINE {round(start_x_point + b,1)},{round(i * 2 * b,1)}' \
                      f' {round(start_x_point + length_meandr,1)},{round(i * 2 * b,1)}' \
                      f' {round(start_x_point + length_meandr,1)},{round(i * 2 * b + 3 * b,1)}\n' \
                      f'X\n' \
                      f'LINE {round(start_x_point + length_meandr - b,1)},{round(i * 2 * b + 2 * b,1)}' \
                      f' {round(start_x_point + length_meandr - b,1)},{round(i * 2 * b + b,1)}' \
                      f' {start_x_point},{round(i * 2 * b + b,1)}\n' \
                      f'X\n'
        else:
            text_to_add += f'LINE {round(start_x_point + length_meandr - b,1)},{round(i * 2 * b,1)}' \
                      f' {start_x_point},{round(i * 2 * b,1)}' \
                      f' {start_x_point},{round(i * 2 * b + 3 * b,1)}\n' \
                      f'X\n' \
                      f'LINE {round(start_x_point + length_meandr,1)},{round(i * 2 * b + b,1)}' \
                      f' {round(start_x_point + b,1)},{round(i * 2 * b + b,1)}' \
                      f' {round(start_x_point + b,1)},{round(i * 2 * b + 2*b,1)}\n' \
                      f'X\n'
    if n_optimal % 2 == 1:
        text_to_add += f'LINE {round(start_x_point + length_meandr - b, 1)},{round(n_optimal*2*b,1)}' \
                       f' {round(start_x_point + length_meandr - b, 1)},{round(n_optimal*2*b + b,1)}' \
                       f' {round(start_x_point + length_meandr, 1)},{round(n_optimal*2*b + b,1)}\n' \
                       f'X\n' \
                       f'COLOR RED\n' \
                       f'LINE {round(start_x_point + length_meandr - b, 1)},{round(n_optimal*2*b,1)}' \
                       f' {round(start_x_point + length_meandr, 1)},{round(n_optimal*2*b,1)}\n' \
                       f'X\n' \
                       f'COLOR ByLayer\n'
    else:
        text_to_add += f'LINE {start_x_point},{round(n_optimal*2*b+b,1)}' \
                       f' {round(start_x_point+b,1)},{round(n_optimal*2*b+b,1)}' \
                       f' {round(start_x_point+b,1)},{round(n_optimal*2*b,1)}\n' \
                       f'X\n' \
                       f'COLOR RED\n' \
                       f'LINE {round(start_x_point+b,1)},{round(n_optimal*2*b,1)}' \
                       f' {start_x_point},{round(n_optimal*2*b,1)}\n' \
                       f'X\n' \
                       f'COLOR ByLayer\n'
    autocad_text+= text_to_add
    # st.text(text_to_add)


# def jumpers(r, p, p0, kf):
#     if kf > 10:
#         variant = st.selectbox('Укажите вариант изготовления', ['Вписанный контур', 'Расчет прямоугольника'])
#         if variant == 'Вписанный контур':
#             length = st.number_input('Укажите длину контура', 0.1)
#             width = st.number_input('Укажите ширину контура', 0.1)
#             side_b = (-length * ro_square + (length ** 2 * ro_square ** 2 + r * ro_square * length * width * 2) ** 0.5) / (
#                         r * 2)
#             print(side_b)
#             number_of_jumpers = length / (width * 2)
#             st.text('Ширина резистивной пленки - {}мм'.format(side_b))
#             st.text('Число резистивных полосок - {}'.format(number_of_jumpers // 1))
#         elif variant == 'Расчет прямоугольника':
#             bp = ((ro_square * p * 0.001) / (r * p0 * 0.01)) ** 0.5
#             length = bp * (1 + (1 + kf * 2) ** 0.5)
#             if kf > 20:
#                 length = bp * (kf * 2) ** 0.5
#             number_of_jumpers = length / (2 * length)
#             st.text('Ширина полоски - {}мм'.format(length))
#             st.text('Ширина и длина одинаковы и равны {}мм'.format(length))
#             st.text('Число резистивных полосок - {}'.format(number_of_jumpers))
#     else:
#         st.text('Такой резистор реализовать невозможно')


def sizes():
    if ro_square >= 3:
        for i in range(number_of_resistors):
            res_form = st.selectbox('Выберите форму резистора {} (рекомендуется {})'.
                                    format(i + 1, forms_fits[0][i]),
                                    ['Прямоугольный(l<b)', ' Прямоугольный(1>b)',
                                     'Меандр']) #'Проводящие перемычки'
            if 'Прямоугольный' in res_form:
                rectangle(p=data_for_table(data[1])[i],
                          r=data_for_table(data[0])[i],
                          p0=material['power'],
                          kf=form_coefs[i],
                          ykf=errors[i],
                          side='b' if '(l<b)' in res_form else 'l')
            if res_form == 'Меандр':
                meander(p=data_for_table(data[1])[i],
                        r=data_for_table(data[0])[i],
                        p0=material['power'],
                        kf=form_coefs[i],
                        ykf=errors[i])
            # if res_form == 'Проводящие перемычки':
            #     jumpers(r=data_for_table(data[0])[i],
            #             p=data_for_table(data[1])[i],
            #             p0=material['power'],
            #             kf=form_coefs[i])

autocad_text = ''
st.markdown(f'<h2>'
            f'<a href="https://teletype.in/@mrc/GIS"'
            f'target="_blank">'
            f'База Знаний</a></h2>', unsafe_allow_html=True)
st.sidebar.title('Расчет резисторов')
number_of_resistors = st.sidebar.number_input('Количество резисторов', 1)
max_temperature = st.sidebar.number_input('Максимальная температура ', 40)
data = spawn_fields()
st.title('Таблица резисторов')

spawn_resistors_table()
ro_square = spawn_ro_opt()
# st.image('table.jpg', use_column_width=True)
st.title('Таблица материалов')
spawn_materials_table()
# st.json(get_materials())
fit_materials = get_materials_with_r()
material = spawn_material_choice()
spawn_material_info()
if ro_square >= 3:
    tks = spawn_some_choice(material['min_tks'], material['max_tks'], TKS_TEXT)
    old_error = spawn_some_choice(material['min_error'], material['max_error'], ERROR_TEXT)
st.sidebar.subheader('Укажите погрешность переходных сопротивлений контактов')
contact_error = st.sidebar.selectbox('', [1, 2])
errors = calc_errors()
form_coefs = calc_forms_coefs()
forms_fits = spawn_coefficients_and_errors_info()
st.sidebar.subheader('Выберите метод изготовления микросхемы')
l_tech = st.sidebar.selectbox('', ['Масочный', 'Фотолитография'])
if l_tech == 'Масочный':
    method = MASK
elif l_tech == 'Фотолитография':
    method = LITHOGRAPHY
if material:
    st.subheader('Расчет размеров элементов')
sizes()
# if autocad_text:
#     st.subheader('Скрипт для Автокада')
#     st.text(autocad_text)
st.sidebar.title('Расчет конденсаторов')
number_of_capacitors = st.sidebar.number_input('Количество конденсаторов', 1)

if autocad_text:
    b64 = base64.b64encode(autocad_text.encode()).decode()
    st.markdown(f'<h2><a href="data:file/scr;base64,{b64}" download="script.scr"> Скачать скрипт</a> (Все нормально, все разрешаем:))</h2>', unsafe_allow_html=True)
else:
    st.warning('Ожидание расчетов...')