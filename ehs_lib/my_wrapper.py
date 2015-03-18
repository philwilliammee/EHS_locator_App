'''
Created on Mar 12, 2015

@author: Phil Williammee
'''

def draw(htmlfile, locations):
    assert len(locations)
    f = open(htmlfile,'w')
    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    '''
    self.drawmap(f)
    self.drawgrids(f)
    self.drawpoints(f)
    self.drawradpoints(f)
    self.drawpaths(f,self.paths)
    '''
#####start here
    f.write('<title>FM GEO Locate</title>\n')
    f.write('<meta name="viewport" content="initial-scale=1.0, user-scalable=no">\n')
    f.write('<meta charset="utf-8">\n')
    f.write('<style>\n')
    f.write('html, body, #map-canvas {\n')
    f.write('height: 100%;\n')
    f.write('margin: 0px;\n')
    f.write('padding: 0px\n')
    f.write('}\n')
    f.write('</style>\n')
    f.write('<script src="https://maps.googleapis.com/maps/api/js?v=3.exp"></script>\n')
    f.write('<script>\n')
    
    f.write('var map;\n')
    f.write('function initialize() {\n')
    f.write('var mapOptions = {\n')
    f.write('zoom: 8,\n')
    f.write('center: new google.maps.LatLng(25.298535, 51.455254)//25.298535, 51.455254)\n')
    f.write('};\n')
    f.write('map = new google.maps.Map(document.getElementById("map-canvas"),\n')
    f.write('mapOptions);\n')
      
    f.write('setMarkers(map, sites);\n')
    f.write('infowindow = new google.maps.InfoWindow({\n')
    f.write('content: "loading..."\n')
    f.write('});\n')
    f.write('}\n')

    f.write('var sites = [\n')
    set_locations(f, locations)
    #f.write('["Abdelrahman Ahmed", 25.3269511, 51.5292181, 1, "Abdelrahman, Ahmed residence"],\n')
    #f.write('["Choi, Sunkyu", 25.2776372, 51.50524739999999, 2, "Choi, Sunkyu residence"],\n')
    #f.write('["Dargham, Soha", 25.2916097, 51.5304368, 3, "Dargham, Soha residence"],\n')
    #f.write('["Dargham, Soha" , 25.2916097, 51.5304368, 4, "Dargham, Soha residence"]\n')
    f.write('];\n')


    f.write('function setMarkers(map, markers) {\n')

    f.write('for (var i = 0; i < markers.length; i++) {\n')
    f.write('var sites = markers[i];\n')
    f.write('var siteLatLng = new google.maps.LatLng(sites[1], sites[2]);\n')
    f.write('var marker = new google.maps.Marker({\n')
    f.write('position: siteLatLng,\n')
    f.write('map: map,\n')
    f.write('title: sites[0],\n')
    f.write('zIndex: sites[3],\n')
    f.write('html: sites[4],\n')
    f.write('icon: sites[5]\n')
    f.write('});\n')

    f.write('var contentString = "Some content";\n')

    f.write('google.maps.event.addListener(marker, "click", function () {\n')
    f.write('infowindow.setContent(this.html);\n')
    f.write('infowindow.open(map, this);\n')
    f.write('});\n')
    f.write('}\n')
    f.write('}\n')

    f.write('google.maps.event.addDomListener(window, "load", initialize);\n')

    f.write('</script>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('<div id="map-canvas"></div>\n')
    f.write('</body>\n')
    f.write('</html>\n')
    f.close()
    
def set_locations(f, locs):
    #locations are in the form title latitude longitude index message
    tail = locs.pop()
    for loc in locs:
        if len(loc)>=5:
            s = '["'+str(loc[0])+ '",'+ str(loc[1]) + ',' + str(loc[2]) +',' + str(loc[3])+',"'+ str(loc[4])+'","'+ str(loc[-1])+'"'+'],\n'
            f.write(s)
    if len(loc)>=5:
        f.write('["'+str(tail[0])+ '",'+ str(tail[1]) + ',' + str(tail[2]) +',' + str(tail[3])+',"'+ str(tail[4])+'","'+ str(loc[-1])+'"'+']\n')
        
#loc =  [["Abdelrahman Ahmed", 25.3269511, 51.5292181, 1, "Abdelrahman, Ahmed residence"]]
#draw("test.html", loc)