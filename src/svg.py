class Svg:
    _px2mm = 3.77952755906

    color = "black"
    fill = "transparent"
    stroke_width = 1

    def __init__(self,h,w,transpose=[0,0]):
        self.h = h
        self.w = w
        self.transpose = transpose
    
    def get_x(self, p, mirror):
        x = p[0] if not mirror else self.w-p[0]
        return self._px2mm * ( x + self.transpose[0] )
    
    def get_y(self, p):
        y = p[1]
        return self._px2mm * ( self.h - y + self.transpose[1] )
    
    def circle(self, r, c, mirror=False):
        return f"<circle r=\"{self._px2mm * r}\" cx=\"{self.get_x(c, mirror)}\" cy=\"{self.get_y(c)}\" fill=\"{self.fill}\" stroke=\"{self.color}\" stroke-width=\"{self._px2mm * self.stroke_width}\" />"
    
    def move_to(self, p, mirror=False):
        return f"M{self.get_x(p, mirror)} {self.get_y(p)}"

    def line(self, p, mirror=False):
        return f"L{self.get_x(p, mirror)} {self.get_y(p)}"
    
    def close(self):
        return "Z"
    
    def arc(self, r, p, dir=True, large_arc=False, mirror=False, relative=False):
        sweep_flag = not dir if mirror else dir
        r *= self._px2mm
        return f"{'a' if relative else 'A'}{r} {r} {0} {1 if large_arc else 0} {1 if sweep_flag else 0} {self.get_x(p, mirror)} {self.get_y(p)}"

