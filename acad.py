import base64

class Autocad:
    def __init__(self, x_pos: float):
        self.text = ''
        self.script = None
        self.x_cord = x_pos

    def change_color(self, color:str = 'ByLayer'):
        self.text += f'COLOR {color}\n'

    def rectangle(self, x1:float, y1:float, x2:float, y2:float):

        self.text += f'RECTANG {x1},{y1} {x2},{y2}\n'

    def line(self, x1:float, y1:float, x2:float, y2:float):
        self.text += f'LINE {round(self.x_cord + x1, 2)},{round(y1, 2)}' \
                     f' {round(self.x_cord+x2, 2)},{round(y2,2)}\nX\n'

    def set_linetype(self, type_name:str = 'ByLayer'):
        self.text += f'-LINETYPE s {type_name} \n'

    def hatch(self, name:str = 'ANSI31', scale:float = '0.05',
              angle:int = 0, x:float = 0, y:float = 0.01):
        self.text += f'-HATCH p {name} {scale} {angle} {x},{y} \n\n '

    def write_text(self, x:float, y:float, text:str, height:float = 0.05, angle:int = 0):
        self.text += f'TEXT {x},{y} {height} {angle} {text}\n'

    def draw_rectangle(self, b, length, number):

        self.change_color()
        self.rectangle(x1=self.x_cord, y1=0,
                       x2=round(self.x_cord+b+0.18,2), y2=length)
        self.change_color(color='RED')
        self.line(x1=0.09, y1=0,
                  x2=0.09, y2=length)
        self.line(x1=b+0.09, y1=0,
                  x2=b+0.09, y2=length)
        self.change_color()
        self.hatch(name='DOTS', x=round(self.x_cord+0.15,2))
        self.write_text(x=round(self.x_cord+b/2, 2), y=round(length/2, 2),
                        text=f'R{number}')
        self.x_cord += b
        return self.text

    def draw_meander(self, b, n, length, number):
        self.change_color()
        self.line(x1=b, y1=0,
                  x2=b, y2=-2*b)
        self.line(x2=b, y2=-2*b,
                  x1=0, y1=-2*b)
        self.line(x1=0, y1=(-2*b),
                  x2=0, y2=b)
        self.change_color('RED')
        self.line(x1=0, y1=-b,
                  x2=b, y2=-b)
        self.change_color()

        for i in range(n):
            if i % 2 == 0:
                self.line(x1=b, y1=i*b*2,
                          x2=length, y2=i*b*2)
                self.line(x2=length, y2=i*b*2,
                          x1=length, y1=i*2*b+3*b)

                self.line(x1=length-b, y1=i*2*b+2*b,
                          x2=length-b, y2=i*2*b+b)
                self.line(x2=length-b, y2=i*2*b+b,
                          x1=0, y1=i*2*b+b)

            else:
                self.line(x1=length-b, y1=i*2*b,
                          x2=0, y2=i*2*b)
                self.line(x2=0, y2=i*2*b,
                          x1=0, y1=i*2*b+3*b)

                self.line(x1=length, y1=i*2*b+b,
                          x2=b, y2=i*2*b+b)
                self.line(x2=b, y2=i*2*b+b,
                          x1=b, y1=i*2*b+2*b)
        if n % 2 == 1:
            self.line(x1=length-b, y1=n*2*b,
                      x2=length-b, y2=n*2*b+b)
            self.line(x2=length-b, y2=n*2*b+b,
                      x1=length, y1=n*2*b+b)
            self.change_color('RED')
            self.line(x1=length-b, y1=n*2*b,
                      x2=length, y2=n*2*b)
            self.change_color()

        else:
            self.line(x1=0, y1=n*2*b+b,
                      x2=b, y2=n*2*b+b)
            self.line(x2=b, y2=n*2*b+b,
                      x1=b, y1=n*2*b)
            self.change_color('RED')
            self.line(x1=b, y1=n*2*b,
                      x2=0, y2=n*2*b)
            self.change_color()
        self.hatch(name='DOTS', x=self.x_cord+0.1, y=0.05)
        self.write_text(x=self.x_cord+b/2, y=length/2,
                        text=f'R{number}')
        return self.text


    def create_script(self):
        self.script = base64.b64encode(self.text.encode()).decode()


