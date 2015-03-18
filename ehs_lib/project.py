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

import copy
import webbrowser
from geo_locator import locator, asset_locator
from my_wrapper import draw
import os
DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(DIR, 'html_lib')
try:
    os.makedirs(DEST_DIR)
except OSError:
    pass # already exists
           
class project():
    def __init__(self, parent):
        self.parent = parent
        self.path =""#pat
        self.name = ""
        self.html_name = ""
        self.save = False
        #data should be in the form: name, lat, long, excel_row, name
        self.lost_data = []
        self.comined_data = []
        self.saved_data = []
        self.lost_asset = []
        self.saved_asset_data = []
        self.text_loc = []
        #a list of list of [[name, adress],[n2,a2],...]
        self.names_adresses = []
        
    def get_data(self):
        #use len(self.saved_asset_data) to seperate data
        my_locator = locator(update_log=self.parent.log)
        self.combined_data = my_locator.combine_markers(copy.deepcopy(self.saved_asset_data + self.saved_data))
        return self.combined_data
    
    def import_address_data(self, excel_path):
        text_loc = []
        my_locator = locator(update_log=self.parent.log)
        my_locator.run_locator(excel_path=excel_path, html_name=self.html_name)
        #save the data to the project
        self.lost_data, self.saved_data = copy.deepcopy(my_locator.cant_find), copy.deepcopy(my_locator.found_cord) 

        for loc in self.get_data():     
            text_loc.append(get_img_loc(float(loc[1]), float(loc[2])))
        self.build_open_html(False)
        self.text_loc = text_loc
        print len(text_loc)
        return text_loc
    
    def import_asset_data(self, excel_path):
        text_loc = []
        '''
        #save the data to the project
        self.project.lost_asset, self.project.saved_asset_data = copy.deepcopy(self.asset_locator.cant_find), copy.deepcopy(self.asset_locator.found_cord)   
        for loc in self.project.get_data():#self.asset_locator.comined_cord:      
            text_loc.append(get_img_loc(float(loc[1]), float(loc[2])))
        self.project.build_open_html(False)
        '''
        my_locator = asset_locator(update_log=self.parent.log)
        my_locator.run_locator(excel_path=excel_path, html_name=self.html_name)
        #save the data to the project
        self.lost_asset, self.saved_asset_data = copy.deepcopy(my_locator.cant_find), copy.deepcopy(my_locator.found_cord) 
        for loc in self.get_data():     
            text_loc.append(get_img_loc(float(loc[1]), float(loc[2])))
        print len(text_loc)
        self.build_open_html(False)
        self.text_loc = text_loc
        return text_loc
 
    def save_project(self, filename):
        if self.name != "":
            self.build_open_html(False)
            prjFile = open(filename, "w")
            print>>prjFile, "n " + self.name.replace(" ", "_")       
            print>>prjFile, "h " + str(self.html_name)
            print>>prjFile, "d " + str(self.saved_data)
            print>>prjFile, "a " + str(self.saved_asset_data)
            self.save = False
        else: self.parent.log("Please create or open a new project")

    def load_project(self, filename):
        error = False
        f = read_file(filename)
        lines = get_lines(f)#a dictionary
        if "n" in lines.keys():
            names = lines["n"]
            if len(names) > 0:
                a = names[-1]
                a = repr(a).replace("\\",",")[1:-1]#remove backslash
                a = a.split(',')
                self.name = a[-1]
            else:
                self.names=""
        else: error = True
        print "loaded file name", self.name
        if "h" in lines.keys():
            html_name = lines["h"]
            if len(html_name ) > 0:
                self.html_name = html_name[-1]
        else: error = True

        if "d" in lines.keys():
            self.saved_data, s = strip_file(lines["d"])
            
        if "a" in lines.keys():
            self.saved_asset_data, ss = strip_file(lines["a"])
        if error == True:
            self.parent.log("error loading project, try saving projects without white spaces or commas")
        if s:
            self.parent.log(s)  
        if ss:
            self.parent.log(ss)
        
        self.save = False
        return error
    
    def load_html(self, fiel ="./EHS_locator_test.html" ):
        #currently unused
        if self.name != "":
            f = read_file(fiel, True)
            data=[]
            for line in f[29:]:
                if line[0]=="[":
                    line = line.replace("[", "")
                    line = line.replace("]", "")
                    line = line.replace('"', "")
                    line = line.split(",")
                    line = filter(None, line)       
                    data.append(line)
            return data
        else: self.parent.log("Please create or open a new project")
    
    def build_open_html(self, gmap):
        #build a hyml file that puts markers with identifiers at each coordinate
        #save the fm_locator file to the local folder
        path = os.path.join(DEST_DIR,self.html_name)
        print path
        if self.name != "" and self.html_name != "" and len(self.get_data()) > 1:
            green = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,00FF00,000000&ext=.png'
            blue = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,0000FF,000000&ext=.png'
            red = 'http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,FF0000,000000&ext=.png'
            filter_cord_info = copy.deepcopy(self.get_data())
            for i , val in enumerate(filter_cord_info):
                if i >= len(self.saved_asset_data):
                    val.append(red)
                else: val.append(blue)
            draw((path), filter_cord_info)
            if gmap==True:
                self.open_gmap(path)
        else: self.parent.log("Please create or open a new project")
            
    def open_gmap(self, f_name):
        f_name = os.path.join(DEST_DIR,self.html_name)
        print f_name
        if self.name != "":
            try:
                webbrowser.open_new_tab(f_name) 
            except Exception as e:
                self.parent.log("could not open "+f_name+" error "+str(e))
        else: self.parent.log("Please create or open a new project")
            
def read_file(f_loc, r_n=False):
    #@warning: this may have problems with blank spaces in a line
    with open(str(f_loc), 'r') as f:
        if r_n:#remove newline
            lines = f.read().splitlines()
        else:#leave raw
            lines = f.readlines()
        return lines
     
def get_lines(lines):
    #returns a dictionary with the first value as the key
    d={}
    for line in lines:
        if line[0] == "#": continue
        d[line[0]] = line[1:].split()#strip()
        #[x.strip() for x in line[1:].split()]
    return d

def strip_file(a, n=5):
    #removes extra characters from text strings
    s = ""
    aa = ",".join(a)
    aa = aa.replace(',,', ',')
    aa = aa.replace('[','')
    aa = aa.replace(']','')
    aa = aa.replace("'",'')
    aa = aa.split(',')
    na = []
    for a in aa:
        if a=='u':
            continue
        else:
            na.append(a)
    aa = chunks(na, n)
    
    for x in aa:
        if len(x)<n:
            s = ("Warning found bad or no data saved. data = "+str(x))
            aa.remove(x)
    return aa, s

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def get_img_loc(y, x):
    #recieves a latitude and longitude and converts it to a position on the image
    #original image size 4233, 4220
    #Lower Left lat long coord 
    #ylat = [25.369572, 25.206881]#bottom, top
    #xlon = [51.387591, 51.607245]#left right
    ylat = [25.385, 25.215]#top, bottom  make top bigger moves it down
    xlon = [51.41, 51.607245]#left right make left bigger moves it left
    newx = ard_map(x, xlon[0],xlon[1], 0, 4233)
    newy = ard_map(y, ylat[0],ylat[1], 0, 4220)
    return newx, newy

def ard_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min   
