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
import xlrd
import requests
import copy
import os
import time

DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(DIR, 'html_lib')
try:
    os.makedirs(DEST_DIR)              #write the html file from asset request here
except OSError:
    pass # already exists

class locator():
    def __init__(self, excel_path, excel_rows, update_log=None):
        self.excel_file = excel_path
        self.rows = excel_rows
        self.log = update_log           #get coordinates updater to let you know its running
        self.names = []
        self.adresses = []
        self.cant_find = []
        self.found_cord = []
        self.comined_cord = []
        self.employees = []

    def run_locator(self, excel_path):
        self.excel_file = excel_path
        #list of names and adresses in excel cells rows 1, 3
        self.names, self.adresses = self.get_names_addresses(self.excel_file)
        #find the coordinates(list of names, location, id, names) of adresses
        self.cant_find, self.found_cord = self.get_coordinates(copy.deepcopy(self.names), copy.deepcopy(self.adresses))
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
                if curr_cell == self.rows[0][0] and curr_row != 0:#remove header
                    val = worksheet.cell_value(curr_row, curr_cell)
                    #split last name first name
                    s=val.split(',')
                    #remove white space from split and reorder first last for consistentcy
                    s = [str(s[1]).replace(" ", ""), str(s[0])]
                    #join first_last
                    s = "_".join(s)
                    #replace white spaces if middle name first_m_last
                    s= s.replace (" ", "_")
                    names.append(s)
                elif curr_cell == self.rows[1][0] and curr_row != 0:
                    adresses.append(worksheet.cell_value(curr_row, curr_cell))
                    
        #every name should have a corespoding adress
        assert len(names)==len(adresses)
        #remove repeated names
        old_name = None
        f_names=[]
        f_adresses=[]
        for n,a in zip(names, adresses):
            if n == old_name:
                continue
            e = employee(name=n, address=a, date=(time.strftime("%d/%m/%Y")))
            f_names.append(n)
            f_adresses.append(a)
            old_name = n
            self.employees.append(e)
            
        
        return f_names, f_adresses
    
    def get_coordinates(self, names, adresses):  
        # recieves a list of names and adresses both list should be same length and 
        # name position should match adress position
        # searches geocoder for matching adress returns a list of lists formated(name, lat, long, position, name
        # returns the names and adresses of poitions it could not find  
        assert len(names) == len(adresses) == len(self.employees), "error in get_coordinates data length"            
        cord_dict={}
        locator_info = []
        count = 1
        errors = []
        s=""
        for n, a, e in zip(names, adresses,self.employees):
            cord_dict[n]=a
            #a = a.replace(",", " ")
            try:
                results = Geocoder.geocode(a)
                e.coord =  [results[0].coordinates[0], results[0].coordinates[1]]
                e.verified = False
                locator_info.append([n, results[0].coordinates[0], results[0].coordinates[1] ,count, n])
                s=("found "+n+" loc "+a+" @cord"+str(results[0].coordinates))
                count +=1
            except Exception as EE:
                errors.append((n,a))
                s = s=("found "+n+" loc "+a+" G_error "+ str(EE))
            self.display_data(s)
        
        return errors, locator_info

class asset_locator(locator):     
    def get_names_addresses(self, excel_path):
        #opens an excel file and returns coumn1 last,2first 7,8,9 zone street building
        #removes repeat names if there are any
        workbook = xlrd.open_workbook(excel_path)

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
                if curr_cell == self.rows[0][0] and curr_row != 0:#remove  header
                    #remove repeats these are family members
                    lnames.append(worksheet.cell_value(curr_row, curr_cell).replace (" ", "_"))
                elif curr_cell == self.rows[1][0]  and curr_row != 0:
                    fnames.append(worksheet.cell_value(curr_row, curr_cell).replace (" ", "_"))               
                elif curr_cell == self.rows[2][0] and curr_row != 0:
                    zone.append(worksheet.cell_value(curr_row, curr_cell))
                elif curr_cell == self.rows[3][0] and curr_row != 0:
                    street.append(worksheet.cell_value(curr_row, curr_cell))
                elif curr_cell == self.rows[4][0] and curr_row != 0:
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
            e = employee(name=n, assets=a, date=(time.strftime("%d/%m/%Y")))
            self.employees.append(e)
        return f_names, f_adresses
        
    def get_coordinates(self, names, adresses):  
        # recieves a list of names and adresses both list should be same length and 
        # name position should match adress position
        # searches geocoder for matching adress returns a list of lists formated(name, lat, long, position, name
        # returns the names and adresses of poitions it could not find  
        assert len(names) == len(adresses) == len(self.employees), 'error reading excel file: len of data does not match len names'
        count = 1
        errors = []
        s=""           
        locator_info =[]
        for n, l, e in zip(names, adresses, self.employees):#remove the header
            try:
                r = requests.get("http://myqplace.info/", 
                        params= {'b': str(int(l[2])), 's': str(int(l[1])), 'z':str(int(l[0]))})
                fl = ''.join(r).splitlines()
                rec = strip_cord(fl)

                locator_info.append([n, float(rec[0][1]), float(rec[1][1]) ,count, n])
                e.coord = (float(rec[0][1]), float(rec[1][1]))
                e.verified = True
                count +=1
                s=("found "+n+" @cord " +str(rec))
            except Exception as EE:
                errors.append((n))
                s=("found "+n+" error "+ str(EE))             
            self.display_data(s)
        return errors, locator_info
    
