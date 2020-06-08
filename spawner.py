import streamlit as st
import base64
from utilities.resistor_counter import ResistorCounter
from utilities.capacitor_counter import CapacitorCounter


class Spawner:
    def __init__(self):
        """
        Base application class unified for
        """
        st.sidebar.header('Параметры схемы')
        self.temperature = st.sidebar.number_input('Укажите максимальную рабочую'
                                                   ' температуру схемы',
                                                   min_value=20, value=40)
        self.type = st.sidebar.selectbox('Укажите тип рассчитываемого элемента',
                                 ['Резисторы', 'Конденсаторы'])
        self.number = st.sidebar.number_input('Укажите количество элементов',
                                              min_value=1,
                                              value=1)

    def get_counter(self):
        if self.type == 'Резисторы':
            counter = ResistorCounter(self.number)
        elif self.type == 'Конденсаторы':
            counter = CapacitorCounter(self.number)
        st.header(f'Таблица "{self.type}"')
        st.table(counter.table)
        st.dataframe(counter.material_table)
        material = counter.choose_material()
        counter.calc_errors(material, self.temperature)
        counter.calc_forms()
        st.table(counter.forms_table())
        text_to_script = counter.count_elements(material)
        b64 = base64.b64encode(text_to_script.encode()).decode()
        st.markdown(
            f'<h2><a href="data:file/scr;base64,{b64}" download="script.scr"> Скачать скрипт</a> (Все нормально, все разрешаем:))</h2>',
            unsafe_allow_html=True)
