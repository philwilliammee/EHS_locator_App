#!/usr/bin/env python2.7
# -*- coding: CP1252 -*-

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
import wxversion
wxversion.select('3.0')

from wx.lib.floatcanvas import NavCanvas, FloatCanvas
import wx
print wx.VERSION_STRING
import gettext
import sys
sys.path.append("ehs_lib")
from geo_locator import locator, asset_locator
import geo_locator as geo 
from project import project, ard_map
import thread
import string

VERSION = "EHS locator"
ImageFile = "./ehs_lib/Doha.jpg"
GreenMarker = "./ehs_lib/green_marker.png"
RedMarker = "./ehs_lib/red_marker.png"
BlueMarker = "./ehs_lib/blue_marker.png"
CL = "./ehs_lib/Copyleft.png"
MARKER_SIZE = 220

class NavPanel(NavCanvas.NavCanvas):
    #explicitly show NavCanvas is a wx.Panel
    def __init__(self, parent):
        NavCanvas.NavCanvas.__init__(self, parent, ProjectionFun = None,
                                     BackgroundColor='#E0E0E0')
        self.parent_frame = parent
        self.MaxScale=5
        #do layout here
        #bind events here>> FloatCanvas.EVT_MOTION(self.Canvas, self.OnMove )
        #self.Canvas is the inherent Canvas object
        
class bit_marker(FloatCanvas.ScaledBitmap2):
    # a class to store marker info, uses same format as goggle but color is color not bitmap
    # gmap markers format [name, ['coord'][0], ['coord'][1], ['id'], names, 'COLOR'])
    global MARKER_SIZE
    def __init__(self, comb_ID, X, Y, ID, names, color, Height=None, Width=None, Position=None):
        self.green_marker = wx.Bitmap(GreenMarker)
        self.red_marker = wx.Bitmap(RedMarker)
        self.blue_marker = wx.Bitmap(BlueMarker)
        self.names = names
        self.XY = (X,Y)
        self.map_cord = self.get_map_coord()
        if self.map_cord[0] == None or  self.map_cord[1] ==None:
            self.obj = None
        else:
            #add a bitmap to the canvas
            FloatCanvas.ScaledBitmap2.__init__(self, Bitmap=self.set_bitmap(color), 
                        XY=self.map_cord , Height=MARKER_SIZE, Position='tl',)
            self.obj = True
        self.id = comb_ID
        
    def set_bitmap(self, color):
        # selects the bit map style
        #receives wx.COLOR returns wx.Bitmap
        if color=='BLUE': bitmap = self.blue_marker
        elif color == 'RED': bitmap = self.red_marker
        elif color == 'GREEN': bitmap = self.green_marker
        else: raise Exception("color is not supported "+str(color))
        return bitmap  
    
    def get_map_coord(self):
        ox,oy = -130, 80 #offset -110, 110
        if self.XY[0]!= None and self.XY[1]!=None:
            x, y = get_img_loc(float(self.XY[0]), float(self.XY[1]))
            if x == None or y==None: self.map_cord = x,y
            else: self.map_cord = [x+ox, -y+oy]     #map uses 'tl' not 'tr' so negate y
            return self.map_cord
        else:
            return None, None
    
    def set_XY(self, coord=(0,0)):
        self.XY = coord
          
