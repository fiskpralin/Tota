#!/usr/bin/env python
from math import *
from matplotlib.patches import Circle
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
import random

from terrain.obstacle import Obstacle
from terrain.terrain import *
from collision import *



class PlantMTerrain(Terrain):
	"""
	This class is for the planting machine terrain.

	Changes all the time due to new instructions, hard to keep it backwards compatible

	"""
	def __init__(self, G=None, ttype=None, areaPoly=None):
		if not G.areaPoly:
			G.areaPoly=[(0,0), (50,0), (50, 40), (0,40)] #default for stump-files.
		Terrain.__init__(self,G) 
		self.stumpFile='undefined'
		self.treeFile='undefined'
		if str(ttype)=='random':
			choices=['0','1','2', '3', '4', '5']
			ttype=random.choice(choices)
		elif ttype is None:
			ttype='5' #default
		else:
			ttype=str(ttype)
		self.ttype=ttype
		if ttype=='0':
			self.stumpFile=None #afforestration
			self.stumpsPerH=0
			self.boulderFreq=0
			self.meanBoulderV=0
			self.blockQuota=0
			self.groundModel= 0  #andersson's
		elif ttype=='1':
			self.stumpFile=554
			self.stumpsPerH=230
			self.boulderFreq=14
			self.meanBoulderV=1.8/1000.#dm3-m3
			self.blockQuota=0.25
			self.groundModel= 4  #andersson's
		elif ttype=='2':
			self.stumpFile=553
			self.stumpsPerH=635
			self.boulderFreq=14
			self.meanBoulderV=1.8/1000.#dm3-m3
			self.blockQuota=0.25
			self.groundModel= 4  #andersson's
		elif ttype=='3':
			self.stumpFile=554
			self.stumpsPerH=230
			self.boulderFreq=25
			self.meanBoulderV=3.6/1000.
			self.blockQuota=0.75
			self.groundModel=2  #andersson's
		elif ttype=='4':
			self.stumpFile=553
			self.stumpsPerH=635
			self.boulderFreq=25
			self.meanBoulderV=3.6/1000.
			self.blockQuota=0.75
			self.groundModel= 2  #andersson's
		elif ttype=='5': #medelhygget
			self.stumpsPerH=390
			self.boulderFreq=21
			self.meanBoulderV=3.0/1000.
			self.stumpFile=552
			self.blockQuota=0.55
			self.groundModel= 3  #andersson's
		else:
			raise Exception("ttype %s not correct"%(str(ttype),))
		if self.stumpFile=='undefined': #default..
			self.stumpFile='554'
		if self.stumpFile: self.readStumps()
		print "Terrain is initialized. Ttype: %s"%ttype
if __name__=="__main__":
	"""example code:"""
	terrain=Terrain()
	terrain.readTrees() #random
	terrain.draw()
	plt.show()
