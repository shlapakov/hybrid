class Autocad:

    def __init__(self, x_pos: float):
        """
        Class to work w/ AutoCAD
        :param x_pos: x-coordinate of element
        """
        self.text = ''
        self.script = None
        self.x_cord = x_pos

    def change_color(self, color: str = 'ByLayer'):
        """
        Change color of layer.
        :param color: expected color for example 'RED', 'BLUE'
        :return: nothing
        """
        self.text += f'COLOR {color}\n'

    def rectangle(self, x1: float, y1: float, x2: float, y2: float):
        """
        Makes RECTANG command.
        :param x1: x-coordinate of first point
        :param y1: y-coordinate of first point
        :param x2: x-coordinate of second point
        :param y2: y-coordinate of second point
        :return: nothing
        """
        self.text += f'RECTANG {round(x1,2)},{round(y1,2)}' \
                     f' {round(x2,2)},{round(y2,2)}\n'

    def line(self, x1: float, y1: float, x2: float, y2: float):
        """
        Makes LINE command. Works only w/ two dots. Cant make multi-line.
        :param x1: x-coordinate of first point
        :param y1: y-coordinate of first point
        :param x2: x-coordinate of second point
        :param y2: y-coordinate of second point
        :return: nothing
        """
        self.text += f'LINE {round(self.x_cord + x1, 2)},{round(y1, 2)}' \
                     f' {round(self.x_cord+x2, 2)},{round(y2,2)}\nX\n'

    def set_linetype(self, type_name: str = 'ByLayer'):
        """
        Makes -LINETYPE command to set type of line.
        :param type_name: name of linetype. For example 'ACAD_ISO04W100'
        :return:
        """
        self.text += f'-LINETYPE s {type_name} \n'

    def hatch(self, name: str = 'ANSI31', scale: float = '0.05',
              angle: int = 0, x: float = 0, y: float = 0.01):
        """
        Makes HATCH command. Working only w/ pick-point.
        :param name: type of hatch. For example 'ANSI31'
        :param scale: scale of hatch.
        :param angle: angle of hatch.
        :param x: x-coordinate of pick-point
        :param y: y-coordinate of pick-point
        :return:
        """
        self.text += f'-HATCH p {name} {scale} {angle} ' \
                     f'{round(x,2)},{round(y,2)} \n\n '

    def write_text(self, x: float, y: float, text: str,
                   height: float = 0.05, angle: int = 0):
        """
        Makes TEXT command w/ custom text.
        :param x: x-coordinate of start text point.
        :param y: x-coordinate of start text point.
        :param text: text to draw
        :param height: height of text
        :param angle: angle of text
        :return:
        """
        self.text += f'TEXT {round(x, 2)},{round(y, 2)} ' \
                     f'{height} {angle} {text}\n'

    def draw_rectangle(self, b: float, length: float, number: int) -> str:
        """
        Makes rectangle-based resistor
        :param b: width of resistor
        :param length: length of resistor
        :param number: positional number of resistor
        :return: script commands
        """
        self.change_color()
        self.rectangle(x1=self.x_cord, y1=0,
                       x2=round(self.x_cord+b+0.18, 2), y2=length)
        self.change_color(color='RED')
        self.line(x1=0.09, y1=0,
                  x2=0.09, y2=length)
        self.line(x1=b+0.09, y1=0,
                  x2=b+0.09, y2=length)
        self.change_color()
        self.hatch(name='DOTS', x=round(self.x_cord+0.15, 2))
        self.write_text(x=round(self.x_cord+b/2, 2), y=round(length/2, 2),
                        text=f'R{number}')
        self.x_cord += b
        return self.text

    def draw_meander(self, b: float, n: int,
                     length: float, number: int) -> str:
        """
        Makes meander resistor
        :param b: width of resistor
        :param n: count of z-elements
        :param length: length of resistor
        :param number: positional number of resistor
        :return: script commands
        """
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

    def draw_overlap(self, a1: float, a2: float,
                     a3: float, number: int) -> str:
        """
        Makes overlap-based capacitor
        :param a1: Smallest side
        :param a2: Second side
        :param a3: Biggest side
        :param number: Positional number of capacitor
        :return: script commands
        """
        self.change_color()
        self.set_linetype(type_name='ACAD_ISO04W100')
        self.rectangle(x1=self.x_cord, y1=0,
                       x2=self.x_cord+a3, y2=a3)
        self.set_linetype(type_name='ByLayer')
        self.rectangle(x1=self.x_cord+0.05, y1=0.05,
                       x2=self.x_cord + a2, y2=a2)
        self.rectangle(x1=self.x_cord+0.1, y1=0.1,
                       x2=self.x_cord+a1, y2=a1)
        self.hatch(name='ANSI31', x=self.x_cord+0.15, y=0.15)
        self.hatch(name='ANSI31', angle=90, x=self.x_cord+0.07, y=0.07)
        self.write_text(x=self.x_cord+a3/2, y=a3/2, text=f'C{number}')
        self.x_cord += a3+1
        return self.text

    def draw_intersection(self, a1: float, a2: float, number: int) -> str:
        """
        Make intersection-based capacitor
        :param a1: smallest side
        :param a2: biggest side
        :param number: Positional number of capacitor
        :return: script commands
        """
        self.change_color()
        self.rectangle(x1=self.x_cord, y1=0,
                       x2=self.x_cord+0.9+a1, y2=a1)
        self.hatch(x=self.x_cord+0.05, y=0.05)
        self.rectangle(x1=self.x_cord+0.45, y1=-0.45,
                       x2=self.x_cord+0.45+a1, y2=a1+0.45)
        self.hatch(angle=90, x=self.x_cord+0.5, y=a1+0.1)
        self.hatch(angle=90, x=self.x_cord+0.5, y=-0.06)
        self.set_linetype('ACAD_ISO02W100')
        self.rectangle(x1=self.x_cord+0.4, y1=-0.05,
                       x2=self.x_cord+0.4+a2, y2=a2-0.05)
        self.set_linetype()
        self.write_text(x=self.x_cord+(0.45+a1/2), y=0.45, text=f'C{number}')
        self.x_cord += a2+2
        return self.text
