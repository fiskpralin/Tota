 
import networkx as nx
from math import *

import graph_alg.grid as grid
import graph_alg.costFunctions as cf
import graph_alg.graph_operations as go
from functions import getDistance, getDistanceSq



def getClosestIntersection(G, n):
	"""
	returns the closest intersection, i.e. d(n)>=3

	can be refined by using indexing
	"""
	closestD=1e10
	closest=None
	for node in G.nodes():
		if node==n: continue
		if G.degree(node)<3: continue
		d=getDistanceSq(node, n[0:2])
		if d<closestD:
			closestD=d
			closest=node
	return closestD, closest

def crazyIdea(L=24, areaPoly=None, refinementRatio=5):
	"""
	just testing out an idea..
	"""
	G=grid.SqGridGraph(areaPoly=areaPoly, L=L/float(refinementRatio))
	R=copy.deepcopy(G)

	#so.. loop thorugh them all and take some of them away.

	inf = 1e15
	eps=1e-9
	lastAdded=None
	origin=G.origin
	if not origin: raise Exception('need info about origin')
	#first, modify the weight of the edges a couple of times. Warmup
	for i in xrange(1):
		paths=nx.algorithms.shortest_paths.weighted.single_source_dijkstra(R, origin)
		for node in R.nodes(data=True):
			p1=paths[1][node[0]]
			p1.reverse()
			if len(p1)<=1: continue
			e=[p1[0], p1[1]] #edge closest to point
			e.append(R.get_edge_data(e[0], e[1]))
			R.remove_edge(e[0], e[1]) #temporary remove to get loop
			p2=nx.dijkstra_path(R,origin, node[0])
			R.add_edges_from([tuple(e)]) #reset road
			for path in p1,p2:
				last=None
				for nTmp in path:
					if last:
						d=R.get_edge_data(*(last, nTmp)) #should always exist if designed properly
						d['visits']+=1
					last=nTmp
		#update edge weight
		for edge in R.edges(data=True):
			modifyEdge(edge,R)
			edge[2]['visits']=0 #zero up.
	paths=nx.algorithms.shortest_paths.weighted.single_source_dijkstra(R, origin)
	#now, start for real and save away all kind of info about the paths.
	for node in R.nodes(data=True):
		p1=paths[1][node[0]]
		p1.reverse()
		node[1]['shortest_path']=p1
		if len (p1)<=1:
			node[1]['second_shortest']=p1
		else:
			e=[p1[0], p1[1]] #edge closest to point
			e.append(R.get_edge_data(e[0], e[1]))
			R.remove_edge(e[0], e[1]) #temporary remove to get loop
			p2=nx.dijkstra_path(R,origin, node[0])
			node[1]['second_shortest']=p2
			R.add_edges_from([tuple(e)]) #reset road
			#ax=testRoads(R, p1, p2, ax) #used for debugging
			for path in p1,p2:
				last=None
				for nTmp in path:
					if last:
						d=R.get_edge_data(*(last, nTmp)) #should always exist if designed properly
						d['visits']+=1
						if not node in d['visited_from_node']: d['visited_from_node'].append(node)
					last=nTmp
	remList=[]
	addList=[]
	for eTmp in R.edges(data=False):
		e=copy.copy(eTmp) #copy, so we can remove them and then add them and so on.
		e2=R.get_edge_data(*e) #not a copy, reference to real dict.
		e=list(e)
		e.append(e2)
		e[2]['origin_dist']=distToOrigin(e,R)
		e[2]['c']=cf.routingCost(R, e, storeData=False)
		remList.append(e)
	i=1
	#at this point, the visited thing should be updated
	drawmod=1e10
	while len(remList)>0:
		i=i+1
		for edge in R.edges(data=True):
			modifyEdge(edge,R) #change the weight slightly as a function of visits"""
		if i%drawmod== 0: #for debugging
			plt.ion()
			if ax: plt.cla()
			ax=draw_custom(R, ax=ax, edge_visits=True)
			ax.set_ylim(-1)
			plt.draw()
			raw_input('press any key')
		first=True
		e1=False
		while first or e[0:2]!=e1[0:2]:
			e1=remList[0] #takes the last item in the list.
			e1[2]=R.get_edge_data(e1[0], e1[1]) #edgelist is a copy, this is not.
			c=cf.routingCost(R, e1, storeData=True) #also updates e[2]['c']
			#e1[2]=R.get_edge_data(e1[0], e1[1])
			e1[2]['c']=c #-e1[2]['origin_dist']*0.1 #origin dist just to experiment.
			if c>=inf:
				remList.remove(remList[0]) #cannot be empty at this time
				if len(remList)==0: break
			remList=sorted(remList, key=lambda edge: edge[2]['c']+edge[2]['visits'])#-edge[2]['origin_dist']*0.1) #first sort
			e=remList[0] # could be the same..
			if first: first=False
		print e[2]['c'], e[0:2]
		if i%drawmod==0:
			if not ax: ax=draw_custom(R, ax=ax, edge_visits=True)
			draw_road(R.node[e1[0]]['shortest_path'], ax, 'r')
			draw_road(R.node[e1[0]]['second_shortest'], ax, 'r')
			#draw_road(R.node[e1[0]]['new_second_shortest'], ax, 'b')
			#draw_road(R.node[e1[0]]['new_shortest_path'], ax, 'b')
			plt.draw()
			print e[2]['c']
			#raw_input('fsdfs')
		e[2]=R.get_edge_data(*e) # Update again, to get "new second shortest"
		if random.uniform(0,1)<0.33:
			print "adds"
			added, addList, remList, lastAdded=addListProcedure(addList,remList,R,e[2]['c'],i)
			if added: continue #go up to while again
		if len(remList)==0: break
		#print "will remove:", remList[0][0:2]
		remList.remove(remList[0]) #we know now that no edge is added this "round"
		#print "is it still there?"
		#for r in remList:
		#	print r[0:2]
		#print "removed, next", remList[0][0:2]
		if e[2]['c']>eps and aCap and R.areaCover-go.singleRoadSegmentCoverage(e, R, remove=True)*G.Ainv<aCap:
			print "tries to exit", e[0:2], "ec:", e[2]['c']
			added, addList, remList, lastAdded=addListProcedure(addList,remList,R,e[2]['c'],i,lastAdded)
			if added:
				remList.append(e) #since we just removed it and didn't remove it from graph
				continue
			else:
				break #we are finished
		if R.degree(e[0])>2 and R.degree(e[1])>2 and c<inf: #loop condition, at least degree 3
			remove_edge(e, R) #remove from R.
			addList.append(e) #add to lists for potential adding again.
			e[2]['c']*=-1 #reverse, we now gain c by adding it again.
			e[2]['i_added']=i
			#this procedure can most certainly be speeded up, expensive operations.
			update_after_mod(e,R)
	for e in R.edges(data=True):
		modifyEdge(e, R, reset=True)
	print "construction finished."
	print "road area coverage:", R.areaCover
	print "total area:", G.A
	return R

