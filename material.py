import streamlit as st
import pandas as pd

class Material:
    def __init__(self, name):
        self.df = pd.read_json(name)

    def resistance_df(self):
        self.df = self.df.rename(index={'name':'Название', 'max_tks':'Макс. ТКС',
                              'min_tks':'Мин. ТКС', 'min_res':'Мин. R',
                              'power':'Мощн.', 'max_res':'Макс. R',
                              'min_error':'Мин. погр.', 'max_error':'Макс. погр.'})
        self.df = self.df.transpose()
        self.df = self.df.rename(index = {x+1:name for x, name in enumerate(list(self.df['Название']))})
        del self.df['Название']
        return self.df