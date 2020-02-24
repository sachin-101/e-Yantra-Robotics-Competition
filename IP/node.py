import math

class Node():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def calc_angle(self, origin, aruco_center):
        x_c, y_c = origin
        x_2, y_2 = aruco_center
        a = ((y_c-self.y)**2 + (x_c-self.x)**2)**0.5                  
        b = ((y_c-y_2)**2 + (x_c-x_2)**2)**0.5
        c = ((self.y-y_2)**2 + (self.x-x_2)**2)**0.5

        num = a**2 + b**2 - c**2
        den = 2*a*b
        angle = math.acos(num/den)  # rads
        self.angle = (angle*180)/math.pi
        
    def __lt__(self, other):
        return self.angle < other.angle

    def __eq__(self,other):
        return self.angle == other.angle 

    def below_line(self, origin, aruco_center):
        x_c, y_c = origin
        x_2, y_2 = aruco_center
        v1 = (x_2 - x_c, y_2 - y_c)   # Vector 1
        v2 = (x_2 - self.x, y_2 - self.y)   # Vector 2
        xp = v1[0]*v2[1] - v1[1]*v2[0]  # Cross product
        if xp > 0:
            return True
        else:
            return False

# ----utils-------#
    
def sort_nodes(nodes, origin, capital):

    below_nodes, above_nodes = [], []
    
    for n in nodes:
        if n.below_line(origin, capital):
            below_nodes.append(n)
        else:
            above_nodes.append(n)

    ######## check this once  ################
    sort_bn = sorted(below_nodes, reverse=True)
    sort_an = sorted(above_nodes,)
    sorted_nodes = sort_an + sort_bn
    return sorted_nodes

