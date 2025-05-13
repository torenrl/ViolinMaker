import svg
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


def four_circles(h, kc, ku, km, kw, b1, b2, bu, bj, cu1, cu2, cl1, cl2, pathcolor = "red", showCircles = False):

    # px to mm for 96 dpi
    px2mm = 3.77952755906 
    h *= px2mm
    
    kA = ( pyth_sub(1 + kc, kc+kw/2) - 1 )
    kB = ( pyth_sub(ku + kc, kc+kw/2) - ku )
    kR1 = km + pyth_add(1, 1-km)
    kR2 = km + pyth_add(ku, ku-km)

    rl = h / ( kR1 + kR2 + kA + kB)
    hc = rl*(kA+kB)

    r1 = rl * kR1
    r2 = rl * kR2

    margin = 4
    height = h+margin
    width = rl*2+margin
    cx = width / 2
    cy = height - r1 + rl - margin/2

    # 4 circles
    clower = (cx, cy)
    ccenterleft = (cx-rl*(kc+kw/2), cy - rl * pyth_sub(1+kc, kc+kw/2))
    ccenterright = (cx+rl*(kc+kw/2), cy - rl * pyth_sub(1+kc, kc+kw/2))
    cupper = (cx, cy - rl*(1+ku) - hc)
    # Upper and lower major circles
    c1 = (cx, cy-rl)
    c2 = (cx, cy-rl-hc)
    # Minor circles
    cmll = (cx-rl*(1-km), cy)
    cmlr = (cx+rl*(1-km), cy)
    cmul = (cx-rl*(ku-km), cupper[1])
    cmur = (cx+rl*(ku-km), cupper[1])
    # Corners
    A1, A2 = rl*b1, rl*b2
    xl1, xl2 = rl*cl1, rl*cl2
    xu1, xu2 = rl*ku*cu1, rl*ku*cu2

    cAl = (ccenterleft[0] + (rl*kc - A1), ccenterleft[1])
    cAr = (ccenterright[0] - (rl*kc - A1), ccenterright[1])

    Lu = pyth_add(cupper[0]-xu1-cAl[0], cupper[1]-cAl[1])
    Ll = pyth_add(clower[0]-xl1-cAl[0], clower[1]-cAl[1])
    du1 =   ( 
            cAl[0] + (cupper[0]-xu1-cAl[0]) * A2/Lu,
            cAl[1] + (cupper[1] - cAl[1]) * A2/Lu
            )
    dl1 =   ( 
            cAl[0] + (clower[0]-xl1-cAl[0]) * A2/Ll,
            cAl[1] + (clower[1] - cAl[1]) * A2/Ll
            )

    du2 = cupper
    dl2 = clower
    for i in line_circle_intersect(cupper, rl*ku, (cupper[0]-xu2, cupper[1]), cAl):
        if ( i[1] > du2[1] ):
            du2 = i
            break
    for i in line_circle_intersect(clower, rl, (clower[0]-xl2, clower[1]), cAl):
        if ( i[1] < dl2[1] ):
            dl2 = i
            break

    # circle_circle_intersect twice to find body tangent point
    yu, yj = du1[1]-du2[1],dl2[1]-dl1[1]
    au, aj = bu*yu, bj*yj

    du2 = du1
    dl2 = dl1
    for i in circle_circle_intersect(du1, yu, cupper, rl*ku+yu):
        if i[1]<du2[1]:
            du2=i

    tmp = line_circle_intersect(du2, yu, cAl, (cupper[0]-xu1, cupper[1]))
    if ( len(tmp)>1 and tmp[1][1] < tmp[0][1] ):
        du1 = tmp[1]
    else:
        du1 = tmp[0]
    
    tmp = circle_circle_intersect(du2,yu+au,ccenterleft,rl*kc-au)
    if len(tmp)>1 and tmp[1][0] > tmp[0][0]:
        du3 = tmp[1]
    else:
        du3 = tmp[0]
        
    du2 = circle_circle_intersect(du2, yu, cupper, rl*ku)[0]
    du3 = circle_circle_intersect(du3, au, ccenterleft, rl*kc)[0]
    
    for i in circle_circle_intersect(dl1, yj, clower, rl+yj):
        if i[1]>dl2[1]:
            dl2=i
            
    tmp = line_circle_intersect(dl2, yj, cAl, (clower[0]-xl1, clower[1]))
    if ( len(tmp)>1 and tmp[1][1] > tmp[0][1] ):
        dl1 = tmp[1]
    else:
        dl1 = tmp[0]

    tmp = circle_circle_intersect(dl2,yj+aj,ccenterleft,rl*kc-aj)
    if len(tmp)>1 and tmp[1][0] > tmp[0][0]:
        dl3 = tmp[1]
    else:
        dl3 = tmp[0]

    dl2 = circle_circle_intersect(dl2, yj, clower, rl)[0]
    dl3 = circle_circle_intersect(dl3, aj, ccenterleft, rl*kc)[0]
    
    du1r = (du1[0] + 2*(cx-du1[0]), du1[1])
    du2r = (du2[0] + 2*(cx-du2[0]), du2[1])
    du3r = (du3[0] + 2*(cx-du3[0]), du3[1])
    dl1r = (dl1[0] + 2*(cx-dl1[0]), dl1[1])
    dl2r = (dl2[0] + 2*(cx-dl2[0]), dl2[1])
    dl3r = (dl3[0] + 2*(cx-dl3[0]), dl3[1])
    
    # DIMENSIONS
    print(f"Height: {h/px2mm}")
    print(f"Lower bout width: {2*rl/px2mm}")
    print(f"Center bout width: {(ccenterright[0]-ccenterleft[0]-2*rl*kc)/px2mm}")
    print(f"Upper bout width: {2*rl*ku/px2mm}")

    # PATH

    points = [
        (
            cx,
            c1[1]+r1
        ),(
            cx + (cmll[0]-c1[0]) * r1/pyth_add(cmll[0]-c1[0],cmll[1]-c1[1]),
            c1[1] + (cmll[1]-c1[1]) * r1/pyth_add(cmll[0]-c1[0],cmll[1]-c1[1])
        ),(
            cmll[0] - rl*km,
            cy
        ),
        dl2,dl1,dl3,
        du3,du1,du2,
        (
            cmul[0] - rl*km,
            cupper[1]
        ),
        (
            cx + (cmul[0]-c2[0]) * r2/pyth_add(cmul[0]-c2[0],cmul[1]-c2[1]),
            c2[1] + (cmul[1]-c2[1]) * r2/pyth_add(cmul[0]-c2[0],cmul[1]-c2[1])
        ),
         # TOP MID
        (
            cx - (cmul[0]-c2[0]) * r2/pyth_add(cmul[0]-c2[0],cmul[1]-c2[1]),
            c2[1] + (cmul[1]-c2[1]) * r2/pyth_add(cmul[0]-c2[0],cmul[1]-c2[1])
        ),
        (
            cmur[0] + rl*km,
            cupper[1]
        ),
        du2r,du1r,du3r,
        dl3r,dl1r,dl2r,
        (
            cmlr[0] + rl*km,
            cy
        ),(
            cx + (cmlr[0]-c1[0]) * r1/pyth_add(cmlr[0]-c1[0],cmlr[1]-c1[1]),
            c1[1] + (cmlr[1]-c1[1]) * r1/pyth_add(cmlr[0]-c1[0],cmlr[1]-c1[1])
        ),(
            cx,
            c1[1]+r1
        )
    ]
    arc = [
        (r1, True),
        (rl*km, True),
        (rl, True),
        (yj, False),
        (aj, False),
        (rl*kc, False),
        (au, False),
        (yu, False),
        (rl*ku, True),
        (rl*km, True),
        (r2, True), # TOP MID
        (rl*km, True),
        (rl*ku, True),
        (yu, False),
        (au, False),
        (rl*kc, False),
        (aj, False),
        (yj, False),
        (rl, True),
        (rl*km, True),
        (r1, True),
    ]

    d = [svg.M(points[0][0], points[0][1])]
    for idx in range(len(points)-1):
        d.append(arc_abs_to_rel(points[idx], points[idx+1], arc[idx][0], arc[idx][1]))

    path = svg.Path(
        stroke=pathcolor,
        stroke_width=2,
        fill="transparent",
        d=d
    )


    color = "grey"
    elems = []
    if showCircles:
        elems += [
                svg.Circle(
                    cx = clower[0], cy = clower[1], r=rl,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cupper[0], cy = cupper[1], r=rl*ku,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = ccenterleft[0], cy = ccenterleft[1], r=rl*kc,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = ccenterright[0], cy = ccenterright[1], r=rl*kc,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = c1[0], cy = c1[1], r=r1,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = c2[0], cy = c2[1], r=r2,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cx+rl*(ku-km), cy = cupper[1], r=rl*km,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cx-rl*(ku-km), cy = cupper[1], r=rl*km,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cx+rl*(1-km), cy = clower[1], r=rl*km,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cx-rl*(1-km), cy = clower[1], r=rl*km,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cAl[0], cy = cAl[1], r=A1,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Circle(
                    cx = cAl[0], cy = cAl[1], r=A2,
                    stroke=color,
                    fill="transparent",
                    stroke_width=5,
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=cupper[0]-xu1,
                    y1=cupper[1],
                    x2=cAl[0],
                    y2=cAl[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=cupper[0]-xu2,
                    y1=cupper[1],
                    x2=cAl[0],
                    y2=cAl[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=clower[0]-xl1,
                    y1=clower[1],
                    x2=cAl[0],
                    y2=cAl[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=clower[0]-xl2,
                    y1=clower[1],
                    x2=cAl[0],
                    y2=cAl[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=cAl[0],
                    y1=du1[1],
                    x2=cAr[0],
                    y2=du1[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=cAl[0],
                    y1=du2[1],
                    x2=cAr[0],
                    y2=du2[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=cAl[0],
                    y1=dl1[1],
                    x2=cAr[0],
                    y2=dl1[1]
                ),
                svg.Line(
                    stroke=color,
                    stroke_width=2,
                    x1=cAl[0],
                    y1=dl2[1],
                    x2=cAr[0],
                    y2=dl2[1]
                ),
                svg.Circle(
                    cx = du1[0], cy = du1[1], r=3,
                    stroke="yellow",
                    fill="transparent",
                    stroke_width=2,
                ),
                svg.Circle(
                    cx = du2[0], cy = du2[1], r=3,
                    stroke="yellow",
                    fill="transparent",
                    stroke_width=2,
                ),
                svg.Circle(
                    cx = du3[0], cy = du3[1], r=3,
                    stroke="yellow",
                    fill="transparent",
                    stroke_width=2,
                ),
                svg.Circle(
                    cx = dl1[0], cy = dl1[1], r=3,
                    stroke="yellow",
                    fill="transparent",
                    stroke_width=2,
                ),
                svg.Circle(
                    cx = dl2[0], cy = dl2[1], r=3,
                    stroke="yellow",
                    fill="transparent",
                    stroke_width=2,
                ),
                svg.Circle(
                    cx = dl3[0], cy = dl3[1], r=3,
                    stroke="yellow",
                    fill="transparent",
                    stroke_width=2,
                ),
                
            ]
    elems.append(path)

    return svg.SVG(
        width=width,
        height=height,
        elements=elems
    )


def gen(h, kc, ku, km, kw, b1, b2, bu, bi, bj, bk, cu1, cu2, cl1, cl2, dbg=False):
    #Guarneri Baltic
    return four_circles(h, kc, ku, km, kw, b1, b2, bu, bj, cu1, cu2, cl1, cl2, 
                        showCircles=dbg)
