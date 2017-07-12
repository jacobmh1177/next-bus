import urllib.request
import xml.etree.ElementTree as ET
import collections

NEXT_BUS_PREDICTION_URL = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions'

def get_all_routes():
	routeURL = 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni'
	response = urllib.request.urlopen(routeURL)
	root = ET.fromstring(response.read())
	numRoutes = len(root)
	routeObjs = [{} for _ in range(numRoutes)]
	for routeObj, route in zip(routeObjs, root):
		try:
			routeObj['tag'] = route.attrib['tag']
			routeObj['title'] = route.attrib['title']
		except:
			continue
	return routeObjs

def get_stop_id(routeID, stopName, agency='sf-muni'):
	routeConfigURL = 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a={}&r={}'.format(agency, routeID)
	response = urllib.request.urlopen(routeConfigURL)
	root = ET.fromstring(response.read())
	for stop in root[0]:
		try:
			if stop.attrib['title'] == stopName: return stop.attrib['tag']
		except:
			continue
	return None

def get_predictions(stopName='Church St Station Outbound', agency='sf-muni'):
	allPredictions = []
	mainRoutes = []
	allRoutes = get_all_routes()
	for index, route in enumerate(allRoutes):
		if not route['tag'][0].isdigit(): 
			print(route['tag'])
			mainRoutes.append(route)

	for index, route in enumerate(mainRoutes):
		routeID = route['tag']
		stopID = get_stop_id(routeID, stopName)
		if stopID == None: continue
		predictionURL = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a={}&r={}&s={}'.format(agency, routeID, stopID)
		response = urllib.request.urlopen(predictionURL)
		respString = response.read()
		root = ET.fromstring(respString)
		allPredictions.append((routeID, root))

	return allPredictions

def parse_predictions(predictionList):
	parsedPredictions = collections.defaultdict(list)
	for routeId, pred in predictionList:
		trains = []
		counter = 0
		for p in pred[0][0]:
			if counter == 2: break
			time = p.attrib['minutes']
			trains.append({'time':time})
			counter += 1
		parsedPredictions[routeId] = trains
	return parsedPredictions

if __name__ == '__main__':
	predictionList = get_predictions()
	preds = parse_predictions(predictionList)