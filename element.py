import streamlit as st

class Element:
    def __init__(self, number: int = 0, name: str = '', x_pos: float = 0.0):
        self.number = number
        self.name = name
        st.sidebar.subheader(f'{self.name} номер {self.number}')
        self.power = self.spawn_param_field('Мощность',
                                            key=f'power{self.number}')
        self.error = self.spawn_param_field('Погрешность',
                                            key=f'error{self.number}')

    @staticmethod
    def spawn_param_field(param_name, key, value: int = 10):
        return st.sidebar.number_input(f'{param_name}', 1, value=value, key=key)




