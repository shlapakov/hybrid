import streamlit as st

from elements.element import Element
from utilities.acad import Autocad



class Resistor(Element):
    def __init__(self, number: int):
        """
        Class to calculate resistors
        :param number: positional number of resistor
        """
        super().__init__(number, 'Резистор')
        self.adjust = None
        self.form_coef = None
        self.form = None
        self.full_error = None
        self.resistance = self.spawn_param_field('Сопротивление', value=1000,
                                                 key=f'resistance{self.number}')
        self.acad_text = ''

    def make_rectangle_b_more(self, ro_square: float, mat_power: float, x_pos: float) -> float:
        """
        Calculate rectangle-based resistor that width is bigger than length.
        :param ro_square: ro_square of material
        :param mat_power: material power
        :param x_pos: bottom-left point of element at AutoCAD sheet
        :return: x_pos for next element
        """
        acad = Autocad(x_pos)
        bp = ((ro_square * self.power * 0.001) /
              (self.resistance * mat_power * 0.01)) ** 0.5
        b_delta = (0.01 / self.form_coef + 0.01) / self.full_error * 100
        b = round(max(bp, b_delta), 2)
        length = round(b * self.form_coef, 2)
        st.text(f'Ширина резистора – {b}\nДлина резистора – {length}')
        self.acad_text = acad.draw_rectangle(b, length, self.number)
        return x_pos + b + 2

    def make_rectangle_l_more(self, ro_square: float, mat_power: float, x_pos: float) -> float:
        """
        Calculate rectangle-based resistor that width is smaller than length.
        :param ro_square: ro_square of material
        :param mat_power: material power
        :param x_pos: bottom-left point of element at AutoCAD sheet
        :return: x_pos for next element
        """
        acad = Autocad(x_pos)
        bp = ((self.resistance * self.power * 0.001) /
              (ro_square * mat_power * 0.01)) ** 0.5
        b_delta = (0.01 * self.form_coef * 0.01) / self.full_error * 100
        b = round(max(bp, b_delta), 2)
        length = round(b * self.form_coef, 2)
        st.text(f'Длина резистора – {b}\nШирина резистора – {length}')
        self.acad_text = acad.draw_rectangle(b, length, self.number)
        return x_pos + length + 2


    def make_meandr(self, ro_square: float, mat_power: float, x_pos: float) -> float:
        """
        Calculate meander-based resistor that width is smaller than length.
        :param ro_square: ro_square from scheme
        :param mat_power: estimated power of material
        :param x_pos: position of aCAD cursor
        :return: x position to next resistor
        """
        acad = Autocad(x_pos)
        bp = ((ro_square * self.power * 0.001) /
              (self.resistance * mat_power * 0.01)) ** 0.5
        b_delta = (0.01 + 0.01 / self.form_coef) / self.full_error * 100
        b = round(max(b_delta, bp), 2)
        l_average = b * self.form_coef
        t = b * 2
        n_optimal = int((l_average / t) ** 0.5 + 1)
        length = round(n_optimal * t, 1)
        width = round((l_average - b * n_optimal) / 3, 1)
        st.text(f'Количество звеньев – {n_optimal}')
        st.text(f'Длина меандра – {length}')
        st.text(f'Ширина меанда – {width}')
        self.acad_text = acad.draw_meander(b, n_optimal, length, self.number)

        return x_pos + b + 2
