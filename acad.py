import base64

class Autocad:
    def __init__(self):
        self.text = ''
        self.script = ...

    def change_color(self, color:str = 'ByLayer'):
        self.text += f'COLOR {color}\n'

    def rectangle(self, x1:float, y1:float, x2:float, y2:float):
        self.text += f'RECTANG {x1},{y1} {x2},{y2}\n'

    def set_linetype(self, type_name:str = 'ByLayer'):
        self.text += f'-LINETYPE s {type_name} \n'

    def hatch(self, name:str = 'ANSI31', scale:float = '0.05',
              angle:int = 0, x:float = 0, y:float = 0):
        self.text += f'-HATCH p {name} {scale} {angle} {x},{y} \n\n '

    def write_text(self, x:float, y:float, text:str, height:float = 0.25, angle:int = 0):
        self.text += f'TEXT {x},{y} {height} {angle} {text} \n'

    def create_script(self):
        self.script = base64.b64encode(self.text.encode()).decode()


