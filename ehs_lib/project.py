#!/usr/bin/env python2.7

""" 
  Description: RunLocator is the main application it contains the wx.GUI 
      and all event handlers to interface with the user
  Created on Mar 17, 2015
  @author: Philip Wiliammee
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import copy                             #deep copies of lists of lists
import webbrowser                       # opens the 
#import geo_locator as geo               # reads excel file gmaps the coord
                                        # extends locator for assets adresses                                    
from my_wrapper import draw             # writes the html file
import os                               # to find th path
import cPickle                          # saves the proct variables
#import csv                             # write binaries unused
import time

DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(DIR, 'html_lib')
try:
    os.makedirs(DEST_DIR)
except OSError:
    pass # already exists
     
class project():
    def __init__(self):
        self.proj_name = ""             # the name of the project .ehs extension see save_proj
        self.html_name = ""             #name of the htm file is the same as the project name.html
        #{'John_Smith': {'verified': False, 'assets': (None, None, None), 'date_updated': '20/03/2015', 'coord': (0,0), 'address': 'doha,qatar', 'id': 0},
        self.employees = {}             #a dictionary of employee values
        self.save = False               # unimplemented
        self.lost_data = []             # used by Run locator to save a list of bad adresses
        self.saved_data = []            # a list of red markers
        self.saved_asset_data = []      #a list of blue markers
        self.marker_loc = []            #a list of combined markers [number, coordinates locations, number, combined names, color]
        self.excel_rows = {'SAP':[[0,'name'],[3,'address']], 
                           'new':[[0, 'last'],[1,'first'],[6,'zone'],[7,'street'],[8,'building']], 
                           'students':[[1, 'last'],[2,'first'],[10,'addr1'],[11,'addr2'],[12,'country']]}
        
    def set_employees(self, emps):
        #@todo this needs more work
        for e in emps:
            v = vars(e)
            name = v.pop('name', 0)
            if name in self.employees.keys() and self.employees[name]['verified']==True:
                pass
            else:
                self.employees[name] = v
                self.employees[name]['date']=(time.strftime("%d/%m/%Y"))
    
    def get_update_marker(self):
        veri_cord=[]
        cord = []
        for name in self.employees.keys():
            if 'student' in self.employees[name].keys():
                veri_cord.append([name, 
                             self.employees[name]['coord'][0], 
                             self.employees[name]['coord'][1], 
                             self.employees[name]['id'],
                             name, 'GREEN'])
            
            elif self.employees[name]['verified']==True:
                veri_cord.append([name, 
                             self.employees[name]['coord'][0], 
                             self.employees[name]['coord'][1], 
                             self.employees[name]['id'],
                             name, 'BLUE'])
            elif self.employees[name]['verified']==False: 
                cord.append([name, 
                             self.employees[name]['coord'][0], 
                             self.employees[name]['coord'][1], 
                             self.employees[name]['id'],
                             name, 'RED'])
        #if saved data cord = data cord do not combine them
        self.saved_data = combine_markers(cord)
        self.saved_asset_data =  combine_markers(veri_cord)
        #marker should be the only class that is ever modified
        self.marker_loc = copy.deepcopy(self.saved_asset_data + self.saved_data)
        #should build open html be called here?
        return copy.deepcopy(self.marker_loc)

    def save_project(self, fname):
        f = file(fname, 'wb')
        cPickle.dump(self, f, protocol=cPickle.HIGHEST_PROTOCOL)
        f.close()

    def load_project(self, fname):
        f = file(fname, 'rb')
        loaded_obj = cPickle.load(f)
        f.close()
        return loaded_obj
    
    def build_open_html(self, gmap):
        # get_update_marker should be called before this to get updated markers
        # build a html java script file that puts markers with identifiers at each coordinate
        # save the fm_locator file to the local folder
        path = os.path.join(DEST_DIR, self.html_name)
        if self.proj_name != "" and self.html_name != "":
            green = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,00FF00,000000&ext=.png'
            blue = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,0000FF,000000&ext=.png'
            red = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,FF0000,000000&ext=.png'
            filter_cord_info = copy.deepcopy(self.marker_loc)
            for i , val in enumerate(filter_cord_info):
                #remove the errors from the list
                if val[1] == None or val[2] == None:
                    del filter_cord_info[i]
                    continue
                if val[5] == 'RED': val[5] = red
                elif val[5] == 'BLUE': val[5] = blue

                else: val[5] = green
            draw((path), filter_cord_info)
            if gmap==True:
                self.open_gmap(path)
        else: return("Please create or open a new project")
            
    def open_gmap(self, f_name):
        #opens the goolgle map display in the web browser
        # the html file is generated by self.build_open_html()
        f_name = os.path.join(DEST_DIR,self.html_name)
        if self.proj_name != "":
            try:
                webbrowser.open_new_tab(f_name) 
            except Exception as e:
                return ("could not open "+f_name+" error "+str(e))
        else: return ("Please create or open a new project")

def combine_markers(locator_info ):
    #@todo improve eficiency this is poorly done
    #find people who live in same place and combine names
    #remove the like locations and return a unique set of locations and names at those coordinates
    combine_cord_info = copy.deepcopy(locator_info)#copy the list
    location={}
    #combine the names
    for x in  combine_cord_info:
        assert len(x)==6, "geo_locator recieved data packet of the wrong size"
        #x[1:2] = coordinates x[4] is combined name
        location.setdefault((x[1],x[2]), []).append(x[4])#setdefault to append a dictionarry
        vals = location[x[1],x[2]]
        #@todo namesx[0] should be the street address
        x[4]= ': '.join(vals) 
                  
    #remove the duplicates because still contains duplicates
    count = 0
    filter_cord_info = []
    for i, l in enumerate(combine_cord_info):
        tt = [[tt[1],tt[2]] for tt in combine_cord_info[i+1:]]
        if [l[1],l[2]] in tt:
            continue #with next iteration of the loop    
        #else place ID to location
        l[0]=str(count)
        filter_cord_info.append(l)
        count +=1
    return filter_cord_info

def ard_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min   
