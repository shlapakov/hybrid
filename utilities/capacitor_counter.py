import streamlit as st
from utilities import constants
import pandas as pd
from utilities.material import Material
from elements.capacitor import Capacitor


class CapacitorCounter:
    def __init__(self, number: int):
        """
        Base class to operate w/ capacitors on scheme
        :param number: number of capacitors
        """
        self.c0 = 0
        self.capacitors = [Capacitor(i + 1) for i in range(number)]
        self.work_power = 0
        self.ysdop = 0
        self.table = pd.DataFrame({
            'Емкость': [cond.capacity for cond in self.capacitors],
            'Мощность': [cond.power for cond in self.capacitors],
            'Погрешность': [cond.error for cond in self.capacitors]},
            index = [i for i in range(1, len(self.capacitors) + 1)])
        self.material_table = Material('/materials/diel_materials.json').condensator_df()
        self.kz = st.sidebar.number_input('Укажите коэффициент запаса', min_value=2, max_value=4)


    def choose_material(self) -> list:
        """
        Get material to work w/
        :return: Parameters of chosen material
        """
        return list(self.material_table.loc
                    [st.selectbox('Укажите материал:', self.material_table.index.values)])

    def calc_errors(self, material: list, temperature: int):
        """
        Calculates errors and base capacity
        :param material: dielectric material
        :param temperature: max-working temperature of scheme
        """
        self.work_power = st.slider('Укажите рабочее напряжение',
                                   min_value=material[2], max_value=material[3], value=material[2])
        error_ys = st.sidebar.selectbox('Укажите погрешность воспроизведения удельной емкости', [3, 4, 5])
        error_st = st.sidebar.selectbox('Укажите погрешность старения', [2,3])
        ysdop = self.capacitors[0].error - error_ys - material[1] * (temperature - 20) / 100 - error_st
        for condensator in self.capacitors:
            condensator.full_error = ysdop
        self.ysdop = ysdop
        d = round(self.work_power * self.kz / material[0] / 100, 2)
        st.text(f'Толщина диэлектрика – {d} мкм')
        c01 = round(0.0885 * material[6] / d * 100, 2)
        st.write(f'C0\' = {c01}')
        capacities = [condensator.capacity for condensator in self.capacitors]
        c02 = round(min(capacities) * (ysdop / 0.01) ** 2 / 40000)
        st.write(f'C0\'\' = {c02}')
        c03 = min(capacities) / 2
        st.write(f'C0\'\'\' = {c03}')
        self.c0 = min([c01, c02, c03])
        st.write(f'Таким образом Со = {self.c0}')


    def calc_forms(self):
        """
        Calculate forms for all capacitors
        """
        for i, capacitor in enumerate(self.capacitors):
            self.capacitors[i].square = round(capacitor.capacity / self.c0, 2)
            self.capacitors[i].form = 'Перекрытие' \
                if self.capacitors[i].square >= 5 else 'Пересечение'

    def forms_table(self) -> pd.DataFrame:
        """
        Makes pandas dataframe of forms and squares.
        :return: dataframe
        """
        st.subheader('Таблица "Площади и формы"')
        table = pd.DataFrame({
            'Площадь': [capacitor.square for capacitor in self.capacitors],
            'Форма': [capacitor.form for capacitor in self.capacitors]},
            index=[i for i in range(1, len(self.capacitors) + 1)])
        return table

    def count_elements(self, material) -> str:
        """
        Makes AutoCAD text, calculate all capacitors and print their info.
        :param material:
        :return: full script text
        """
        x_pos = 0
        acad_text = ''
        if self.ysdop < 0:
            st.error('Необходимо выбрать другой материал и/или другие характеристики. Погрешность меньше нуля.')
        else:
            for capacitor in self.capacitors:
                form_index = constants.condensator_forms.index(capacitor.form)
                res_form = st.selectbox(f'Выберите форму конденсатора {capacitor.number}. '
                                        f'Рекомендуется {capacitor.form}',
                                        options=constants.condensator_forms,
                                        index=form_index)
                if res_form == 'Перекрытие':
                    x_pos = capacitor.make_overlap(x_pos)
                elif res_form == 'Пересечение':
                    x_pos = capacitor.make_intersection(x_pos)
                acad_text += capacitor.acad_text
        return acad_text