class DrawFrame(wx.Frame):
    ID_IMPORT_XLS=wx.NewId()
    ID_IMPORT_ASSET_XLS = wx.NewId()
    ID_IMPORT_STUDENTS = wx.NewId()
    ID_EXPORT=wx.NewId()
    ID_OPEN=wx.NewId()
    ID_SAVE=wx.NewId()
    ID_SAVE_AS=wx.NewId()
    ID_EXIT=wx.NewId()
    ID_ABOUT=wx.NewId()
    ID_ENABLE_GMAP = wx.NewId()
    ID_NEW = wx.NewId()
    ID_EXPORT_IMG = wx.NewId()
    ID_SHOW_EMPLOYEES = wx.NewId()
    ID_EDIT_EXCEL_SAP = wx.NewId()
    ID_EDIT_EXCEL_NEW = wx.NewId()
    ID_EDIT_EXCEL_STUDENTS = wx.NewId()
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        '''--------------------- S T A R T   O F   I N I T -------------------------------'''
        self.orig_bitmap = wx.Bitmap(ImageFile)
        self.cl = wx.Bitmap(CL)
        self.red_marker = wx.Bitmap(RedMarker)
        #-------- Start Build Menu Bar --------------------------------
        #self.SetBackgroundColour('#E0E0E0')
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.frame_1_menubar.Append(wxglade_tmp_menu, ("File"))
        wxglade_tmp_menu.Append(self.ID_NEW, "&New")
        wxglade_tmp_menu.Append(self.ID_OPEN, "&Open") 
        wxglade_tmp_menu.Append(self.ID_SAVE,"&Save")
        wxglade_tmp_menu.Append(self.ID_SAVE_AS,"Save as") 
        wxglade_tmp_menu.AppendSeparator()
        imp = wx.Menu()
        imp.Append(self.ID_IMPORT_XLS, "SAP_HR.xls")
        imp.Append(self.ID_IMPORT_ASSET_XLS, "New_Adress_Plaque.xls")
        imp.Append(self.ID_IMPORT_STUDENTS, "Student_Adress.xls")
        wxglade_tmp_menu.AppendMenu(wx.ID_ANY, 'I&mport', imp)      
        exp = wx.Menu()
        exp.Append(self.ID_EXPORT_IMG, "Map_JPEG")
        wxglade_tmp_menu.AppendMenu(wx.ID_ANY, 'E&xport', exp)
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(self.ID_EXIT, "Exit")    
        wxglade_tmp_menu = wx.Menu()
        self.frame_1_menubar.Append(wxglade_tmp_menu, ("Settings"))
        self.enable_gmap = wxglade_tmp_menu.Append(self.ID_ENABLE_GMAP, 
                                        "Show_map")
        self.show_employees = wxglade_tmp_menu.Append(self.ID_SHOW_EMPLOYEES, 
                                "Show_Employees", kind=wx.ITEM_CHECK)
        
        self.edit_excel_sap = wxglade_tmp_menu.Append(self.ID_EDIT_EXCEL_SAP, 
                                "Edit_Excel_SAP")
        self.edit_excel_new = wxglade_tmp_menu.Append(self.ID_EDIT_EXCEL_NEW, 
                                "Edit_Excel_new")
        self.edit_excel_student = wxglade_tmp_menu.Append(self.ID_EDIT_EXCEL_STUDENTS, 
                                "Edit_Excel_student")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(self.ID_ABOUT,"About")
        self.frame_1_menubar.Append(wxglade_tmp_menu, ("Help"))
        wx.EVT_MENU(self, self.ID_NEW, self.new_project_handler)
        wx.EVT_MENU(self, self.ID_OPEN, self.open_project_handler)
        wx.EVT_MENU(self, self.ID_SHOW_EMPLOYEES, self.show_employees_handler)
        wx.EVT_MENU(self, self.ID_ENABLE_GMAP, self.enable_gmap_handler)
        wx.EVT_MENU(self, self.ID_EDIT_EXCEL_SAP, self.excel_sap_row_handler)
        wx.EVT_MENU(self, self.ID_EDIT_EXCEL_NEW, self.excel_new_row_handler)
        wx.EVT_MENU(self, self.ID_EDIT_EXCEL_STUDENTS, self.excel_students_row_handler)
        
        wx.EVT_MENU(self, self.ID_SAVE, self.save_project_handler)
        wx.EVT_MENU(self, self.ID_SAVE_AS, self.project_save_as_handler)
        wx.EVT_MENU(self, self.ID_IMPORT_XLS, self.import_file_handler) 
        wx.EVT_MENU(self, self.ID_IMPORT_ASSET_XLS, self.import_asset_file_handler) 
        wx.EVT_MENU(self, self.ID_IMPORT_STUDENTS, self.import_student_handler)
        wx.EVT_MENU(self, self.ID_ABOUT, self.about_event) 
        wx.EVT_MENU(self, self.ID_EXPORT_IMG, self.export_img_event) 
        wx.EVT_MENU(self, self.ID_EXIT, sys.exit)
        self.SetMenuBar(self.frame_1_menubar) 
        #-------------End of Build Menu Bar -----------------------------------     
        self.sb = self.CreateStatusBar()
        
        #-------------- start build display -------------------------------------
        self.panel_1 = NavPanel(self)
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        self.Canvas = self.panel_1.Canvas

        self.org_img_size  = (self.orig_bitmap.GetWidth(),self.orig_bitmap.GetHeight())
        assert (self.org_img_size[0]+self.org_img_size[1] > 500),(
                        "Failed to load doha image, is it at "+str(ImageFile))
        
        self.img = FloatCanvas.ScaledBitmap2(self.orig_bitmap, (0,0),
                Height=self.orig_bitmap.GetHeight(), Position = 'tl',)
        
        self.Canvas.AddObject(self.img)

        #build the other panel that contains the employee table
        #self.list_box_1 = wx.ListBox(self.panel_2, wx.ID_ANY, choices=[], style=wx.LC_REPORT)
        self.list_box_1 = wx.ListCtrl(self.panel_2, style=wx.LC_REPORT | wx.LC_NO_HEADER)
        self.list_box_1.InsertColumn(0, "employee")
        
        self.sizer_2_staticbox = wx.StaticBox(self.panel_2, wx.ID_ANY, _("employees"))
    
        self.__set_properties()
        self.__do_layout()
        self.init_variables()
        
        #Bind Events
        #self.Bind(wx.EVT_LISTBOX_DCLICK, self.box_dclick_event, self.list_box_1)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.box_dclick_event, self.list_box_1)
        FloatCanvas.EVT_MOTION(self.Canvas, self.OnMove )
        
        # final layout canvas
        self.Canvas.ZoomToBB()
        self.Canvas.Zoom(1.3)
        #self.canvas.Draw()
        '''--------------------- E N D   O F   __I N I T__   --------------------------------'''

    def __set_properties(self):
        self.sb.SetStatusWidths([-1])
        sb_field = ("Hello EHS....Lets find some location>>Coordinates")
        self.sb.SetStatusText(sb_field)
        self.display_obj=[]
        font = wx.Font(32, wx.MODERN, wx.NORMAL, wx.BOLD)

        self.display_obj.append(self.Canvas.AddScaledText("please create or load a new project", 
                            (120,-(self.org_img_size[0]/2)-50), Size=120, Position = 'tl', 
                            Font=font, Color=wx.BLUE))
               
        self.x_img, self.y_img = wx.GetDisplaySize()       
        res, __ = scale_bitmap(self.orig_bitmap, self.x_img, self.y_img)
        self.SetSize((res[0]+50,res[1]-40))
        self.panel_2.Hide()

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_2_staticbox.Lower()
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_1.Add(self.panel_1, 4, wx.EXPAND, 0)
        sizer_2.Add(self.list_box_1, 1, wx.ALL | wx.EXPAND|wx.GROW, 0)
        self.panel_2.SetSizer(sizer_2)
        sizer_1.Add(self.panel_2, 1, wx.ALL|wx.EXPAND|wx.GROW, 0)
        self.SetSizer(sizer_1)
        #sizer_1.Fit(self)
        self.Layout()

    def init_variables(self):
        self.orig_image = wx.Image(ImageFile)
        
        self.width, self.height = self.orig_bitmap.GetSize()
        self.filename = ""              #name of the current file being edoted
        self.dirname = ""               #directy that the file is saved in
        #move this to project
        self.project = project()
        self.project.html_name = "ehs_lib/EHS_locator_test.html"
        self.tx = 0
        self.ty = 0
        self.last_tx = 0
        self.last_ty = 0
        self.text_box = []
    '''--------------------- E N D   O F   I N I T    F U N C ---------------------------'''

        
    #---------------EVENT HANDLERS----------------------------
    #@todo add a test to see if the marker is off the display screen this is causing errors
    #@todo from the self.GUIMode.OnWheel(event) if the objects are deleted they have no size
    #@todo if not need to bind scroll wheel event that removes markers if they are deleted
    #assert objects are on view display
    # from the docs>> Zooming: I have set no zoom limits. What this means is that if you 
    # zoom in really far, you can get integer overflows, and get wierd results. It doesn't 
    # seem to actually cause any problems other than wierd output, at least when I have run it.
    def OnMove(self, event):
        #self.log("%i, %i"%tuple(event.Coords))
        event.Skip()
        
    def l_clicked(self, obj):
        len_line = 3
        font = wx.Font(20, wx.MODERN, wx.ITALIC, wx.BOLD)
        names=[]
        s = obj.names.split(':')
        for i , ss in enumerate(s):
            if i%len_line == 0:
                ss = ss.replace(" ", "\n")
            names.append(ss)
        names =  ": ".join(names)
        self.text_box.append(self.Canvas.AddScaledTextBox(names, 
                (obj.XY), Size=50,  BackgroundColor=wx.WHITE,
                PadSize = 50, Position = 'tl', Font=font, Color=wx.BLACK))
        self.Canvas.Zoom(1)
          
    def MouseOver(self, obj):
        font = wx.Font(20, wx.MODERN, wx.ITALIC, wx.BOLD)
        self.text_box.append(self.Canvas.AddScaledTextBox(str(obj.id), 
                (obj.XY), Size=50,  BackgroundColor=wx.WHITE,
                PadSize = 50, Position = 'tl', Font=font, Color=wx.BLACK))
        self.Canvas.Zoom(1)
        
    def MouseLeave(self, obj):
        if self.text_box:
            self.Canvas.RemoveObjects(self.text_box)
            self.text_box[:]=[]
        self.Canvas.Zoom(1)
        
    def show_employees_handler(self, event):
        if self.show_employees.IsChecked():
            self.panel_2.Show(True)
        else:
            self.panel_2.Hide()
        self.Canvas.ZoomToBB()
        self.Layout()
        event.Skip()
        
    def box_dclick_event(self, event):
        name = event.GetText()
        emp = self.project.employees[name]
        # Creates a new project
        dlg = my_dialog(self, -1, "Create New EHS_locator Project", 
                        [name, emp])
        if dlg.ShowModal() == wx.ID_OK:
            emp['name'] = dlg.panel_2.text_ctrl_1.GetValue() 

            emp["date"]= dlg.panel_2.text_ctrl_5.GetValue()
            
            try:
                emp["coord"]= eval(dlg.panel_2.text_ctrl_2.GetValue())
                
            except Exception as e:
                print ("evaluate error coord, assets not accepted "+str(e))
                
            try:
                emp["assets"]=[int(dlg.panel_2.text_ctrl_6_1.GetValue()),
                            int(dlg.panel_2.text_ctrl_6_1.GetValue()),
                            int(dlg.panel_2.text_ctrl_6_1.GetValue())]
            except Exception as e:
                print ("evaluate error coord, assets not accepted "+str(e))

            emp["address"]=dlg.panel_2.text_ctrl_3.GetValue()
            
            emp["id"]= int(dlg.panel_2.text_ctrl_7.GetValue())
            
            emp["verified"]= dlg.panel_2.checkbox_1.IsChecked() 
            self.log("updated emp: "+str(emp))
            self.__update_listbox()
            self.redraw_map(self.project.get_update_marker())   
        dlg.Destroy()
        event.Skip()
        
    def excel_sap_row_handler(self, event):
        vals = self.project.excel_rows['SAP']
        dlg = excel_editor_dialog (self, -1, "Excel_SAP_row_editor", 
                        [vals])
        if dlg.ShowModal() == wx.ID_OK:
            self.project.excel_rows['SAP'] = dlg.panel_2.get_vals()

            self.log("updated excel SAP rows: "+str(vals))
            self.__update_listbox()
            self.redraw_map(self.project.get_update_marker())   
        dlg.Destroy()
        event.Skip()
        
    def excel_new_row_handler(self, event):
        vals = self.project.excel_rows['new']
        # Creates a new project
        dlg = excel_editor_dialog (self, -1, "Excel_new_row_editor", 
                        [vals])
        if dlg.ShowModal() == wx.ID_OK:
            ret = dlg.panel_2.get_vals()
            self.project.excel_rows['new'] = ret
            self.__update_listbox()
            self.redraw_map(self.project.get_update_marker()) 
            self.log("updated excel new rows: "+str(ret))
        dlg.Destroy()
        event.Skip()
        
    def excel_students_row_handler(self, event):
        vals = self.project.excel_rows['students']
        # Creates a new project
        dlg = excel_editor_dialog (self, -1, "Excel_students_row_editor", 
                        [vals])
        if dlg.ShowModal() == wx.ID_OK:
            ret = dlg.panel_2.get_vals()
            self.project.excel_rows['students'] = ret

            self.log("updated excel students rows: "+str(vals))
            self.__update_listbox()
            self.redraw_map(self.project.get_update_marker())   
        dlg.Destroy()
        event.Skip()


    def export_img_event(self, event):
        #saves a JPEG image of the canvas and adds a marker bitmap at a list of coordinates
        if self.project.proj_name != '':
            dlg = wx.FileDialog(self, "Choose a file", self.dirname,
                                '', "*.jpg",wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                if filename[-4:] != ".jpg":
                    filename = filename + ".jpg"
                self.log("saving file "+str(filename ))
                if self.project.proj_name!= "" and len(self.project.get_update_marker())>0:
                    text_loc = self.project.get_update_marker()

                img = self.orig_bitmap
                ox,oy = -75, -20 #offset -55, -55
                xs , ys, markers = [],[],[]
                if text_loc and len(text_loc)>1:
                    __, marker = scale_bitmap(self.red_marker, MARKER_SIZE, MARKER_SIZE)
                    for loc in (text_loc):
                        if loc[1]!=None and loc[2]!=None:
                            x, y = get_img_loc(float(loc[1]), float(loc[2]))
                            if x!=None and y!=None:
                                markers.append(marker)
                                xs.append(x+ox)
                                ys.append(y+oy)
                            
                    markers.append(self.cl)      
                    xs.append(4000)
                    ys.append(4000)
                    print xs,
                    print ys
                    img = paste_bitmaps(img, markers, xs,ys)
                else: img = self.orig_bitmap
                img.SaveFile(filename, wx.BITMAP_TYPE_JPEG)
                self.orig_image = wx.Bitmap(ImageFile)
                #self.Canvas.SaveAsImage(filename, ImageType=wx.BITMAP_TYPE_JPEG)
                
            dlg.Destroy()
        else: self.log("Please Create a New Project")

    def new_project_handler(self, event):
        # Creates a new project
        dlg = new_project_dialog(self, -1, "Create New EHS_locator Project")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name.GetValue()
            if name and len(name) > 0:
                del(self.project)
                self.project = project()
                self.project.proj_name = name
                self.project.html_name = name+".html"
                self.log('created new project ' + self.project.proj_name + 
                         ', please import data.xls')
                self.SetTitle(VERSION+" - " + self.project.proj_name)
                self.project.save = True
                self.filename = ""
            else: self.log("error in project name please select a new project name")
            self.redraw_map([])
        dlg.Destroy()
    
    def __update_listbox(self): 
        #accesses proj.employees and modifies listbox
        #this method is slow but needed to set individual colors
        for i, name in enumerate(self.project.employees.keys()):
                self.list_box_1.DeleteItem(i)
                self.list_box_1.InsertStringItem(i,name)
                if self.project.employees[name]["verified"]==False:
                    self.list_box_1.SetItemTextColour(i, wx.RED)
                elif self.project.employees[name]["verified"]==True:
                    self.list_box_1.SetItemTextColour(i, wx.BLUE)
                elif self.project.employees[name]["verified"]==None:
                    self.list_box_1.SetItemTextColour(i, wx.GREEN)
                else: raise Exception("invalid data entered for update_listbox, emp verified")
        self.list_box_1.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                        
    def open_project_handler(self, event):
        #Loads a  project into the GUI. """ 
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, 
                            "", "*.ehs", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.dirname = dlg.GetDirectory()
            self.log("Opening: " + self.filename)   
            #load the project data        
            self.project = self.project.load_project(self.filename)  
            
            if self.project == None:#this should never happen assert
                del self.project
                self.project = project()
                self.log('load error reseting project')
            else:
                self.__update_listbox()
                self.redraw_map(self.project.get_update_marker())  
                
            self.SetTitle(VERSION+" - " + self.project.proj_name)
            dlg.Destroy()
            self.log('opened ' + self.filename)
        
    def enable_gmap_handler(self, event):
        if self.project.proj_name != "":
            self.project.open_gmap(self.project.html_name)
        else:
            self.log("please create or open a project")
            
    def save_project_handler(self, event=None):
        """ Save a file from the GUI. """
        if self.project.proj_name != '':
            #if self.project.proj_name == "": 
            dlg = wx.FileDialog(self, "Choose a file", self.dirname,
                                '', "*.ehs",wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetPath()
                self.dirname = dlg.GetDirectory()
                dlg.Destroy()
                if self.filename[-4:] != ".ehs":
                    self.filename = self.filename + ".ehs"
                self.log("saving file "+str(self.filename ))
                self.project.path = self.filename[:-4]
                self.project.save_project(self.filename)
            else:
                return  
        else: self.log("please create or open a project")
        
    def project_save_as_handler(self, event):
        self.filename = ""
        self.save_project_handler()  

    def import_file_handler(self, event):
        #@todo need a check to verify proper format of adresses or 
        # else bad stuff or wrong rows can be used
        if self.project.proj_name != "":
            dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", 
                                "Excel (*.xls; *.xlsx)|*.xls;*.xlsx|" \
                                "All files (*.*)|*.*", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetPath()
                self.log('opened ' + self.filename)
                self.dirname = dlg.GetDirectory()    
                dlg.Destroy()
                thread.start_new_thread(self.import_address_data_thread, 
                                        (self.filename, self.log))    
        else: self.log("please create or open a project, first!")
        
    def import_address_data_thread(self, excel_path, display):
        #this is not an event it is a thread
        my_locator = geo.locator(excel_path, self.project.excel_rows['SAP'], display)
        my_locator.run_locator(excel_path=excel_path)
        #save the data to the project
        self.project.lost_data = my_locator.cant_find
        self.project.set_employees(my_locator.employees)
        marker_loc = self.project.get_update_marker()
        self.project.build_open_html(False)
        wx.CallAfter(self.__update_listbox,)
        wx.CallAfter(self.redraw_map, self.project.marker_loc)
        return marker_loc
            
    def import_asset_file_handler(self, event):
        #@todo need a check to verify proper format of adresses or else wrong rows can be used
        if self.project.proj_name != '':
            dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", 
                                "Excel (*.xls; *.xlsx)|*.xls;*.xlsx|" \
                                "All files (*.*)|*.*", wx.OPEN)
            
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetPath()
                self.log('opened ' + self.filename)
                self.dirname = dlg.GetDirectory()    
                dlg.Destroy()   
                thread.start_new_thread(self.import_asset_data_thread, 
                                        (self.filename, self.log))  
        else: self.log("please create or open a project, first!")
        
    def import_student_handler(self, event):
        #@todo need a check to verify proper format of adresses or else wrong rows can be used
        if self.project.proj_name != '':
            dlg = wx.FileDialog(self, "Choose a file", self.dirname, "",
                                "Excel (*.xls; *.xlsx)|*.xls;*.xlsx|" \
                                "All files (*.*)|*.*", wx.OPEN)
            
            if dlg.ShowModal() == wx.ID_OK:
                self.filename = dlg.GetPath()
                self.log('opened ' + self.filename)
                self.dirname = dlg.GetDirectory()    
                dlg.Destroy()   
                thread.start_new_thread(self.import_student_data_thread, 
                                        (self.filename, self.log))  
        else: self.log("please create or open a project, first!")
        
    def import_student_data_thread(self, excel_path, display):
        #save the data to the project
        my_locator = geo.student_locator(excel_path, self.project.excel_rows['students'], display)
        my_locator.run_locator(excel_path=excel_path)
        self.project.lost_data = my_locator.cant_find
        self.project.set_employees(my_locator.students)
        
        marker_loc = self.project.get_update_marker()
        self.project.build_open_html(False)
        wx.CallAfter(self.__update_listbox, )
        wx.CallAfter(self.redraw_map, self.project.marker_loc)
        return marker_loc   
        
    def import_asset_data_thread(self, excel_path, display):
        #save the data to the project
        my_locator = geo.asset_locator(excel_path, self.project.excel_rows['new'], display)
        my_locator.run_locator(excel_path=excel_path)
        self.project.lost_data = my_locator.cant_find
        self.project.set_employees(my_locator.employees)
        
        marker_loc = self.project.get_update_marker()
        self.project.build_open_html(False)
        wx.CallAfter(self.__update_listbox,)
        wx.CallAfter(self.redraw_map, self.project.marker_loc)
        return marker_loc
        
    def redraw_map(self, text_loc=[]):
        #recieves a list of coordinates and puts markers on the canvas
        
        #remove the objects from the canvas
        if self.display_obj:
            self.Canvas.RemoveObjects(self.display_obj)
        #delete all of the objects in the list so we can build new list
        self.display_obj[:]=[]   
        self.Canvas.ZoomToBB()
        for loc in text_loc:
            #color, ID, XY, names, Height=None, Width=None, Position=Non
            img = bit_marker(*loc)
            if img.obj == None:
                pass
            else:
                obj = self.Canvas.AddObject(img)
                obj.Bind(FloatCanvas.EVT_FC_ENTER_OBJECT, self.MouseOver)
                obj.Bind(FloatCanvas.EVT_FC_LEAVE_OBJECT, self.MouseLeave)
                obj.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.l_clicked)      
    
                self.display_obj.append(img)
            
        self.Canvas.Zoom(1)
        
    def log(self, s):
        self.sb.SetStatusText(s, 0)
            
    def about_event(self, event):
        PSW_license= """This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA)"""
        info = wx.AboutDialogInfo()
        info.SetName(VERSION)
        info.SetDescription("A geo locator that imports data from an excel spread sheet \n"
        "and plots the points on a map this software is provided \nfree as in beer and free"+
         "as in speech to all users.")
        info.SetCopyright("Copyright (c) 2015-2017 Philip Williammee.  All right reserved.")
        info.SetLicense(PSW_license)
        info.SetWebSite("https://github.com/philwilliammee/EHS_locator_App")
        wx.AboutBox(info)

        
