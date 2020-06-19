import streamlit as st


class Element:
    def __init__(self, number: int = 0, name: str = ''):
        """
        Base element class for inheritance
        :param number: positional number of element
        :param name: type of element
        """
        self.number = number
        self.name = name
        st.sidebar.subheader(f'{self.name} номер {self.number}')
        self.power = self.spawn_param_field('Мощность',
                                            key=f'power{self.number}')
        self.error = self.spawn_param_field('Погрешность',
                                            key=f'error{self.number}')

    @staticmethod
    def spawn_param_field(param_name: str, key: str, value: int = 10) -> int:
        """
        Spawns field to get parameter
        :param param_name: name of parameter. For example 'Мощность'
        :param key: unique key for number_input field
        :param value: default value for field
        :return: value of selected parameter
        """
        return st.sidebar.number_input(f'{param_name}', 1,
                                       value=value, key=key)
