import pandas as pd

class Material:
    def __init__(self, name):
        """
        Generate pandas DataFrame from custom JSON
        :param name: name of json file
        """
        self.df = pd.read_json(name)

    def resistance_df(self) -> pd.DataFrame:
        """
        Makes pretty df w/ resistance materials parameters
        :return: df to spawn on site
        """
        self.df = self.df.rename(index={'name':'Название', 'max_tks':'Макс. ТКС',
                              'min_tks':'Мин. ТКС', 'min_res':'Мин. R',
                              'power':'Мощн.', 'max_res':'Макс. R',
                              'min_error':'Мин. погр.', 'max_error':'Макс. погр.'})
        self.df = self.df.transpose()
        self.df = self.df.rename(index = {x+1:name for x, name in enumerate(list(self.df['Название']))})
        del self.df['Название']
        return self.df

    def condensator_df(self):
        """
        Makes pretty df w/ dielectric materials parameters
        :return: df to spawn on site
        """

        self.df = self.df.rename(index={'name': 'Название', 'mat_obk': 'Материал обкладки',
                                  'min_power': 'Мин. мощность', 'max_power': 'Макс. мощность',
                                  'min_c': 'Мин. уд. емк.', 'max_c': 'Макс. уд. емк.',
                                  'diel_pron': 'Диэл. прониц.', 'e_pr': 'Епр',
                                  'tke': 'ТКЕ'})
        self.df = self.df.transpose()
        self.df = self.df.rename(index={x + 1: name for x, name in enumerate(list(self.df['Название']))})
        del self.df['Название']
        del self.df['Материал обкладки']
        return self.df
