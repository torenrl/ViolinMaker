import math
from svg import Svg
from helpers import *

def cycloid(h,L,N=101):
    dir = 1 if h > 0 else -1
    if dir<0:
        h = -h

    b = h/2
    a = L/(2*math.pi)
    theta = [2*math.pi*i/(N-1) for i in range(N)]

    x = [a*t - b*math.sin(t) for t in theta]
    y = [a   - b*math.cos(t) for t in theta]
    my = min(y)
    y = [dir*(i-my) for i in y]

    return [x,y]

def circle_arch(h, L, x, d1=None, h1=None, smooth=0):
    dir = 1 if h > 0 else -1
    h *= dir

    r = h/2 + math.pow(L,2)/(8*h)
    tmp = circle_circle_intersect((0,0),r,(L,0),r)
    if len(tmp) == 1:
        c = tmp[0]
    else:
        c = tmp[0] if tmp[0][1] < tmp[1][1] else tmp[1]

    if d1 is not None and h1 is not None:
        h1 *= dir

        if h1 <= 0:
            raise Exception("h and h1 must have same polarity")
        if d1 <= 0:
            raise Exception("d1 must be positive")
        if d1 >= h1:
            raise Exception("d1 must be lower than h1")
        if h1 >= h:
            raise Exception("h1 must be lower than h")
        
        h1 -= d1
        
        r1 = h1/2 + math.pow(L,2)/(8*h1)
        tmp = circle_circle_intersect((0,d1),r1,(L,d1),r1)
        c1 = tmp[0] if tmp[0][1] < tmp[1][1] else tmp[1]



        tmp = circle_circle_intersect(c,r,c1,r1)
        
        
        
        y0 = [
            dir*(math.sqrt(math.pow(r,2) - math.pow(xi-c[0],2)) + c[1]) 
            for xi in x
        ]
        y1 = [
            dir*(math.sqrt(math.pow(r1,2) - math.pow(xi-c1[0],2)) + c1[1]) 
            for xi in x
        ]
        combine = lambda a,b: (a,b)
        y = [min(yi,yj) for yi,yj in map(combine, y0, y1)]


    elif d1 is not None or h1 is not None:
        raise Exception("Either both or none of d1 and h1 can be given")
    else:
        y = [
            dir*(math.sqrt(math.pow(r,2) - math.pow(xi-c[0],2)) + c[1]) 
            for xi in x
        ]

    return x,y


if __name__ == "__main__":
    h = 20
    w = 260

    x,y=cycloid(h,w,100)

    svg = Svg(h, w)

    path = []
    svg.color = "white"
    svg.stroke_width = 2

    path.append(svg.move_to((x[0],y[0])))
    for i in range(len(x)):
        path.append(svg.line((x[i],y[i])))
    
    svgstr = f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{w*Svg._px2mm}\" height=\"{h*Svg._px2mm}\">\n"
    svgstr += "<path d=\""
    for p in path:
        svgstr += p
    svgstr += f"\" style=\"fill:none;stroke:{svg.color};stroke-width:{svg.stroke_width}\" />"
    svgstr += "</svg>\n"

    with open("test.svg", "w") as fout:
        fout.write(svgstr)