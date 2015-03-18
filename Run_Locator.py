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

from wx.lib.floatcanvas import NavCanvas, FloatCanvas
import wx
#print wx.VERSION_STRING
import gettext
import sys
sys.path.append("ehs_lib")
from geo import locator, asset_locator
from project import project

VERSION = "EHS locator"
ImageFile = "./ehs_lib/Doha.jpg"

class DrawFrame(wx.Frame):
    ID_IMPORT_XLS=wx.NewId()
    ID_IMPORT_ASSET_XLS = wx.NewId()
    ID_EXPORT=wx.NewId()
    ID_OPEN=wx.NewId()
    ID_SAVE=wx.NewId()
    ID_SAVE_AS=wx.NewId()
    ID_EXIT=wx.NewId()
    ID_ABOUT=wx.NewId()
    ID_ENABLE_GMAP = wx.NewId()
    ID_NEW = wx.NewId()
    ID_EXPORT_IMG = wx.NewId()
    
    """
    A frame used for the FloatCanvas
    
    """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        # Menu Bar
        #self.SetBackgroundColour('#E0E0E0')
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.frame_1_menubar.Append(wxglade_tmp_menu, ("File"))
        wxglade_tmp_menu.Append(self.ID_NEW, "&New")
        wxglade_tmp_menu.Append(self.ID_OPEN, "&Open") 
        wxglade_tmp_menu.Append(self.ID_SAVE,"&Save")
        wxglade_tmp_menu.Append(self.ID_SAVE_AS,"Save as") 
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(self.ID_IMPORT_XLS, "Import address.xls")
        wxglade_tmp_menu.Append(self.ID_IMPORT_ASSET_XLS, "Import asset_loc.xls")
        wxglade_tmp_menu.Append(self.ID_EXPORT_IMG, "Export_img")
        wxglade_tmp_menu.AppendSeparator()
        wxglade_tmp_menu.Append(self.ID_EXIT, "Exit")
        
        wxglade_tmp_menu = wx.Menu()
        self.frame_1_menubar.Append(wxglade_tmp_menu, ("Settings"))
        self.enable_gmap = wxglade_tmp_menu.Append(self.ID_ENABLE_GMAP, "Show_map", kind=wx.ITEM_CHECK)
        
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(self.ID_ABOUT,"About")
        self.frame_1_menubar.Append(wxglade_tmp_menu, ("Help"))
        
        wx.EVT_MENU(self, self.ID_NEW, self.new_project_handler)
        wx.EVT_MENU(self, self.ID_OPEN, self.open_project_handler)
        wx.EVT_MENU(self, self.ID_ENABLE_GMAP, self.enable_gmap_handler)
        wx.EVT_MENU(self, self.ID_SAVE, self.save_project_handler)
        wx.EVT_MENU(self, self.ID_SAVE_AS, self.project_save_as_handler)
        wx.EVT_MENU(self, self.ID_IMPORT_XLS, self.import_file_handler) 
        wx.EVT_MENU(self, self.ID_IMPORT_ASSET_XLS, self.import_asset_file_handler) 
        wx.EVT_MENU(self, self.ID_ABOUT, self.about_event) 
        wx.EVT_MENU(self, self.ID_EXPORT_IMG, self.export_img_event) 
        wx.EVT_MENU(self, self.ID_EXIT, sys.exit)

        self.SetMenuBar(self.frame_1_menubar)      
        self.sb = self.CreateStatusBar()
        
        
        
        
        # Add the Canvas
        Canvas = NavCanvas.NavCanvas(self, ProjectionFun=None,
        BackgroundColor='#E0E0E0' , Debug=False ).Canvas
        
        Canvas.MaxScale=20
        self.Canvas = Canvas
        
        FloatCanvas.EVT_MOTION(self.Canvas, self.OnMove )

        self.orig_image = wx.Bitmap(ImageFile)
        
        self.width, self.height = self.orig_image.GetSize()
        
        self.img = FloatCanvas.ScaledBitmap2( self.orig_image, (0,0),
                Height=self.orig_image.GetHeight(), Position = 'tl',)
        
        Canvas.AddObject(self.img)
        
        self.org_img_size  = (self.orig_image.GetWidth(),self.orig_image.GetHeight())
        assert (self.org_img_size[0]+self.org_img_size[1] > 500),("Failed to load doha image, is it at "+ImageFile)

        font = wx.Font(32, wx.MODERN, wx.NORMAL, wx.BOLD)
        #(self, String, xy, Size, Color, BackgroundColor, Family, Style, Weight, Underlined, Position, InForeground, Font)
        self.text=[]
        self.text.append(self.Canvas.AddScaledText("please create a new project or load a project", 
                            (120,-(self.org_img_size[0]/2)-50), Size=110, Position = 'tl', Font=font, Color=wx.BLUE))
        
        self.__set_properties()
        self.__do_layout()
        self.init_variables()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_propertie
        self.sb.SetStatusWidths([-1])
        # statusbar fields
        sb_fields = [_("Hello EHS")]
        for i in range(len(sb_fields)):
            self.sb.SetStatusText(sb_fields[i], i)
                
        self.x_img, self.y_img = wx.GetDisplaySize()       
        res, __ =scale_bitmap(self.orig_image, self.x_img, self.y_img)
        #print res
        self.SetSize((res[0],res[1]-40))
        self.Canvas.ZoomToBB()
        self.Canvas.Zoom(1.3)

    def __do_layout(self):
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(self.Canvas, 1, wx.EXPAND)
        #MainSizer.Add(self.MsgWindow, 1, wx.EXPAND | wx.ALL, 5)
        #MainSizer.Fit(self)
        #self.SetSizer(MainSizer)
        self.Layout()

        
    def OnMove(self, event):
        """
        Updates the status bar with the world coordinates
        
        """
        #self.SetStatusText("%i, %i"%tuple(event.Coords))
        pass
        
    def init_variables(self):
        self.filename = ""              #name of the current file being edoted
        self.dirname = ""               #directy that the file is saved in
        self.locator = locator(update_log=self.log)
        self.asset_locator = asset_locator(update_log=self.log)
        #move this to project
        self.project = project(self)
        self.project.html_name = "ehs_lib/EHS_locator_test.html"
        self.tx = 0
        self.ty = 0
        self.last_tx = 0
        self.last_ty = 0

        
    #---------------EVENT HANDLERS----------------------------
    def export_img_event(self, event):
        if self.project.name != '':
            """ Save a file from the GUI. """
            #if self.project.name == "": 
            dlg = wx.FileDialog(self, "Choose a file", self.dirname,
                                '', "*.jpg",wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                #self.dirname = dlg.GetDirectory()
                dlg.Destroy()
                if filename[-4:] != ".jpg":
                    filename = filename + ".jpg"
                self.log("saving file "+str(filename ))
    
                font = wx.Font(32, wx.MODERN, wx.NORMAL, wx.BOLD)#you can also set text
                if self.project.name!= "" and self.project.get_data():
                    text_loc = [(get_img_loc(float(loc[1]), float(loc[2]))) for loc in self.project.get_data()]
                if text_loc and len(text_loc)>1:
                    for i, loc in enumerate(text_loc):
                        if i >= len(self.project.saved_asset_data):
                            color = wx.RED
                        else:
                            color = wx.BLUE
                    
                        img = WriteTextOnBitmap(str(i), self.orig_image, 
                                pos=(loc[0],loc[1]),font=font, color=color)
                else: img = self.orig_image
                img.SaveFile(filename, wx.BITMAP_TYPE_JPEG)
            else:
                return 
        else: self.log("Please Create a New Project")

    def new_project_handler(self, event):
        #print "new file handler"
        dlg = new_project_dialog(self, -1, "Create New EHS_locator Project")
        if dlg.ShowModal() == wx.ID_OK:
            del(self.project)
            self.project = project(self)
            name = dlg.name.GetValue()
            if name and len(name) > 0:
                print "project name", name
                self.project.name = name
                self.project.html_name = name+".html"
                #print self.project.html_name
                self.log('created new project ' + self.project.name + ', please import data.xls')
                self.SetTitle(VERSION+" - " + self.project.name)
                self.project.save = True
                self.filename = ""
            else: self.log("error in project name please select a new project name")
            self.redraw_map([])
        dlg.Destroy()
        #@todo update map here
        
    def open_project_handler(self, event):
        """ Loads a  file into the GUI. """ 
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, 
                            "", "*.ehs", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.dirname = dlg.GetDirectory()
            self.log("Opening: " + self.filename)   
            #load the project data        
            load_error = self.project.load_project(self.filename)  
            
            if load_error:
                del self.project
                self.project = project(self)
                self.sb.SetStatusText('load error reseting project')
            else:
                text_loc = []
                for loc in self.project.get_data():
                    if len(loc) == 5:
                        #print loc
                        text_loc.append(get_img_loc((float(loc[1])), (float(loc[2]))))
                    else:
                        self.log( "data error "+str(loc))
                self.project.build_open_html(False)
                self.redraw_map(text_loc)  
            self.SetTitle(VERSION+" - " + self.project.name)
            dlg.Destroy()
            self.sb.SetStatusText('opened ' + self.filename)
        
    def enable_gmap_handler(self, event):
        if self.enable_gmap.IsChecked() and self.project.name != "":
            self.project.open_gmap(self.project.html_name)
            #uncheck it so every time you want to see a gmap you have to click the box
            self.enable_gmap.Check(False)
        else:
            self.log("please create or open a project")
            
    def save_project_handler(self, event=None):
        """ Save a file from the GUI. """
        if self.project.name != '':
            #if self.project.name == "": 
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
        if self.project.name != "":
            dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Excel (*.xls; *.xlsx)|*.xls;*.xlsx|" \
                                "All files (*.*)|*.*", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.log('opened ' + self.filename)
                self.filename = dlg.GetPath()
                self.dirname = dlg.GetDirectory()    
                dlg.Destroy()
                text_loc = self.project.import_address_data(excel_path=self.filename)    
    
                self.redraw_map(text_loc)
        else: self.log("please create or open a project, first!")
            
    def import_asset_file_handler(self, event):
        if self.project.name != '':
            dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Excel (*.xls; *.xlsx)|*.xls;*.xlsx|" \
                                "All files (*.*)|*.*", wx.OPEN)
            
            if dlg.ShowModal() == wx.ID_OK:
                self.log('opened ' + self.filename)
                self.filename = dlg.GetPath()
                self.dirname = dlg.GetDirectory()    
                dlg.Destroy()    
                text_loc = self.project.import_asset_data(excel_path=self.filename)
                '''
                text_loc = []
                #save the data to the project
                self.project.lost_asset, self.project.saved_asset_data = copy.deepcopy(self.asset_locator.cant_find), copy.deepcopy(self.asset_locator.found_cord)   
                
                for loc in self.project.get_data():#self.asset_locator.comined_cord:      
                    text_loc.append(get_img_loc(float(loc[1]), float(loc[2])))
                self.project.build_open_html(False)
                '''
                self.redraw_map(text_loc)
        else: self.log("please create or open a project, first!")
            
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
        info.SetDescription("A geo locator that imports data from an excel spread sheet \nand plots "+
         "the points on a map this software is provided \nfree as in beer and free as in speech to all users.")
        info.SetCopyright("Copyright (c) 2015-2017 Philip Williammee.  All right reserved.")
        info.SetLicense(PSW_license)
        info.SetWebSite("https://github.com/philwilliammee")
        wx.AboutBox(info)
            
    def log(self, s):
        self.sb.SetStatusText(s, 0)
        
    def redraw_map(self, text_loc=[]):

        if self.text:
            self.Canvas.RemoveObjects(self.text)
        self.text[:]=[]   
        font = wx.Font(16, wx.MODERN, wx.NORMAL, wx.BOLD)#you can also set text
        for i, loc in enumerate(text_loc):
            if i >= len(self.project.saved_asset_data):
                #(self, pointSize, family, style, weight, underline, face, encoding) 
                color = wx.RED
            else:
                color = wx.BLUE
            #print "adding text @", loc[0], loc[1]
            self.text.append(self.Canvas.AddText(str(i),(loc[0],-loc[1]), Size=110, Position = 'tl', Font=font, Color=color))
        self.Canvas.Zoom(1)
        
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
    result = NewW,NewH 
    scale = NewW/W , NewH/H
    return result, scale

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
    #wx.Font(pointSize, family, style, weight, underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT)
    memDC = wx.MemoryDC()
    __SetDcContext( memDC, font, color )
    memDC.SelectObject( bitmap )
    try:
        memDC.DrawText( text, pos[0], pos[1])
    except :
        pass

    memDC.SelectObject( wx.NullBitmap )
    return bitmap

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

# end of class MyFrame
if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name
    app = wx.App(False)
    #wx.InitAllImageHandlers()
    frame_1 = DrawFrame(parent=None, id=wx.ID_ANY, title="EHS_Locator", pos=(0,0),
        size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name="PSW")# & ~(wx.RESIZE_BORDER | 
        #wx.MAXIMIZE_BOX), name="PSW" )
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