def modifyEdge(edge, R, reset=False):
	"""
	used systematically in order to deal with the "taxi-cab-geometry-problem", i.e. there
	are several paths of equal length between two specific points.
	"""
	if reset:
		edge[2]['weight']=R.edgeWeightCalc(edge[0], edge[1])
	else:
		edge[2]['weight']=R.edgeWeightCalc(edge[0], edge[1])*(1-float(edge[2]['visits'])/(4.0*float(R.elements)))
		
def addListProcedure(addList,remList, R, c,i,lastAdded=None):
	"""
	does some stuff connected to addList

	This is the thing that adds complexity. 98% of the execution time is spent here.. insane..
	"""
	#print "goes into loop..."
	#routingcost is really expensive, procedure to minimize number of calls.
	for aTmp in addList:
		cTmp=cf.routingCost(R,aTmp,storeData=False, add=True)
		if abs(cTmp)<c and i-aTmp[2]['i_added']>1000: addList.remove(aTmp) #strange procedure, modify later.
		else: aTmp[2]['c']=cTmp
	if len(addList)!=0:
		addList=sorted(addList, key=lambda edge: edge[2]['c']) #first sort
		a=addList[0]
		eps=1e-9 #tolerance
		if a[2]['c']<-eps and abs(a[2]['c'])>c+eps: #add edge again
			if lastAdded and lastAdded==a[0:2]:
				print 'noWay'
				return False, addList, remList, lastAdded
			lastAdded=a[0:2]
			print "adds. e:", a[0:2], " ec:", c, "benefit:", a[2]['c']
			addList.remove(a)
			#for at in addList:
			#	if at[0:2]==[(120.0, 168.0), (120.0, 144.0)]: raise Exception('edge was never removed..')
			a[2]['c']*=-1 #you don't get any benefit from it now.
			add_edge(a, R)
			remList.append(a)
			#print i, "1R has (312.0, 96.0), (312.0, 120.0):", R.has_edge((312.0, 96.0), (312.0, 120.0))
			return True, addList, remList, lastAdded #next while cycle
	return False, addList, remList, lastAdded
def findAwsomeDiagonals(addList,R):
	"""
	identifies hugely trafficed bends, and straightens them out.
	"in production-not yet done"
	"""
	pass
	
	#first, list the 


def update_after_mod(e,R):
	"""
	updates graph after edge was removed or added. Assumes that routingcost function has stored correct data before.
	"""
	for nTmp in e[2]['visited_from_node']: #each node that visited the removed edge
		P1=nTmp[1]['second_shortest']+nTmp[1]['shortest_path']
		P2=nTmp[1]['new_second_shortest']+nTmp[1]['new_shortest_path']
		#ax=testRoads(R, nTmp[1]['new_shortest_path'], nTmp[1]['new_second_shortest'], ax) #used for debugging
		for path, diff in (P1, -1), (P2, 1):
			last=path[0]
			for nTmp2 in path[1:]: #loop over the edges in path
				if nTmp2==last: continue #overlap between roads, skip
				try:
					d=R.get_edge_data(*(last, nTmp2))
					d['visits']=d['visits']+diff
					if diff==-1 and nTmp in d['visited_from_node']:
						d['visited_from_node'].remove(nTmp)
					elif not nTmp in d['visited_from_node']:
						d['visited_from_node'].append(nTmp)
				except ValueError:
					print "remove failed", d['visited_from_node']
					print d['visited_from_node'].count(nTmp),nTmp
					raise Exception('sads')
				except:
					if not ((last==e[0] and nTmp2==e[1]) or (last==e[1] and nTmp2==e[0])): #if not the removed edge
						raise Exception('tries to modify edge that does not exist, something is wrong')
				last=nTmp2
		nTmp[1]['shortest_path']=nTmp[1]['new_shortest_path']
		nTmp[1]['second_shortest']=nTmp[1]['new_second_shortest']

def remove_edge(e, R):
	"""removes edge e from R and updates related statistics"""
	R.remove_edge(e[0], e[1])
	update_after_mod(e,R)

def add_edge(e, R):
	"""adds e to R and updates statistics."""
	R.add_edges_from([tuple(e)])
	a=R.get_edge_data(e[0], e[1])
	a['c']=cf.routingCost(R,e,storeData=True)
	#update_after_mod(e,R)
	