import math

def pyth_add(a, b):
    return math.sqrt(math.pow(a,2) + math.pow(b,2))

def pyth_sub(a, b):
    return math.sqrt(math.pow(a,2) - math.pow(b,2))

def arc_abs_to_rel(p0, p1, r, dir=True):
    return svg.a(r,r,0,False,dir,p1[0]-p0[0], p1[1]-p0[1])

def line_circle_intersect(ccenter, cradius, p0, p1):
    # setting circle center to origo
    a = (p0[0], p0[1])
    b = (p1[0], p1[1])

    # setting line to y = mx + c
    m = (b[1]-a[1]) / (b[0]-a[0])
    c = a[1]-m*a[0]

    h = ccenter[0]
    k = ccenter[1]

    A = 1 + math.pow(m,2)
    B = 2 * (m * (c - k) - h)
    C = math.pow(h,2) + math.pow(c-k,2) - math.pow(cradius,2)

    discriminant = math.pow(B,2) - 4 * A * C
    
    if discriminant < 0:
        return []
    elif discriminant == 0:
        x = -B / (2 * A)
        y = m * x + c
        return [(x, y)]
    else:   
        sqrt_discriminant = math.sqrt(discriminant)
        x1 = (-B + sqrt_discriminant) / (2 * A)
        x2 = (-B - sqrt_discriminant) / (2 * A)
        y1 = m * x1 + c
        y2 = m * x2 + c
        return [(x1, y1), (x2, y2)]

def circle_circle_intersect(c0, r0, c1, r1):
    # circle 1: c0=(x0, y0), radius r0
    # circle 2: c1=(x1, y1), radius r1

    x0,y0 = c0
    x1,y1 = c1

    d=math.sqrt((x1-x0)**2 + (y1-y0)**2)
    
    # non intersecting
    if d > r0 + r1 :
        r0 = d-r1
    # One circle within other
    elif d < abs(r0-r1):
        r0 = d-r1
    # coincident circles
    elif d == 0 and r0 == r1:
        return []
    
    a=(math.pow(r0,2)-math.pow(r1,2)+math.pow(d,2))/(2*d)
    x2=x0+a*(x1-x0)/d   
    y2=y0+a*(y1-y0)/d 
      
    # single intersect 
    if d == r0+r1 or abs(r0) < abs(a):
        return [(x2,y2)]
    else:
        h=math.sqrt(math.pow(r0,2)-math.pow(a,2))
        x3=x2+h*(y1-y0)/d     
        y3=y2-h*(x1-x0)/d 

        x4=x2-h*(y1-y0)/d
        y4=y2+h*(x1-x0)/d
        
        return [(x3, y3), (x4, y4)]

