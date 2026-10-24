"""Prepared regular triangular flag; no native execution/cloth qualification."""
import math

def topology(n=22):
 if type(n) is not int or not 8<=n<=32:raise ValueError('FLAG363_GRID')
 points=[];lookup={};pins=[];faces=[]
 for i in range(n+1):
  for j in range(n+1-i):
   u=i/n;v=j/n;idx=len(points);lookup[i,j]=idx
   points.append((.022+.004*math.sin(5*u+3*v)*u,.55*u,3.48-.54*v-.27*u))
   if i==0 and j in {0,n//2,n}:pins.append(idx)
 for i in range(n):
  for j in range(n-i):
   faces.append((lookup[i,j],lookup[i+1,j],lookup[i,j+1]))
   if i+j<n-1:faces.append((lookup[i+1,j],lookup[i+1,j+1],lookup[i,j+1]))
 return points,faces,pins

OLD=[252,283,300,307,323,331,350,356]
NEW=[252,283,300,306,314,317,327,333]
def edit_time(x):
 """Monotone C1 edit map, unchanged prep and translated downstream clock."""
 if x<=OLD[0]:return x
 if x>=OLD[-1]:return x-23
 i=next(i for i in range(len(OLD)-1) if OLD[i]<=x<OLD[i+1]);h=OLD[i+1]-OLD[i];t=(x-OLD[i])/h
 slopes=[(NEW[j+1]-NEW[j])/(OLD[j+1]-OLD[j]) for j in range(len(OLD)-1)]
 def slope(j):
  if OLD[j]==350:return .5  # retain the faster descent right through contact
  if j==0 or j==len(OLD)-1:return 1.
  a=OLD[j]-OLD[j-1];b=OLD[j+1]-OLD[j];w1=2*b+a;w2=b+2*a
  return (w1+w2)/(w1/slopes[j-1]+w2/slopes[j])
 return (2*t**3-3*t*t+1)*NEW[i]+(t**3-2*t*t+t)*h*slope(i)+(-2*t**3+3*t*t)*NEW[i+1]+(t**3-t*t)*h*slope(i+1)
