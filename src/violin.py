## Violin, Viola and Cello family instruments
#  

from helpers import *
from svg import Svg
from arching import *

class Violin:
    body_calculated = False
    corner_calculated = False

    move_px = [0,0]

    def as_image_px(self, p, move=False, mirror=False):
        x = p[0] if not mirror else 2*self.rl-p[0]
        y = p[1]
        if move:
            x += self.move_px[0]
            y -= self.move_px[1]
        y = self.h-y
        return (x,y)
    
    def as_image_px_mirror(self, p, move=False):
        return self.as_image_px((2*self.rl-p[0], p[1]), move)

    @staticmethod
    def by_measures(wu, wc, wl, overhang:float=None) -> tuple[float, float]:
        """
        Calculates ku and kw based on width measurements

        Args:
            wu (float): Upper bout width
            wc (float): Center bout width
            wl (float): Lower bout width
            overhang (float): (Optional) Overhang from ribs

        Returns:
            float:  ku
            float:  kc
        """
        if overhang is not None:
            wu -= 2*overhang
            wc -= 2*overhang
            wl -= 2*overhang

        return wu/wl, wc/wl

    def __init__(self, kc, ku, kw, b1, b2, bu, bl, cu1, cu2, cl1, cl2, h = None, km = None, kmu = None, kml = None):
        """
        Initialize instrument parameters. 

        Optional arguments:
            height: If obmitted a standard violin height (350mm) will be used
            km: For minor upper/lower bout circles, one option must be given:
                km = common for upper and lower
                kmu and kml: different for upper and lower 
        Args:
            h   (float): (Optional) length of body
            kc  (float): Center bout width relative to lower bout width
            ku  (float): Upper bout width relative to lower bout width
            kw  (float): Center bout width relative to lower bout width
            km  (float): (Optional) Minor upper and lower bout circle diameter relative to lower bout width
            kmu (float): (Optional) Minor upper bout circle diameter relative to lower bout width
            kml (float): (Optional) Minor lower bout circle diameter relative to lower bout width
            b1  (float): Radius of outer center side circle for corner shape
            b2  (float): Radius of inner center side circle for corner shape
            bu  (float): Inner corner radius relative to outer corner radius (upper)
            bl  (float): Inner corner radius relative to outer corner radius (lower)
            cu1 (float): Upper relative reference point for corner angle  
            cu2 (float): Upper relative reference point for corner radius  
            cl1 (float): Lower relative reference point for corner angle  
            cl2 (float): Lower relative reference point for corner radius
        """

        # Basic parameters
        if ( km is None and (kmu is None or kml is None) ):
            raise Exception("Violin init: Either km or both kmu and kml must be given")
        elif (km is not None):
            self.kmu = km
            self.kml = km
        else:
            self.kmu = kmu
            self.kml = kml

        self.h   = h if h is not None else 100
        self.kc  = kc
        self.ku  = ku
        self.kw  = kw
        self.b1  = b1
        self.b2  = b2
        self.bu  = bu
        self.bl  = bl
        self.cu1 = cu1
        self.cu2 = cu2
        self.cl1 = cl1
        self.cl2 = cl2

    def calculate_body_params(self):
        # Circle parameters
        kA = ( pyth_sub(1 + self.kc, self.kc+self.kw/2) - 1 )
        kB = ( pyth_sub(self.ku + self.kc, self.kc+self.kw/2) - self.ku )
        self.kr1 = self.kml + pyth_add(1, 1-self.kml)
        self.kr2 = self.kmu + pyth_add(self.ku, self.ku-self.kmu)
            
        self.rl = self.h / ( self.kr1 + self.kr2 + kA + kB)
        self.hc = self.rl*(kA+kB)

        self.r1 = self.rl * self.kr1
        self.r2 = self.rl * self.kr2

        # Upper and lower major circles
        self.c1 = (self.rl, self.r1)
        self.c2 = (self.rl, self.r1+self.hc)

        # Bout centers
        self.cl = (self.rl, self.r1-self.rl)
        self.cu = (self.rl, self.r1+self.hc+self.rl*self.ku)
        self.cc = (self.rl, self.cl[1] + self.rl*pyth_sub(1+self.kc, self.kc+self.kw/2))

        # Center left circle
        self.cc_left = (self.rl*(1-(self.kc+self.kw/2)),self.cc[1])
        
        
        # Minor circles
        self.cml_left  = (self.rl*(1-(1-self.kml)), self.cl[1])
        self.cmu_left  = (self.rl*(1-(self.ku-self.kmu)), self.cu[1])

        self.body_calculated = True

        return self.rl,self.r1,self.r2,self.cl,self.cu,self.cc,self.cc_left,self.c1,self.c2,self.cml_left,self.cmu_left

    def calculate_corner_params(self):     
        self.A1, self.A2 = self.rl*self.b1, self.rl*self.b2
        self.xl1, self.xl2 = self.rl*self.cl1, self.rl*self.cl2
        self.xu1, self.xu2 = self.rl*self.ku*self.cu1, self.rl*self.ku*self.cu2
        
        self.cA = (self.cc[0] - self.kw * self.rl / 2 - self.A1, self.cc[1])

        self.Lu = pyth_add(self.cu[0]-self.xu1-self.cA[0], self.cu[1]-self.cA[1])
        self.Ll = pyth_add(self.cl[0]-self.xl1-self.cA[0], self.cl[1]-self.cA[1])
        
        self.du1 =   ( 
                self.cA[0] + (self.cu[0]- self.xu1-self.cA[0]) * self.A2/self.Lu,
                self.cA[1] + (self.cu[1] - self.cA[1]) * self.A2/self.Lu
                )
        self.dl1 =   ( 
                self.cA[0] + (self.cl[0] - self.xl1-self.cA[0]) * self.A2/self.Ll,
                self.cA[1] + (self.cl[1] - self.cA[1]) * self.A2/self.Ll
                )
        
        tmp = line_circle_intersect(self.cu, self.rl*self.ku, (self.cu[0]-self.xu2, self.cu[1]), self.cA)
        self.du2 = tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1]

        tmp = line_circle_intersect(self.cl, self.rl, (self.cl[0]-self.xl2, self.cl[1]), self.cA)
        self.dl2 = tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1]

        self.yu, self.yl = self.du2[1]-self.du1[1],self.dl1[1]-self.dl2[1]
        self.au, self.al = self.bu*self.yu, self.bl*self.yl

        tmp = circle_circle_intersect(self.du1, self.yu, self.cmu_left, self.rl*self.kmu+self.yu)
        self.yuc = tmp[0] if len(tmp)==1 or tmp[0][1] > tmp[1][1] else tmp[1]
        
        tmp = circle_circle_intersect(self.dl1, self.yl, self.cl, self.rl+self.yl)
        self.ylc = tmp[0] if len(tmp)==1 or tmp[0][1] < tmp[1][1] else tmp[1]

        tmp = circle_circle_intersect(self.du1, self.au, self.cc_left, self.rl*self.kc-self.au)
        self.auc = tmp[0] if len(tmp)==1 or tmp[0][1] < tmp[1][1] else tmp[1]

        tmp = circle_circle_intersect(self.dl1, self.al, self.cc_left, self.rl*self.kc-self.al)
        self.alc = tmp[0] if len(tmp)==1 or tmp[0][1] > tmp[1][1] else tmp[1]

        self.corner_calculated = True
    
    def get_circles(self, color="red", move=[0,0]):
        circles = []
        
        svg = Svg(self.h, 2*self.rl, transpose=move)

        svg.fill="transparent"
        svg.color = color
        svg.stroke_width = 1/svg._px2mm

        # Body

        circles.append(svg.circle(self.rl, self.cl))
        circles.append(svg.circle(self.rl*self.ku, self.cu))
        circles.append(svg.circle(self.rl*self.kc, self.cc_left))
        circles.append(svg.circle(self.rl*self.kc, self.cc_left,mirror=True))
        circles.append(svg.circle(self.rl*self.kml, self.cml_left))
        circles.append(svg.circle(self.rl*self.kml, self.cml_left,mirror=True))
        circles.append(svg.circle(self.rl*self.kmu, self.cmu_left))
        circles.append(svg.circle(self.rl*self.kmu, self.cmu_left,mirror=True))
        circles.append(svg.circle(self.r1, self.c1))
        circles.append(svg.circle(self.r2, self.c2))


        # Corners
        if self.corner_calculated:
            circles.append(svg.circle(self.A1, self.cA))
            circles.append(svg.circle(self.A2, self.cA))
            circles.append(svg.circle(self.A1, self.cA,mirror=True))
            circles.append(svg.circle(self.A2, self.cA,mirror=True))
            
            circles.append(svg.circle(self.au, self.auc))
            circles.append(svg.circle(self.yu, self.yuc))
            circles.append(svg.circle(self.al, self.alc))
            circles.append(svg.circle(self.yl, self.ylc))
            
            circles.append(svg.circle(self.au, self.auc, mirror=True))
            circles.append(svg.circle(self.yu, self.yuc, mirror=True))
            circles.append(svg.circle(self.al, self.alc, mirror=True))
            circles.append(svg.circle(self.yl, self.ylc, mirror=True))

            circles.append(svg.circle(5, self.du1))
            circles.append(svg.circle(5, self.du2))
            circles.append(svg.circle(5, self.dl1))
            circles.append(svg.circle(5, self.dl2))

            circles.append(svg.circle(5, self.du1,mirror=True))
            circles.append(svg.circle(5, self.du2,mirror=True))
            circles.append(svg.circle(5, self.dl1,mirror=True))
            circles.append(svg.circle(5, self.dl2,mirror=True))

            circles.append(svg.circle(5, (self.cu[0]-self.xu2, self.cu[1])))
            circles.append(svg.circle(5, (self.cu[0]-self.xu1, self.cu[1])))
            circles.append(svg.circle(5, (self.cl[0]-self.xl1, self.cl[1])))
            circles.append(svg.circle(5, (self.cl[0]-self.xl2, self.cl[1])))
            
            circles.append(svg.circle(5, (self.cu[0]-self.xu2, self.cu[1]), mirror=True))
            circles.append(svg.circle(5, (self.cu[0]-self.xu1, self.cu[1]), mirror=True))
            circles.append(svg.circle(5, (self.cl[0]-self.xl1, self.cl[1]), mirror=True))
            circles.append(svg.circle(5, (self.cl[0]-self.xl2, self.cl[1]), mirror=True))

        return circles

    def get_circles_svg(self, color="red", move=[0,0]):
        svg = ""
        for circle in self.get_circles(color=color, move=move):
            svg += circle + "\n"
        return svg

    def get_outline_path(self, move=[0,0], color="black"):
        
        path = []
        svg = Svg(self.h, 2*self.rl, transpose=move)
        svg.color = color
        svg.stroke_width = 5

        path.append(svg.move_to( (
            self.rl    + (self.cml_left[0]-self.c1[0]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0], self.cml_left[1]-self.c1[1]), 
            self.c1[1] + (self.cml_left[1]-self.c1[1]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0],self.cml_left[1]-self.c1[1])
        )))
        path.append(svg.arc(self.rl * self.kml, (
            self.cl[0]-self.rl,
            self.cl[1]
        )))
        tmp = line_circle_intersect(self.cl, self.rl, self.ylc, self.cl)
        path.append(svg.arc(self.rl, 
            tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1]
        ))
        path.append(svg.arc(self.yl, self.dl1, dir=0))
        tmp = line_circle_intersect(self.cc_left, self.rl*self.kc, self.alc, self.cc_left)
        path.append(svg.arc(self.al, 
            tmp[0] if tmp[0][0] > tmp[1][0] else tmp[1],
            dir=0
        ))
        tmp = line_circle_intersect(self.cc_left, self.rl*self.kc, self.auc, self.cc_left)
        path.append(svg.arc(self.rl*self.kc, 
            tmp[0] if tmp[0][0] > tmp[1][0] else tmp[1],
            dir=0
        ))
        path.append(svg.arc(self.au, self.du1, dir=0))
        tmp = line_circle_intersect(self.cu, self.rl*self.ku, self.yuc, self.cu)
        path.append(svg.arc(self.yu, 
            tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1],
            dir=0
        ))
        path.append(svg.arc(self.rl*self.ku, (
            self.cu[0]-self.rl*self.ku,
            self.cu[1]
        )))
        path.append(svg.arc(self.rl*self.kmu, (
            self.cu[0] + (self.cmu_left[0]-self.c2[0]) * self.r2/pyth_add(self.cmu_left[0]-self.c2[0], self.cmu_left[1]-self.c2[1]), 
            self.c2[1] + (self.cmu_left[1]-self.c2[1]) * self.r2/pyth_add(self.cmu_left[0]-self.c2[0], self.cmu_left[1]-self.c2[1])
        )))
        
        path.append(svg.arc(self.r2, (
            self.cu[0] + (self.cmu_left[0]-self.c2[0]) * self.r2/pyth_add(self.cmu_left[0]-self.c2[0], self.cmu_left[1]-self.c2[1]), 
            self.c2[1] + (self.cmu_left[1]-self.c2[1]) * self.r2/pyth_add(self.cmu_left[0]-self.c2[0], self.cmu_left[1]-self.c2[1])
        ), dir=0, mirror=True))

        path.append(svg.arc(self.rl*self.kmu, (
            self.cu[0]-self.rl*self.ku,
            self.cu[1]
        ), dir=0, mirror=True))
        tmp = line_circle_intersect(self.cu, self.rl*self.ku, self.yuc, self.cu)
        path.append(svg.arc(self.rl * self.ku, 
            tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1],
            dir=0, mirror=True
        ))
        path.append(svg.arc(self.yu, self.du1, dir=1, mirror=True))
        tmp = line_circle_intersect(self.cc_left, self.rl*self.kc, self.auc, self.cc_left)
        path.append(svg.arc(self.au, 
            tmp[0] if tmp[0][0] > tmp[1][0] else tmp[1],
            dir=1, mirror=True
        ))
        tmp = line_circle_intersect(self.cc_left, self.rl*self.kc, self.alc, self.cc_left)
        path.append(svg.arc(self.rl * self.kc, 
            tmp[0] if tmp[0][0] > tmp[1][0] else tmp[1],
            dir=1, mirror=True
        ))
        path.append(svg.arc(self.al, self.dl1, dir=1, mirror=True))
        tmp = line_circle_intersect(self.cl, self.rl, self.ylc, self.cl)
        path.append(svg.arc(self.yl, 
            tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1],
            dir=1, mirror=True
        ))
        path.append(svg.arc(self.rl, (
            self.cl[0]-self.rl,
            self.cl[1]
        ), dir=0, mirror=True))
        path.append(svg.arc(self.rl * self.kml, (
            self.rl    + (self.cml_left[0]-self.c1[0]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0], self.cml_left[1]-self.c1[1]), 
            self.c1[1] + (self.cml_left[1]-self.c1[1]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0],self.cml_left[1]-self.c1[1])
        ), dir=0, mirror=True))

        path.append(svg.arc(self.r1, (
            self.rl    + (self.cml_left[0]-self.c1[0]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0], self.cml_left[1]-self.c1[1]), 
            self.c1[1] + (self.cml_left[1]-self.c1[1]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0],self.cml_left[1]-self.c1[1])
        )))

        path.append(svg.close())



        path_str = "<path d=\""
        for p in path:
            path_str += p
        path_str += f"\" style=\"fill:none;stroke:{svg.color};stroke-width:{svg.stroke_width}\" />"

        return path_str       


    def get_template(self, color="black", move=[0,0]):
        
        path = []
        svg = Svg(self.h, 2*self.rl, transpose=move)
        svg.color = color
        svg.stroke_width = 0.25

        path.append(svg.move_to((self.rl, 0)))
        path.append(svg.arc(self.r1, (
            self.rl    + (self.cml_left[0]-self.c1[0]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0], self.cml_left[1]-self.c1[1]), 
            self.c1[1] + (self.cml_left[1]-self.c1[1]) * self.r1/pyth_add(self.cml_left[0]-self.c1[0],self.cml_left[1]-self.c1[1])
        )))
        path.append(svg.arc(self.rl * self.kml, (
            self.cl[0]-self.rl,
            self.cl[1]
        )))
        tmp = line_circle_intersect(self.cl, self.rl, self.ylc, self.cl)
        path.append(svg.arc(self.rl, 
            tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1]
        ))
        path.append(svg.arc(self.yl, self.dl1, dir=0))
        tmp = line_circle_intersect(self.cc_left, self.rl*self.kc, self.alc, self.cc_left)
        path.append(svg.arc(self.al, 
            tmp[0] if tmp[0][0] > tmp[1][0] else tmp[1],
            dir=0
        ))
        tmp = line_circle_intersect(self.cc_left, self.rl*self.kc, self.auc, self.cc_left)
        path.append(svg.arc(self.rl*self.kc, 
            tmp[0] if tmp[0][0] > tmp[1][0] else tmp[1],
            dir=0
        ))
        path.append(svg.arc(self.au, self.du1, dir=0))
        tmp = line_circle_intersect(self.cu, self.rl*self.ku, self.yuc, self.cu)
        path.append(svg.arc(self.yu, 
            tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1],
            dir=0
        ))
        path.append(svg.arc(self.rl*self.ku, (
            self.cu[0]-self.rl*self.ku,
            self.cu[1]
        )))
        path.append(svg.arc(self.rl*self.kmu, (
            self.cu[0] + (self.cmu_left[0]-self.c2[0]) * self.r2/pyth_add(self.cmu_left[0]-self.c2[0], self.cmu_left[1]-self.c2[1]), 
            self.c2[1] + (self.cmu_left[1]-self.c2[1]) * self.r2/pyth_add(self.cmu_left[0]-self.c2[0], self.cmu_left[1]-self.c2[1])
        )))
        path.append(svg.arc(self.r2,(
            self.cu[0], self.h #self.c2[1]+self.r2
        )))
        path.append(svg.line((self.cu[0]+10, self.h)))
        path.append(svg.line((self.cu[0]+10, 0)))
        path.append(svg.close())

        # Template outline path
        as_str = "<path d=\""
        for p in path:
            as_str += p
        as_str += f"\" style=\"fill:none;stroke:{svg.color};stroke-width:{svg._px2mm * svg.stroke_width}\" />\n"

        # Template holes
        closs_size = (100,30)#(40,15)
        corner_closs_size = (50,10)#(24,6)

        hole_dia = 1
        svg.fill=color
        svg.stroke_width=0

        as_str += svg.circle(hole_dia, self.cl) + "\n"
        as_str += svg.circle(hole_dia, self.cu) + "\n"
        as_str += svg.circle(hole_dia, (self.rl, self.h-(closs_size[1]+10))) + "\n"
        as_str += svg.circle(hole_dia, (self.rl, closs_size[1]+10)) + "\n"


        as_str += svg.circle(hole_dia, (self.rl, self.h-closs_size[1])) + "\n"
        as_str += svg.circle(hole_dia, (self.rl-closs_size[0]/2, self.h-closs_size[1])) + "\n"
        as_str += svg.circle(hole_dia, (self.rl-closs_size[0]/2, self.h-closs_size[1]/2)) + "\n"
        as_str += svg.circle(hole_dia, (self.rl, closs_size[1])) + "\n"
        as_str += svg.circle(hole_dia, (self.rl-closs_size[0]/2, closs_size[1])) + "\n"
        as_str += svg.circle(hole_dia, (self.rl-closs_size[0]/2, closs_size[1]/2)) + "\n"

        #tmp = line_circle_intersect(self.cl, self.rl-corner_closs_size[1], self.cl, self.dl1)
        #lower_corner_closs_center = tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1]
        tmp = line_circle_intersect(self.cu, self.rl*self.ku-corner_closs_size[1], self.cu, self.du1)
        upper_corner_closs_center = tmp[0] if tmp[0][0] < tmp[1][0] else tmp[1]

        tmp = pyth_add(self.dl1[0]-self.cl[0], self.dl1[1]-self.cl[1])
        unit_lower = ((self.dl1[0]-self.cl[0])/tmp, (self.dl1[1]-self.cl[1])/tmp)
        tmp = pyth_add(self.du1[0]-self.cu[0], self.du1[1]-self.cu[1])
        unit_upper = ((self.du1[0]-self.cu[0])/tmp, (self.du1[1]-self.cu[1])/tmp)
        normal_lower = (-unit_lower[1], unit_lower[0])
        normal_upper = (-unit_upper[1], unit_upper[0])

        lower_corner_closs_center = (
            self.cl[0] + (self.rl-corner_closs_size[1]) * unit_lower[0],
            self.cl[1] + (self.rl-corner_closs_size[1]) * unit_lower[1]
        )

        as_str += svg.circle(hole_dia, lower_corner_closs_center) + "\n"
        as_str += svg.circle(hole_dia, upper_corner_closs_center) + "\n"
        
        as_str += svg.circle(hole_dia, (upper_corner_closs_center[0] + corner_closs_size[0]/2*normal_upper[0], upper_corner_closs_center[1] + corner_closs_size[0]/2*normal_upper[1])) + "\n"
        as_str += svg.circle(hole_dia, (upper_corner_closs_center[0] - corner_closs_size[0]/2*normal_upper[0], upper_corner_closs_center[1] - corner_closs_size[0]/2*normal_upper[1])) + "\n"

        as_str += svg.circle(hole_dia, (upper_corner_closs_center[0] + .6*unit_upper[0]*corner_closs_size[1] + corner_closs_size[0]/2*normal_upper[0], upper_corner_closs_center[1] + .6*unit_upper[1]*corner_closs_size[1] + corner_closs_size[0]/2*normal_upper[1])) + "\n"
        as_str += svg.circle(hole_dia, (upper_corner_closs_center[0] + .6*unit_upper[0]*corner_closs_size[1] - corner_closs_size[0]/2*normal_upper[0], upper_corner_closs_center[1] + .6*unit_upper[1]*corner_closs_size[1] - corner_closs_size[0]/2*normal_upper[1])) + "\n"

        as_str += svg.circle(hole_dia, (lower_corner_closs_center[0] + corner_closs_size[0]/2*normal_lower[0], lower_corner_closs_center[1] + corner_closs_size[0]/2*normal_lower[1])) + "\n"
        as_str += svg.circle(hole_dia, (lower_corner_closs_center[0] - corner_closs_size[0]/2*normal_lower[0], lower_corner_closs_center[1] - corner_closs_size[0]/2*normal_lower[1])) + "\n"

        as_str += svg.circle(hole_dia, (lower_corner_closs_center[0] + .6*unit_lower[0]*corner_closs_size[1] + corner_closs_size[0]/2*normal_lower[0], lower_corner_closs_center[1] + .6*unit_lower[1]*corner_closs_size[1] + corner_closs_size[0]/2*normal_lower[1])) + "\n"
        as_str += svg.circle(hole_dia, (lower_corner_closs_center[0] + .6*unit_lower[0]*corner_closs_size[1] - corner_closs_size[0]/2*normal_lower[0], lower_corner_closs_center[1] + .6*unit_lower[1]*corner_closs_size[1] - corner_closs_size[0]/2*normal_lower[1])) + "\n"

        return as_str

    def get_center_line(self, move=[0,0]):
        linecfg = f"fill:none;stroke:green;stroke-width:{Svg._px2mm * 1}"

        line = f"<line x1=\"{Svg._px2mm*(self.rl+move[0])}\" y1=\"{Svg._px2mm*(move[1])}\" x2=\"{Svg._px2mm*(self.rl+move[0])}\" y2=\"{Svg._px2mm*(self.h+move[1])}\" style=\"{linecfg}\" />\n"
        line += f"<line x1=\"{Svg._px2mm*(self.rl-5+move[0])}\" y1=\"{Svg._px2mm*(self.h+move[1])}\" x2=\"{Svg._px2mm*(self.rl+5+move[0])}\" y2=\"{Svg._px2mm*(self.h+move[1])}\" style=\"{linecfg}\" />\n"
        line += f"<line x1=\"{Svg._px2mm*(self.rl-5+move[0])}\" y1=\"{Svg._px2mm*(move[1])}\" x2=\"{Svg._px2mm*(self.rl+5+move[0])}\" y2=\"{Svg._px2mm*(move[1])}\" style=\"{linecfg}\" />\n"

        return line

    def get_dimensions(self):
        return Svg._px2mm * self.h, Svg._px2mm * 2*self.rl
    
    def get_dimensions_mm(self):
        return self.h, 2*self.rl
    
    def get_arching(self, h, afc=None, afd=None):
        N=101
        long = circle_arch(h=h, L=self.h, h1=afc, d1=afd, x=[self.h*i/(N-1) for i in range(N)])

        combine = lambda a,b : (a,b)

        arches_pos, arches_heigth = circle_arch(
            h=h, 
            L=self.h, 
            h1=afc, 
            d1=afd,
            x=[
                self.cl[1],
                self.ylc[1],
                self.cc[1],
                self.yuc[1],
                self.cu[1]
            ])
        arches_width = [
            2*self.rl, 2*(self.rl-self.ylc[0]-self.yl), self.rl*self.kw, 2*(self.rl-self.yuc[0]-self.yu), 2*self.rl*self.ku
        ]
        arches = [cycloid(h,w)
            for h,w in map(combine, arches_heigth, arches_width)]
        
        return arches_width, arches_pos, arches, long

    def get_arches_path_on_outline(self, h, afc=None, afd=None, color="red", long_color="green", refline_color="grey"):
        arches_width, arches_pos, arches, long = self.get_arching(h,afc,afd)

        combine = lambda a,b,c : (a,b,c)
        paths = ""
        for a,p,w in map(combine, arches, arches_pos, arches_width):
            paths += self.get_arch_path([[0,w],[0,0]], start=((2*self.rl-w)/2, -p), color=refline_color)
            paths += "\n"
            paths += self.get_arch_path(a,start=((2*self.rl-w)/2, -p), color=color)
            paths += "\n"
        paths += self.get_arch_path([[0,self.h],[0,0]], dir=1, start=(self.rl, 0), color=refline_color)
        paths += self.get_arch_path(long, dir=1, start=(self.rl, 0), color=long_color)

        return paths

    def get_arches_paths(self, h, color="black"):
        arches_width, _, arches, long = self.get_arching(h)
        
        combine = lambda a,b : (a,b)
        paths = []
        for a,w in map(combine, arches, arches_width):
            paths.append(self.get_arch_path(a, color=color))
        paths.append(self.get_arch_path(long, color=color))

        return paths
    
    def get_arch_path(self, arch, dir=0, start=(0,0), color="black"):
        path = []
        
        svg = Svg(self.h, 2*self.rl, transpose=start)
        svg.color = color
        svg.stroke_width = 1

        arch_p = list(map(lambda a,b: (a,b) if dir==0 else (b,a), arch[0], arch[1]))

        path.append(svg.move_to(arch_p[0]))
        for a in arch_p[1:]:
            path.append(svg.line(a))
        
        as_str = "<path d=\""
        for p in path:
            as_str += p
        as_str += f"\" style=\"fill:none;stroke:{svg.color};stroke-width:{svg._px2mm * svg.stroke_width}\" />"

        return as_str
        





