import streamlit as st
import constants
import pandas as pd
from material import Material
from condensator import Condensator

class CondensatorCounter:
    def __init__(self, number: int):
        self.c0 = 0
        self.condensators = [Condensator(i+1) for i in range(number)]
        self.work_power = 0
        self.ysdop = 0
        self.table = pd.DataFrame({
            'Емкость': [cond.capacity for cond in self.condensators],
            'Мощность': [cond.power for cond in self.condensators],
            'Погрешность': [cond.error for cond in self.condensators]},
            index = [i for i in range(1, len(self.condensators) + 1)])
        self.material_table = Material('diel_materials.json').condensator_df()
        self.kz = st.sidebar.number_input('Укажите коэффициент запаса', min_value=2, max_value=4)


    def choose_material(self):
        return list(self.material_table.loc
                    [st.selectbox('Укажите материал:', self.material_table.index.values)])

    def calc_errors(self, material, temperature):
        self.work_power = st.slider('Укажите рабочее напряжение',
                                   min_value=material[2], max_value=material[3], value=material[2])
        error_ys = st.sidebar.selectbox('Укажите погрешность воспроизведения удельной емкости', [3, 4, 5])
        error_st = st.sidebar.selectbox('Укажите погрешность старения', [2,3])
        ysdop = self.condensators[0].error - error_ys - material[1]*(temperature-20)/100 - error_st
        for condensator in self.condensators:
            condensator.full_error = ysdop
        self.ysdop = ysdop
        d = round(self.work_power * self.kz / material[0] / 100, 2)
        st.text(f'Толщина диэлектрика – {d} мкм')
        c01 = round(0.0885 * material[6] / d * 100, 2)
        st.write(f'C0\' = {c01}')
        capacities = [condensator.capacity for condensator in self.condensators]
        c02 = round(min(capacities) * (ysdop / 0.01) ** 2 / 40000)
        st.write(f'C0\'\' = {c02}')
        c03 = min(capacities) / 2
        st.write(f'C0\'\'\' = {c03}')
        self.c0 = min([c01, c02, c03])
        st.write(f'Таким образом Со = {self.c0}')


    def calc_forms(self):
        for i, condensator in enumerate(self.condensators):
            self.condensators[i].square = round(condensator.capacity / self.c0, 2)
            self.condensators[i].form = 'Перекрытие' \
                if self.condensators[i].square >= 5 else 'Пересечение'

    def forms_table(self):
        st.subheader('Таблица "Площади и формы"')
        table = pd.DataFrame({
            'Площадь': [condensator.square for condensator in self.condensators],
            'Форма': [condensator.form for condensator in self.condensators]},
            index=[i for i in range(1, len(self.condensators)+1)])
        return table

    def count_elements(self, material):
        x_pos = 0
        acad_text = ''
        if self.ysdop < 0:
            st.error('Необходимо выбрать другой материал и/или другие характеристики. Погрешность меньше нуля.')
        else:
            for condensator in self.condensators:
                form_index = constants.condensator_forms.index(condensator.form)
                res_form = st.selectbox(f'Выберите форму конденсатора {condensator.number}. '
                                        f'Рекомендуется {condensator.form}',
                                        options=constants.condensator_forms,
                                        index=form_index)
                if res_form == 'Перекрытие':
                    x_pos = condensator.make_overlap(x_pos)
                elif res_form == 'Пересечение':
                    x_pos = condensator.make_intersection(x_pos)
                acad_text += condensator.acad_text
        return acad_text