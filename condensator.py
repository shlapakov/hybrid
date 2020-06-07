import streamlit as st

from element import Element
from acad import Autocad

class Condensator(Element):
    def __init__(self, number):
        super().__init__(number, 'Конденсатор')
        self.capacity = self.spawn_param_field('Емкость', value=500,
                                               key=f'capacity{self.number}')
        self.acad_text = ''
        self.form = None
        self.square = 0

    def make_overlap(self, x_pos):
        """
        :param x_pos:
        :return:
        """
        acad = Autocad(x_pos)
        a1 = round(self.square ** 0.5, 2)
        st.text(f'Сторона верхней обкладки равна {a1}мм')
        a2 = round(a1 + 0.1, 2)
        st.text(f'Сторона нижней обкладки равна {a2}мм')
        a3 = round(a2 + 0.1, 2)
        st.text(f'Сторона диэлектрика равна {a3}мм')
        self.acad_text = acad.draw_overlap(a1, a2, a3, self.number)
        return x_pos + a3 + 2

    def make_intersection(self, x_pos):
        acad = Autocad(x_pos)
        self.square *= 1.15
        self.square = round(self.square, 2)
        st.text(f'Площадь перекрытия обкладок равна {self.square}')
        a1 = round(self.square ** 0.5, 2)
        st.text(f'Размеры обкладок – {a1}мм')
        a2 = round(a1 + 0.1, 2)
        st.text(f'Размеры диэлектрика – {a2}мм')
        self.acad_text = acad.draw_intersection(a1, a2, self.number)
        return x_pos + a2 + 2