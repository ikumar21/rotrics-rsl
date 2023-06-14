import numpy as np
import math
from scipy.stats import gmean
from scipy.optimize import minimize
from statistics import mean

def sort_counterclockwise(points, centre):
  centre_x, centre_y = sum([x for x,_ in points])/len(points), sum([y for _,y in points])/len(points)
  angles = [math.atan2(y - centre_y, x - centre_x) for x,y in points]
  counterclockwise_indices = sorted(range(len(points)), key=lambda i: angles[i])
  counterclockwise_points = [points[i] for i in counterclockwise_indices]
  return counterclockwise_points

def shoelace(x_y):
    x_y = np.array(x_y)
    x_y = x_y.reshape(-1,2)
    
    x = x_y[:,0]
    y = x_y[:,1]

    S1 = np.sum(x*np.roll(y,-1))
    S2 = np.sum(y*np.roll(x,-1))

    area = .5*np.absolute(S1 - S2)

    return area

#pnts = [[60,75],[58,81],[53,85],[47,85],[42,81],[40,75],[42,69],[47,65],[53,65],[58,69],[60,75]]
pnts = [[60,75],[58,81],[42,82],[37,75],[56,80],[47,85],[38,70],[48,65],[53,65],[58,69],[60,75]]


x = [i[0] for i in pnts]
y = [i[1] for i in pnts]

xca = (max(x)-min(x))/2 + min(x)
yca = (max(y)-min(y))/2 + min(y)
pnts = sort_counterclockwise(pnts,[xca,yca])

A = shoelace(pnts)

cntr = gmean(pnts)

Ra2 = [math.sqrt((i[0]-cntr[0])**2+(i[1]-cntr[1])**2) for i in pnts]

r = A/(math.pi*mean(Ra2)**2)

n = len(pnts)
def f(x,y,n,R,xc,yc): return (x-xc)**2 + (y-yc)**2

# The objective Function to minimize (least-squares regression)
def obj(x,y,n,R,xc,yc): return abs(np.sum(f(x,y,n,R,xc,yc))/n-R**2)

# define the bounds -infty < a < infty,  b <= 0
bounds = [(None,None),(None,None),(None,None)]

# res.x contains your coefficients
res = minimize(lambda coeffs: obj(x,y,n,*coeffs), x0=[mean(Ra2),cntr[0],cntr[1]], bounds=bounds)
print(res.x)
print(math.pi*res.x[0]**2)
print(A/(math.pi*res.x[0]**2))









