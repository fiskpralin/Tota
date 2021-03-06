import os, sys #insert /dev to path so we can import these modules.
if __name__=='__main__':
	cmd_folder = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
	if not cmd_folder in sys.path:
		sys.path.insert(0, cmd_folder)

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline 
import time
import graph_alg.GIS.GIS as GIS #Gis folder -> GIS.py

import graph_alg.draw as draw

###
#This file is supposed to be a script that introduces how the interpolation and plotting works.
#I have taken out a lot of stuff that is implemented in the ExtendedGraph class, just to show the methods I've used so that everything is in one place..
###



#this is a sweref99 coordinate outside of sandviken. Needed in order to use lokal coordinates
globalOrigin=596673,6728492

#define our area...local coordinates.. a polygon (actually rectangle here) with 4 points

areaPoly=[(0, 0), (240, 0), (240, 480), (0, 480)]

print areaPoly

#get our x,y,z raster data for given area. numpy arrays
#I simply read some data from the GIS folder. See GIS/grid/.. for the files used.
#readTerrain function is very simple, what you need to know is that it scan's through the .asc x,y,z data and stores all points that are inside areaPoly polygon.
t_x,t_y,t_z=GIS.readTerrain(globalOrigin=globalOrigin, areaPoly=areaPoly)

#draw... some routines I have written for plotting... simple to use
fig=plt.figure()
ax=fig.add_subplot(121)
ax=draw.plotBackground(globalOrigin=globalOrigin , areaPoly=areaPoly, ax=ax)
#above localizes us in the flight photo 672_59_11 found in GIS folder and uses photo as background
ax=draw.plot2DContour(t_x,t_y,t_z,ax, w=2) #plots contours

#interpolate...I use a scipy interpolator called RectBivariateSpline.. google it for more info.

xlist=t_x[:,0] #just the variations needed, not the 2D-matrix
ylist=t_y[0,:]

interpol=RectBivariateSpline(xlist, ylist, t_z) #used pretty much everytime we need the height of a specific point. Implemented in fortran and very fast


#we now have an interpolation and can use interpol to get height in pretty much every point possible. 

#two arbitrary points:
p1=(200.3454, 300.45)
p2=(100.343,480.454) 
points=200 #a lot of points along above line.
x=np.linspace(p1[0], p2[0], points)
y=np.linspace(p1[1], p2[1], points)
z=interpol.ev(x,y) #gives array of z for x,y list of positions. we are done..

plt.plot(x,y, 'o') #plot the points defined by x, y arrays
ax2=fig.add_subplot(122)
d=np.sqrt(x**2+y**2)-np.sqrt(x[0]**2+y[0]**2) #distance from start point
ax2.set_xlabel('d')
ax2.plot(d,z, lw=2) #plot z along line...
ax2.set_title('The interpolated height along the line specified to the right.')
plt.show()

#we are done and have z data for this point. What we want to do is to given t_x,t_y and t_z data above get the gradient or roll for an arbitrary point..