class student_locator(locator):  
    def __init__(self, *args, **kwargs):
        locator.__init__(self, *args, **kwargs)
        self.students = []
        
    def get_names_addresses(self, excel_path):
        #opens an excel file and returns coumn1 and column 3 of all rows on page1
        #removes repeated names
        workbook = xlrd.open_workbook(excel_path)
        worksheet = workbook.sheet_by_name(workbook.sheet_names()[0])
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = -1
        #id num    last name    first name    mobile phone    email address    current class cde    cur stud div    birth date    citizen    residence    legal addr line 1    legal addr line 2    legal country

        l_names = []
        f_names = []
        addr1 = []
        addr2=[]
        lcountry=[]
        #@todo improve this needs a generator
        while curr_row < num_rows:
            curr_row += 1
            curr_cell = -1
            while curr_cell < num_cells:
                curr_cell += 1
                if curr_cell == self.rows[0][0] and curr_row != 0:#remove  header
                    #remove repeats these are family members
                    l_names.append(worksheet.cell_value(curr_row, curr_cell).replace (" ", "_"))
                elif curr_cell == self.rows[1][0]  and curr_row != 0:
                    f_names.append(worksheet.cell_value(curr_row, curr_cell).replace (" ", "_"))               
                elif curr_cell == self.rows[2][0] and curr_row != 0:
                    addr1.append(worksheet.cell_value(curr_row, curr_cell))
                elif curr_cell == self.rows[3][0] and curr_row != 0:
                    addr2.append(worksheet.cell_value(curr_row, curr_cell))
                elif curr_cell == self.rows[4][0] and curr_row != 0:
                    lcountry.append(worksheet.cell_value(curr_row, curr_cell))
                    
        #every name should have a corespoding adress
        assert len(f_names)==len(l_names)
        names = [str(f+" "+l) for f, l in zip(f_names, l_names)]
        assert len(addr1)== len(addr2) ==len(lcountry)
        adresses = [ str(a1+", "+a2+", "+c) for a1, a2, c in zip(addr1, addr2, lcountry)]
        assert len(names)==len(adresses)
        #remove repeated names
        old_name = None
        f_names=[]
        f_adresses=[]
        for n,a in zip(names, adresses):
            if n == old_name:
                continue
            e = student(name=n, address=a, date=(time.strftime("%d/%m/%Y")))
            f_names.append(n)
            f_adresses.append(a)
            old_name = n
            self.students.append(e)
            
        return f_names, f_adresses
    
    def get_coordinates(self, names, adresses):  
        # recieves a list of names and adresses both list should be same length and 
        # name position should match adress position
        # searches geocoder for matching adress returns a list of lists formated(name, lat, long, position, name
        # returns the names and adresses of poitions it could not find  
        assert len(names) == len(adresses) == len(self.students), "error in get_coordinates data length"            
        cord_dict={}
        locator_info = []
        count = 1
        errors = []
        s=""
        for n, a, e in zip(names, adresses, self.students):
            cord_dict[n]=a
            #a = a.replace(",", " ")
            try:
                results = Geocoder.geocode(a)
                e.coord =  [results[0].coordinates[0], results[0].coordinates[1]]
                e.verified = False
                locator_info.append([n, results[0].coordinates[0], results[0].coordinates[1] ,count, n])
                s=("found "+n+" loc "+a+" @cord"+str(results[0].coordinates))
                count +=1
            except Exception as EE:
                errors.append((n,a))
                s = s=("found "+n+" loc "+a+" G_error "+ str(EE))
            self.display_data(s)
        
        return errors, locator_info
    
def read_file(f_loc, r_n=False):
    with open(str(f_loc), 'r') as f:
        if r_n:#remove newline
            lines = f.read().splitlines()
        else:#leave raw
            lines = f.readlines()
        return lines

def write_file(f_name, r):
    r.iter_content 
    chunk_size = 384
    with open(f_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)
    
def strip_cord(fl):
    coord = []
    for l in fl:
        if "Coordinates:" in l:
            l = l[l.index("Coordinates:")+12:l.index("</td></tr><tr><td></td><td>")]#E</td>")] 
            l = l.translate(None,'</td>')
            l = l.translate(None,'</tr>')
            l = l.translate(None,'<tr>')
            l = l.translate(None,'<td>')      
            l = l.split(',')
            for ll in l:
                ll = ll.strip()
                coord.append([ll[0], ll[1:]])
    return coord

class employee():
    unique_id = 0
    def __init__(self, name=None, coord=[None, None], 
                    address=None, assets=(None,None,None), date=None):
        self.name = name
        self.coord = coord
        self.address = address
        self.assets = assets
        self.date = date
        self.verified = None
        self.id= employee.unique_id
        employee.unique_id += 1
        
class student(employee):
    def __init__(self, *args, **kwargs):
        employee.__init__(self, *args, **kwargs)
        self.student = True

def asset_test():
    test = asset_locator(excel_path='./Copy of Residential Address Information (3).xls')
    test.run_locator(test.excel_file)
    print test.names, test.adresses
    print test.cant_find, test.found_cord
    for employee in test.employees:
        print employee.name, employee.id
        
def student_test():
    print "student test"
    test = student_locator(excel_path='./students.xlsx')
    test.run_locator(test.excel_file)
    print test.names, test.adresses
    print test.cant_find, test.found_cord
    for employee in test.students:
        print employee.name, employee.id
        
def excel_test(f='./excel_adress_test.xlsx'):
    test = locator()
    test.run_locator(f)
    print test.names, test.adresses
    print test.cant_find, test.found_cord
    
if __name__=="__main__":
    excel_rows = {'SAP':[0,3], 'new':[0,1,6,7,8], 'students':[1,2,10,11,12]}
    student_test()
    
    
    


