#!/usr/bin/env python2.7

""" 
  Description: geo_locator a specialized class to receive names, 
  address from a excel spread sheet and look them up with google maps, and returns 
  lat, long coordinates.
  Asset locator receives name, building, street, area and finds coordinates @"http://myqplace.info/"
  
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

from pygeocoder import Geocoder
#path = 'excel_adress_test.xlsx' 
import xlrd
import requests
import copy


class locator():
    def __init__(self, excel_path='./excel_adress_test.xlsx', update_log=None):
        self.excel_file = excel_path
        self.log = update_log           #get coordinates updater to let you know its running
        self.names = []
        self.adresses = []
        self.cant_find = []
        self.found_cord = []
        self.comined_cord = []

    def run_locator(self, excel_path, html_name="FM_locator_test.html"):
        self.excel_file = excel_path
        #list of names and adresses in excel cells rows 1, 3
        self.names, self.adresses = self.get_names_addresses(self.excel_file)
        #find the coordinates(list of names, location, id, names) of adresses
        self.cant_find, self.found_cord = self.get_coordinates(copy.deepcopy(self.names), copy.deepcopy(self.adresses))
        #combine names of people who live at the same location
        self.comined_cord = self.combine_markers(copy.deepcopy(self.found_cord))
        #self.build_open_htm(list(self.comined_cord), f_name=html_name, gmap=do_map)
        self.display_data("locator found "+str(len(self.found_cord))+" adresses, cant find " + str(len(self.cant_find)) )
        
    
    def display_data(self, s):
        if self.log: self.log(s)
        else: print s
        
    def get_names_addresses(self, excel_path):
        #opens an excel file and returns coumn1 and column 3 of all rows on page1
        #removes repeated names
        workbook = xlrd.open_workbook(excel_path)
        worksheet = workbook.sheet_by_name(workbook.sheet_names()[0])
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = -1
        names = []
        adresses = []
        #@todo improve this needs a generator
        while curr_row < num_rows:
            curr_row += 1
            curr_cell = -1
            while curr_cell < num_cells:
                curr_cell += 1
                if curr_cell == 0 and curr_row != 0:#remove header
                    val = worksheet.cell_value(curr_row, curr_cell)
                    #print val
                    s=val.split(',')
                    s = [str(s[1]), str(s[0])]
                    s = "_".join(s)
                    s= s.replace (" ", "_")
                    #remove repeats these are family members
                    names.append(s)
                elif curr_cell == 3 and curr_row != 0:
                    adresses.append(worksheet.cell_value(curr_row, curr_cell))
        #every name should have a corespoding adress
        #print len(names), len(adresses)
        assert len(names)==len(adresses)
        #remove repeated names
        old_name = None
        f_names=[]
        f_adresses=[]
        for n,a in zip(names, adresses):
            if n == old_name:
                continue
            f_names.append(n)
            f_adresses.append(a)
            old_name = n
        
        return f_names, f_adresses
    
    def get_coordinates(self, names, adresses):  
        # recieves a list of names and adresses both list should be same length and 
        # name position should match adress position
        # searches geocoder for matching adress returns a list of lists formated(name, lat, long, position, name
        # returns the names and adresses of poitions it could not find  
        assert len(names) == len(adresses)             
        cord_dict={}
        locator_info = []
        count = 1
        errors = []
        s=""
        for n, a in zip(names, adresses):
            cord_dict[n]=a
            #a = a.replace(",", " ")
            try:
                results = Geocoder.geocode(a)
                #print n, (results[0].coordinates),count,n+("residence")
                locator_info.append([n, results[0].coordinates[0], results[0].coordinates[1] ,count, n])
                s=("found "+n+" loc "+a+" @cord"+str(results[0].coordinates))
                count +=1
            except Exception as e:
                errors.append((n,a))
                s = s=("found "+n+" loc "+a+" G_error "+ str(e))
            self.display_data(s)
        
        return errors, locator_info
    
    def combine_markers(self, locator_info ):
        #@todo improve eficiency this is poorly done
        #find people who live in same place and combine names
        #remove the like locations and return a unique set of locations and names at those coordinates
        combine_cord_info = copy.deepcopy(locator_info)#copy the list
        location={}
        for x in  combine_cord_info:
            assert len(x)>=5, "geo_locator recieved data packet of the wrong size"
            location.setdefault((x[1],x[2]), []).append(x[4])
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

class asset_locator(locator):     
    def get_names_addresses(self, excel_path):
        #opens an excel file and returns coumn1 last,2first 7,8,9 zone street building
        #removes repeat names if there are any
        workbook = xlrd.open_workbook(excel_path)
        #print workbook.sheet_names()

        worksheet = workbook.sheet_by_name(workbook.sheet_names()[0])

        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = -1
        lnames = []
        fnames = []
        zone,street,building = [],[],[]
        #@todo improve this needs a generator
        while curr_row < num_rows:
            curr_row += 1
            curr_cell = -1
            while curr_cell < num_cells:
                curr_cell += 1
                if curr_cell == 0 and curr_row != 0:#remove  header
                    #remove repeats these are family members
                    lnames.append(worksheet.cell_value(curr_row, curr_cell).replace (" ", "_"))
                elif curr_cell == 1  and curr_row != 0:
                    fnames.append(worksheet.cell_value(curr_row, curr_cell).replace (" ", "_"))               
                elif curr_cell == 6 and curr_row != 0:
                    zone.append(worksheet.cell_value(curr_row, curr_cell))
                elif curr_cell == 7 and curr_row != 0:
                    street.append(worksheet.cell_value(curr_row, curr_cell))
                elif curr_cell == 8 and curr_row != 0:
                    building.append(worksheet.cell_value(curr_row, curr_cell))
        #every name should have a corespoding adress
        assert len(lnames)==len(fnames)==len(zone)==len(building)==len(street)
        names = ['_'.join([str(f),str(l)])for f,l in zip(fnames,lnames)]
        adresses =[[z,s,b] for z,s,b in zip(zone,street,building)]
        #remove repeated names
        old_name = None
        f_names=[]
        f_adresses=[]
        for n,a in zip(names, adresses):
            if n == old_name:
                continue
            f_names.append(n)
            f_adresses.append(a)
            old_name = n
        
        return f_names, f_adresses
        
    def get_coordinates(self, names, adresses):  
        # recieves a list of names and adresses both list should be same length and 
        # name position should match adress position
        # searches geocoder for matching adress returns a list of lists formated(name, lat, long, position, name
        # returns the names and adresses of poitions it could not find  
        assert len(names) == len(adresses)  
        count = 1
        errors = []
        s=""           
        locator_info =[]
        for n, l in zip(names,adresses):#remove the header
            payload = {'b': str(l[2]), 's': str(l[1]), 'z':str(l[0])}
            #print payload
            try:
                r = requests.get("http://myqplace.info/", 
                        params= {'b': str(int(l[2])), 's': str(int(l[1])), 'z':str(int(l[0]))})
                
                #wrtite the data into a text file
                write_file("test_cord.txt", r)
                #read it and strip it
                fl = read_file("test_cord.txt", True)
                rec = strip_cord(fl)

                locator_info.append([n, float(rec[0][1]), float(rec[1][1]) ,count, n])
                count +=1
                s=("found "+n+" @cord " +str(rec))
            except Exception as e:
                errors.append((n))
                s=("found "+n+" error "+ str(e))
            self.display_data(s)   
  
        return errors, locator_info
    
    def combine_markers(self, locator_info ):
        #@todo improve eficiency this is poorly done
        #find people who live in same place and combine names
        #remove the like locations and return a unique set of locations and names at those coordinates
        combine_cord_info = copy.deepcopy(locator_info)#copy the list
        location={}
        for x in  combine_cord_info:
            assert len(x)>=5, "geo_locator recieved data packet of the wrong size"
            location.setdefault((x[1],x[2]), []).append(x[4])
            vals = location[x[1],x[2]]
            #@todo namesx[0] should be the street address
            x[4]= ': '.join(vals) 
            
        #remove the duplicates because still contains duplicates
        count = 0
        filter_cord_info = []
        for i, l in enumerate(combine_cord_info):
            tt = [[tt[1],tt[2]] for tt in combine_cord_info[i+1:]]
            if [l[1],l[2]] in tt:
                continue

            #place ID to location
            l[0]=str(count)
            #l.append('http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,00FF00,000000&ext=.png')#red
            filter_cord_info.append(l)
            
            count +=1
        return filter_cord_info
    
def read_file(f_loc, r_n=False):
    with open(str(f_loc), 'r') as f:
        if r_n:#remove newline
            lines = f.read().splitlines()
        else:#leave raw
            lines = f.readlines()
        return lines

def write_file(f_name, r):
    chunk_size = 384
    with open(f_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)
    
def strip_cord(fl):
    coord = []
    for l in fl:
        if "Coordinates:" in l:
            #print l
            l = l[l.index("Coordinates:")+12:l.index("</td></tr><tr><td></td><td>")]#E</td>")]
            #dirty= l.split("Coordinates:", 1)[0]    
            l = l.translate(None,'</td>')
            l = l.translate(None,'</tr>')
            l = l.translate(None,'<tr>')
            l = l.translate(None,'<td>')      
            #N25.26599, E51.527674 25&deg; 15' 57.6'' N,51&deg; 31' 39.6'' 
            l = l.split(',')
            for ll in l:
                ll = ll.strip()
                coord.append([ll[0], ll[1:]])
    return coord
    
if __name__=="__main__":
    '''
    test = asset_locator(excel_path='./Copy of Residential Address Information (3).xls')
    test.run_locator(test.excel_file)
    print test.names, test.adresses
    print test.cant_find, test.found_cord
    print test.comined_cord
    '''
    
    test = locator()
    test.run_locator(test.excel_file)
    print test.names, test.adresses
    print test.cant_find, test.found_cord
    #print test.comined_cord
    


