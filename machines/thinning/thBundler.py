from SimPy.Simulation  import *
from machines.basics import UsesDriver, Operator
from functions import getCartesian, getCylindrical, getDistance, getDistanceSq
from math import pi, sin, asin, cos, sqrt
import matplotlib as mpl
import numpy as np
import copy
from terrain.pile import Pile, Bundle


"""
This file is now just a copy of the heads, should be rebuilt to a bundler
"""
###################################################
# Bundler
##################################################
class Bundler(Process,UsesDriver):
	"""
	This is the Bundler Class to be positioned in front of the machine. Will be run from machine.py
	"""
	def __init__(self, sim, driver, machine, name="Bundler"):
		UsesDriver.__init__(self,driver)
		Process.__init__(self, name, sim)

		self.m = machine
		self.color = 'blue'
		self.s = self.m.G.simParam
		self.pos = self.m.pos+[0,3]
		self.timeBundle = self.s['timeBundle']
		self.maxXSection = self.s['maxXSectionJ']
		self.xSectionThresh = 0.1#self.s['xSectionThreshJ']
		self.currentBundle = None
		self.forceBundler = False #Is set to true when bundler is filled or new pile from head does not fit
		
	def run(self):
		"""
		PEM of the bundler class.
		This method checks for a condition to run which is when it filled above threshold
		or the incoming pile does not fit. It makes a bundle with some set properties
		end dump it beside the road. 
		"""
		while True:
			yield waituntil, self, self.bundlerFilled
			print 'The bundler runs and makes a bundle of the pile'
			for c in self.startTheBundler(): yield c
			self.bundleIt()
			self.dumpBundle()
			self.resetBundle()
			self.cmnd([],self.s['timeBundle']-self.s['timeStartBundler'],auto=self.s['restOfBundling'])#true here means the rest is automatic
			for c in self.releaseDriver(): yield c
			print 'end of bundlerrun'
		
	def dumpBundle(self, direction=None):
		"""
		Releases the bundle at the current position. (And dumps the bundle in terrain)
		Needs to be fixed for bundler
		"""
		if direction is None: direction=pi/2

		#here the nodes of the bundle are set when the bundle is put in the terrain
		dumpPos=self.m.pos+[-2.5,3]#puts it beside the main road, NO IT DOESNT WORK
		cB=self.currentBundle
		c1=getCartesian([-cB.diameter/2,cB.length], origin=dumpPos, direction=direction, fromLocalCart=True)
		c2=getCartesian([-cB.diameter/2, 0], origin=dumpPos, direction=direction, fromLocalCart=True)
		c3=getCartesian([cB.diameter/2, 0], origin=dumpPos, direction=direction, fromLocalCart=True)
		c4=getCartesian([cB.diameter/2,cB.length], origin=dumpPos, direction=direction, fromLocalCart=True)
		cB.nodes=[c1,c2,c3,c4]
		
		self.m.G.terrain.piles.append(cB)#adds the pile to the list of piles in terrain
		self.m.G.terrain.addObstacle(cB)
		print '*Saved the current bundle in the terrain with',len(cB.trees),'trees in it'
	
	def startTheBundler(self):
		"""
		Adds the time it takes for the driver to push the "start bundling"-button.
		"""
		return self.cmnd([],self.s['timeStartBundler'], auto=self.s['startBundler'])



	def bundleIt(self):
		"""
		Performs the actual bundling of the trees. 
		"""
		cB=self.currentBundle
		cB.length = 5 #cut in five meter long sections
		cB.xSection=sum([t.dbh**2 for t in cB.trees])
  		cB.biomass = sum([t.weight for t in cB.trees])#initial weight no losses when doing the bundles
   		cB.radius = sqrt(cB.length**2+(cB.diameter/2)**2)
		
	def bundlerFilled(self):
		"""
		controls when the bundler runs and makes a bundle.
		"""
		if self.currentBundle:
			if self.forceBundler==True:
				return True
			elif self.currentBundle.xSection > self.xSectionThresh: return True
			else: return False
		else: return False

	def resetBundle(self):
		self.forceBundler=False
		self.currentBundle=None


	def draw(self):
		"""
		This is the drawing of the actual bundler without any trees in it
		"""
		pass 