class new_project_dialog(wx.Dialog):
    def __init__(self, parent, ids, title):
        wx.Dialog.__init__(self, parent, ids, title, size=(300, 100))  
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        wx.StaticText(panel, -1, 'Project Name:', (15,10))
        self.name  =  wx.TextCtrl(panel, -1, 'test', (105, 10))#
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, ' Ok ', size=(55, 30))
        closeButton = wx.Button(self, wx.ID_CANCEL, 'Close', size=(55, 30))
        hbox.Add(okButton, wx.ALL, 10)
        hbox.Add(closeButton, wx.ALL, 10)
        vbox.Add(panel)
        vbox.Add(hbox, -1, wx.ALL | wx.ALIGN_CENTER , 10)
        self.SetSizer(vbox)   
        #self.Fit()
        self.Layout()

class excel_editor_dialog(wx.Dialog):
    def __init__(self, parent, ids, title, args):
        wx.Dialog.__init__(self, parent, ids, title)
        self.parent = parent
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_2 = excel_editor_panel(self.panel_1, wx.ID_ANY, args)
        self.sizer_6_staticbox = wx.StaticBox(self.panel_1,
                                wx.ID_ANY, _("Emplyee Editor Dialog"))
        self.button_5 = wx.Button(self.panel_1, wx.ID_OK, _("OK"))
        self.button_6 = wx.Button(self.panel_1,  wx.ID_CANCEL, _("Cancel"))
        self.SetTitle(title)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_6_staticbox.Lower()
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_6.Add(self.panel_2, 1, 0, 0)
        sizer_5.Add(sizer_6, 1, 0, 0)
        sizer_7.Add(self.button_5, 0, wx.ALL, 5)
        sizer_7.Add(self.button_6, 0, wx.ALL, 5)
        sizer_5.Add(sizer_7, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.panel_1.SetSizer(sizer_5)
        sizer_3.Add(self.panel_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()
        
class excel_editor_panel(wx.Panel):
    def __init__(self, parent, ids, args):
        wx.Panel.__init__(self, parent, ids, style=wx.TAB_TRAVERSAL)
        self.vals = args[0]
        num2alpha = dict(zip(range(0, 26), string.ascii_uppercase))
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.labels = []
        self.text_ctrl = []
        for val in self.vals:
            label = wx.StaticText(self, wx.ID_ANY, str(val[1]))
            text = wx.TextCtrl(self, wx.ID_ANY, str(num2alpha[val[0]]))
            self.labels.append(label)
            self.text_ctrl.append(text)
            sizer_1.Add(label, 0,wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
            sizer_1.Add(text, 0)
            
        self.SetSizerAndFit(sizer_1)
        sizer_1.Fit(self)
        
    def get_vals(self):
        a2n = dict(zip(string.ascii_uppercase, range(0, 26)))
        ret = []
        assert len(self.text_ctrl)==len(self.vals), "number of vals dont match number of text boxes"
        for val, name in zip(self.text_ctrl, self.vals):
            ret.append([int(a2n[val.GetValue().upper()]),name[1]] )
        return ret
        

class my_dialog(wx.Dialog):
    def __init__(self, parent, ids, title, args):
        wx.Dialog.__init__(self, parent, ids, title)
        self.parent = parent
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_2 = employee_dialog(self.panel_1, wx.ID_ANY, args)
        self.sizer_6_staticbox = wx.StaticBox(self.panel_1, wx.ID_ANY,
                                         _("Emplyee Editor Dialog"))
        self.button_5 = wx.Button(self.panel_1, wx.ID_OK, _("OK"))
        self.button_6 = wx.Button(self.panel_1,  wx.ID_CANCEL, _("Cancel"))
        self.SetTitle(title)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_6_staticbox.Lower()
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_6.Add(self.panel_2, 1, 0, 0)
        sizer_5.Add(sizer_6, 1, 0, 0)
        sizer_7.Add(self.button_5, 0, wx.ALL, 5)
        sizer_7.Add(self.button_6, 0, wx.ALL, 5)
        sizer_5.Add(sizer_7, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.panel_1.SetSizer(sizer_5)
        sizer_3.Add(self.panel_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()
        
class employee_dialog(wx.Panel):
    def __init__(self, parent, ids, args):
        wx.Panel.__init__(self, parent, ids, style=wx.TAB_TRAVERSAL)
        name = args[0]
        emp = args[1]
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _("Name:"))
        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, name)
        self.label_2 = wx.StaticText(self, wx.ID_ANY, _("Date:"))
        self.text_ctrl_5 = wx.TextCtrl(self, wx.ID_ANY, emp["date"])
        self.label_3 = wx.StaticText(self, wx.ID_ANY, _("Coord:"))
        self.text_ctrl_2 = wx.TextCtrl(self, wx.ID_ANY, str(emp["coord"]))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, _("Assets:"))
        #[z,s,b]
        ''''I will change the editor window that has plate locations in one display box, 
        to building, zone, and street displayed in three separate separate display boxes 
        example  Assets:[128, 30, 25]  -->  b: 128   z:30    s: 25'''
        self.label_4_1 = wx.StaticText(self, wx.ID_ANY, _("Z:"))
        self.label_4_2 = wx.StaticText(self, wx.ID_ANY, _("S:"))
        self.label_4_3 = wx.StaticText(self, wx.ID_ANY, _("B:"))
        self.text_ctrl_6_1 = wx.TextCtrl(self, wx.ID_ANY, str(emp["assets"][0]))
        self.text_ctrl_6_2 = wx.TextCtrl(self, wx.ID_ANY, str(emp["assets"][1]))
        self.text_ctrl_6_3 = wx.TextCtrl(self, wx.ID_ANY, str(emp["assets"][2]))
        
        self.label_6 = wx.StaticText(self, wx.ID_ANY, _("Adress:"))
        self.text_ctrl_7 = wx.TextCtrl(self, wx.ID_ANY, str(emp["address"]))
        self.label_5 = wx.StaticText(self, wx.ID_ANY, _("ID:"))
        self.text_ctrl_3 = wx.TextCtrl(self, wx.ID_ANY, str(emp["id"]))
        
        self.checkbox_1 = wx.CheckBox(self, wx.ID_ANY, _("verified"))
        if emp["verified"]==True:
            self.checkbox_1.SetValue(True)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        pass

    def __do_layout(self):
        # begin wxGlade: MyPanel.__do_layout
        grid_sizer_1 = wx.FlexGridSizer(6, 4, 3, 3)
        grid_sizer_1.Add(self.label_1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                         wx.ALIGN_RIGHT, 5)
        grid_sizer_1.Add(self.text_ctrl_1, 1, wx.ALL|wx.GROW|wx.EXPAND, 5)
        grid_sizer_1.Add(self.label_2, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                         wx.ALIGN_RIGHT, 5)
        grid_sizer_1.Add(self.text_ctrl_5, 1, wx.ALL|wx.GROW|wx.EXPAND, 5)
        grid_sizer_1.Add(self.label_3, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                         wx.ALIGN_RIGHT, 5)
        grid_sizer_1.Add(self.text_ctrl_2, 1, wx.ALL|wx.GROW|wx.EXPAND, 5)
        
        grid_sizer_1.Add(self.label_4, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                         wx.ALIGN_RIGHT, 5)
        
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_4_1, 0,wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_2.Add(self.text_ctrl_6_1, 0)
        sizer_2.Add(self.label_4_2, 0,wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_2.Add(self.text_ctrl_6_2, 0)
        sizer_2.Add(self.label_4_3, 0,wx.ALL| wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_2.Add(self.text_ctrl_6_3, 0)
        grid_sizer_1.Add(sizer_2, 1, wx.ALL|wx.GROW|wx.EXPAND, 5)
        
        grid_sizer_1.Add(self.label_5, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                         wx.ALIGN_RIGHT, 5)
        grid_sizer_1.Add(self.text_ctrl_3, 1, wx.ALL|wx.GROW|wx.EXPAND, 5)
        grid_sizer_1.Add(self.label_6, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                         wx.ALIGN_RIGHT, 5)
        grid_sizer_1.Add(self.text_ctrl_7, 1, wx.ALL|wx.GROW|wx.EXPAND, 5)
        grid_sizer_1.Add((20, 20), 0, 0, 0)
        grid_sizer_1.Add((200, 20), 1, 0, 0)
        grid_sizer_1.Add(self.checkbox_1, 0, 0, 0)
        grid_sizer_1.Add((200, 20), 1, 0, 0)
        self.SetSizerAndFit(grid_sizer_1)
        grid_sizer_1.Fit(self)
# end of class MyPanel

        
'''-------------------    S T A R T    F U N C T I O N S  ------------------------- '''      
        
def scale_bitmap(bitmap, width, height):
    #scales the bitmap to the proper aspect ratio
    # recieves a wx.bitmap and two sizes typ screen size
    # calculates aprop aspect ratio and 
    # returns the returns the scaled size and its scale multipler
    MaxImageSize = width if width < height else height
    image = wx.ImageFromBitmap(bitmap)
    W = image.GetWidth()*1.0
    H = image.GetHeight()*1.0
    if W > H:
        NewW = MaxImageSize
        NewH = MaxImageSize * H / W
    else:
        NewH = MaxImageSize
        NewW = MaxImageSize * W / H

    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(NewW , NewH, wx.IMAGE_QUALITY_HIGH)
    bitmap = wx.BitmapFromImage(image)
    
    result = NewW,NewH 
    #scale = NewW/W , NewH/H
    return result, bitmap

def __SetDcContext( memDC, font=None, color=None ):
    # helper function for writing text on bitmap
    if font:
        memDC.SetFont( font )
    else:
        memDC.SetFont( wx.NullFont )
    if color:
        memDC.SetTextForeground( color )
        
def WriteTextOnBitmap( text, bitmap, pos=(0, 0), font=None, color=None) :
    #Simple write into a bitmap doesn't do any checking.
    #returns the bitmap with the text drawn on it
    #wx.Font(pointSize, family, style, weight, underline=False, faceName="", 
    # encoding=wx.FONTENCODING_DEFAULT)
    memDC = wx.MemoryDC()
    __SetDcContext( memDC, font, color )
    memDC.SelectObject( bitmap )
    try:
        memDC.DrawText( text, pos[0], pos[1])
    except :
        pass

    memDC.SelectObject( wx.NullBitmap )
    return bitmap

def paste_bitmaps(i1, images, xs, ys):
    i3 = wx.EmptyBitmap(i1.Size.width, i1.Size.height)
    
    dc = wx.MemoryDC(i3)
    MASK = (0,0,1)  # just an unused color
    dc.SetBackground(wx.Brush(MASK))
    dc.Clear()
    dc.DrawBitmap(i1, 0, 0, True)
    for i2, x, y in zip(images, xs, ys):
        dc.DrawBitmap(i2, x, y, True)
    del dc
    i3.SetMaskColour(MASK)
    return i3

def get_img_loc(y, x):
    #recieves a latitude and longitude and converts it to a position on the image
    #original image size 4233, 4220
    #Lower Left lat long coord 
    #ylat = [25.369572, 25.206881]#bottom, top
    #xlon = [51.387591, 51.607245]#left right
    ylat = [25.3865, 25.213]#top, bottom  make top bigger moves it down
    xlon = [51.41, 51.607245]#left right make left bigger moves it left

    newx = ard_map(x, xlon[0],xlon[1], 0, 4233)
    newy = ard_map(y, ylat[0],ylat[1], 0, 4220)
    if newy > 4219.0 or newy < 1.0 or newx > 4232.0 or newx < 1.0: return None, None

    return newx, newy

# end of class MyFrame
if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name
    app = wx.App(False)
    frame_1 = DrawFrame(parent=None, id=wx.ID_ANY, title="EHS_Locator", pos=(0,0),
        size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name="PSW")# & ~(wx.RESIZE_BORDER | 
        #wx.MAXIMIZE_BOX), name="PSW" )
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    
