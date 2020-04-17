import streamlit as st
import pandas as pd
import json
import time

TKS_TEXT = 'Укажите ТКС'
ERROR_TEXT = 'Укажите погрешность старения'
MASK = 0.3
LITHOGRAPHY = 0.1
method = ...


def data_for_table(data_to_change):
    keys = data_to_change.keys()
    res = []
    for i in keys:
        res.append(data_to_change[i])
    return res


def spawn_resistors_table():
    st.write(pd.DataFrame({
        'Номер резистора': [i for i in range(1, len(data[0]) + 1)],
        'Сопротивление': data_for_table(data[0]),
        'Мощность': data_for_table(data[1]),
        'Погрешность': data_for_table(data[2]),
        'Макc. температура': [max_temperature] * len(data[0])
    }))


def spawn_field(number, name):
    x = st.number_input('{} резистора {}'.format(name, number), 1)
    return x


def spawn_fields():
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
        ro_opt = (sum(data_for_table(data[0])) / sum([1 / i for i in data_for_table(data[0])])) ** 0.5
        ro_square = st.number_input('Введите ро квадрат (рекомендуется {})'.format(ro_opt))
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
        main_material = st.selectbox('Выберите подходящий вам материал', names_of_fit)
        for i in fit_materials:
            if i['name'] == main_material:
                return i


def check_for_double(min_value, max_value):
    if min_value == max_value:
        return str(min_value)
    else:
        return '[({})-({})]'.format(min_value, max_value)


def spawn_material_info():
    if ro_square >= 3:
        st.text('Сопротивление квадрата разистивной пленки (Ом/кв) - {}'.
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
            value = st.slider(text,
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
            full_errors.append(error)
        return full_errors


def calc_forms_coefs():
    if ro_square >= 3:
        coefs = []
        for resistor in data_for_table(data[0]):
            coefficient = resistor / ro_square
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
            elif 10 < i <= 20:
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
            {'Номер': [i for i in range(1, len(data[0]) + 1)],
             'Кф': form_coefs,
             'Форма': forms,
             'Погрешность': errors,
             'Пригонка': fits}
        ))
        return [forms, fits]


def rectangle(p, r, p0, kf, ykf, side):
    bp = ((ro_square * p * 0.001) / (r * p0 * 0.01)) ** 0.5
    print(ro_square, p, r, p0)
    b_delta = (0.01 + kf + 0.01) / ykf
    length = max(bp, b_delta) * kf
    if side == 'b':
        st.text('Ширина - {}мм, Длина - {}мм'.format(max(bp, b_delta), length))
    else:
        st.text('Длина - {}мм, Ширина - {}мм'.format(max(bp, b_delta), length))


def meander(p, r, p0, kf, ykf):
    bp = ((ro_square * p * 0.001) / (r * p0 * 0.01)) ** 0.5
    b_delta = (0.01 + 0.01 / kf) / ykf
    b = max(b_delta, bp)
    a = b
    print(bp)
    l_average = b * kf
    t = a + b
    n_optimal = int((l_average / t) ** 0.5 + 1)
    n = st.slider('Укажите количество звеньев. Оптимальное количество: {}'.format(n_optimal),
                  0, 10, n_optimal)
    length_meandr = n * (a + b)
    width_meandr = (l_average - a * n) / 3
    st.text('Длина меандра - {}'.format(length_meandr))
    st.text('Ширина меандра - {}'.format(width_meandr))


def jumpers(r, p, p0, kf):
    variant = st.selectbox('Укажите вариант изготовления', ['Вписанный контур', 'Расчет прямоугольника'])
    if variant == 'Вписанный контур':
        length = st.number_input('Укажите длину контура', 1)
        width = st.number_input('Укажите ширину контура', 1)
        side_b = (-length * ro_square + (length ** 2 * ro_square ** 2 + r * ro_square * length * width * 2) ** 0.5) / (
                    r * 2)
        number_of_jumpers = length / (width * 2)
        st.text('Ширина резистиваной пленки - {}мм'.format(side_b))
        st.text('Число резистивных полосок - {}'.format(number_of_jumpers // 1))
    elif variant == 'Расчет прямоугольника':
        bp = ((ro_square * p * 0.001) / (r * p0 * 0.01)) ** 0.5
        if kf > 20:
            length = bp * (kf * 2) ** 0.5
        else:
            length = bp * (1 + (1 + kf * 2) ** 0.5)
        width = length
        number_of_jumpers = length / (2 * width)
        st.text('Ширина полоски - {}мм'.format(width))
        st.text('Ширина и длина одинаковы и равны {}мм'.format(length))
        st.text('Число резистивных полосок - {}'.format(number_of_jumpers))


def sizes():
    if ro_square >= 3:
        for i in range(number_of_resistors):
            res_form = st.selectbox('Выберите форму резистора {} (рекомендуется {})'.
                                    format(i + 1, forms_fits[0][i]),
                                    ['Прямоугольный(l<b)', ' Прямоугольный(1>b)',
                                     'Меандр', 'Проводящие перемычки'])
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
            if res_form == 'Проводящие перемычки':
                jumpers(r=data_for_table(data[0])[i],
                        p=data_for_table(data[1])[i],
                        p0=material['power'],
                        kf=form_coefs[i])


st.title('Расчет резисторов')
number_of_resistors = st.number_input('Количество резисторов', 1)
max_temperature = st.number_input('Максимальная температура ', 40)
data = spawn_fields()
spawn_resistors_table()
ro_square = spawn_ro_opt()
st.image('table.jpg', use_column_width=True)
fit_materials = get_materials_with_r()
material = spawn_material_choice()
spawn_material_info()
if ro_square >= 3:
    tks = spawn_some_choice(material['min_tks'], material['max_tks'], TKS_TEXT)
    old_error = spawn_some_choice(material['min_error'], material['max_error'], ERROR_TEXT)
contact_error = st.selectbox('Укажите погрешность переходных сопротивлений контактов', [1, 2])
errors = calc_errors()
form_coefs = calc_forms_coefs()
forms_fits = spawn_coefficients_and_errors_info()
l_tech = st.selectbox('Выберите метод изготовления микросхемы ', ['Масочный', 'Фотолитография'])
if l_tech == 'Масочный':
    method = MASK
elif l_tech == 'Фотолитография':
    method = LITHOGRAPHY
sizes()
