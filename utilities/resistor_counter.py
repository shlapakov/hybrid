import streamlit as st
from utilities import constants
import pandas as pd
from elements.resistor import Resistor
from utilities.material import Material

class ResistorCounter:
    def __init__(self, number: int):
        """
        Base class to operate w/ resistors on scheme
        :param number: number of resistors
        """
        self.ro_square = st.sidebar.number_input('Укажите ро квадрат', min_value=3, step=1,
                                                 value=1000)
        self.resistors = [Resistor(i+1) for i in range(number)]
        self.optimal_param = int(round((sum([res.resistance for res in self.resistors]) /
                                        sum([1/res.resistance for res in self.resistors])) **
                                       0.5))
        self.table = pd.DataFrame({
            'Сопротивление': [resistor.resistance for resistor in self.resistors],
            'Мощность': [resistor.power for resistor in self.resistors],
            'Погрешность': [resistor.error for resistor in self.resistors]},
            index=[i for i in range(1, len(self.resistors)+1)])
        st.warning(f'Рекомендуемое значение ро квадрат {self.optimal_param}')
        self.material_table = Material('/materials/resist_materials.json').resistance_df()
        self.acad_text = ''


    def choose_material(self) -> list:
        """
        Get material to work w/
        :return: Parameters of chosen material
        """

        fit_materials = self.material_table.loc[
            (self.material_table['Мин. R'] <= self.ro_square) &
            (self.ro_square <= self.material_table['Макс. R'])]

        return list(self.material_table.loc[st.selectbox('Укажите материал:',
                         fit_materials.index.values)])

    def calc_errors(self, material: list, temperature: int):
        """
        Calculates full-errors for each resistor
        :param material: dielectric material
        :param temperature: max-working temperature of scheme
        """
        old_error = st.selectbox('Укажите погрешность старения', [1,2])
        if material[-4] != material[-3]:
            tks = st.slider(label='Укажите ТКС',
                            min_value=material[-4], max_value=material[-3],
                            value=material[-4])
        else: tks = material[-3]
        if material[-1] != material[-2]:
            contact_error = st.slider(label='Укажите погрешность переходных контактов',
                                      min_value=material[-2], max_value=material[-1])
        else: contact_error = material[-2]
        for i, resistor in enumerate(self.resistors):
            self.resistors[i].full_error = resistor.error - 5 - old_error - \
            (tks * 0.01 * (temperature-20)) - contact_error
            if self.resistors[i].full_error < 0:
                self.resistors[i].adjust = True
            else: self.resistors[i].adjust = False

    def calc_forms(self):
        """
        Calculate forms for all resistors
        """
        for i, resistor in enumerate(self.resistors):
            self.resistors[i].form_coef = round(resistor.resistance / self.ro_square, 2)
            if self.resistors[i].form_coef < 1:
                self.resistors[i].form = 'Прямоугольный (l<b)'
            elif 1 <= self.resistors[i].form_coef <= 10:
                self.resistors[i].form = 'Прямоугольный (l>b)'
            else:
                self.resistors[i].form = 'Меандр'

    def forms_table(self) -> pd.DataFrame:
        """
        Makes pandas dataframe of forms, form coefficietns and errors.
        :return: dataframe
        """
        st.subheader('Таблица "Формы и погрешности"')
        table = pd.DataFrame({
            'КФ': [res.form_coef for res in self.resistors],
            'Рекомендуемая форма': [res.form for res in self.resistors],
            'Погрешность': [res.full_error for res in self.resistors],
            'Пригонка': ['Да' if res.full_error < 0 else 'Нет' for res in self.resistors]},
            index=[i for i in range(1, len(self.resistors) + 1)])
        return table

    def count_elements(self, material: list) -> str:
        """
        Makes AutoCAD text, calculate all resistors and print their info.
        :param material: list-based parameters of selected material
        :return: full script text
        """

        x_pos = 0
        acad_text = ''
        for resistor in self.resistors:
            if resistor.adjust:
                st.error(f'Резистор номер {resistor.number} с подгонкой.'
                           f'Необходимы ручные расчеты ')
            else:
                form_index = constants.resistor_forms.index(resistor.form)
                res_form = st.selectbox(f'Выберите форму резистора {resistor.number}. '
                                        f'Рекомендуется {resistor.form}',
                                        options=constants.resistor_forms,
                                        index=form_index)
                if res_form == 'Прямоугольный (l<b)':
                    x_pos = resistor.make_rectangle_b_more(self.ro_square,
                                                           material[2],
                                                           x_pos)
                elif res_form == 'Прямоугольный (l>b)':
                    x_pos = resistor.make_rectangle_l_more(self.ro_square,
                                                           material[2],
                                                           x_pos)
                elif res_form == 'Меандр':
                    x_pos = resistor.make_meandr(self.ro_square, material[2], x_pos)
                st.text(resistor.acad_text)
                acad_text += resistor.acad_text
        return acad_text