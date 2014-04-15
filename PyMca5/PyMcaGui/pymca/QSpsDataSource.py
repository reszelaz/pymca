#/*##########################################################################
# Copyright (C) 2004-2014 V.A. Sole, European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license
# is a problem for you.
#
#############################################################################*/
__author__ = "V.A. Sole - ESRF Data Analysis"
__contact__ = "sole@esrf.fr"
__license__ = "LGPL2+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
import sys
from PyMca5 import QSource
from PyMca5 import SpsDataSource
qt = QSource.qt
QTVERSION = qt.qVersion()

SOURCE_TYPE = SpsDataSource.SOURCE_TYPE

class QSpsDataSource(QSource.QSource):
    """Shared memory source

    The shared memory source object uses SPS through the SPSWrapper
    module to get access to shared memory zones created by Spec or Device Servers

    Emitted signals are :
    updated
    """
    def __init__(self, sourceName):
        QSource.QSource.__init__(self)
        self.__dataSource = SpsDataSource.SpsDataSource(sourceName)
        #easy speed up by making a local reference
        self.sourceName = self.__dataSource.sourceName
        self.isUpdated  = self.__dataSource.isUpdated
        self.sourceType = self.__dataSource.sourceType 
        self.getKeyInfo = self.__dataSource.getKeyInfo 
        self.refresh    = self.__dataSource.refresh
        self.getSourceInfo = self.__dataSource.getSourceInfo

    def __getattr__(self,attr):
        if not attr.startswith("__"):
            #if not hasattr(qt.QObject, attr):
            if not hasattr(self, attr):
                try:
                    return getattr(self.__dataSource, attr)
                except:
                    pass
        raise AttributeError        

    def getDataObject(self,key_list,selection=None, poll=True):
        if poll:
            data = self.__dataSource.getDataObject(key_list,selection)
            self.addToPoller(data)
            return data
        else:
            return self.__dataSource.getDataObject(key_list,selection)

    def customEvent(self, event):
        ddict = event.dict
        ddict['SourceName'] = self.__dataSource.sourceName
        ddict['SourceType'] = SOURCE_TYPE
        key = ddict['Key']

        idtolook = [] 
        ddict['selectionlist'] = []
        for object in self.surveyDict[key]:
            idtolook.append(id(object))
                        
        if key in self.selections.keys():
            n = len(self.selections[key])
            if n:
                a = range(n)
                a.reverse()
                legendlist = []
                for i in a:
                    objectId, info = self.selections[key][i]
                    scanselection = 0
                    if 'scanselection' in info:
                        scanselection = info['scanselection']
                    if info['legend'] in legendlist:
                        if not scanselection:
                            del self.selections[key][i]
                            continue
                    if objectId in idtolook:
                        sel = {}
                        sel['SourceName'] = self.__dataSource.sourceName
                        sel['SourceType'] = SOURCE_TYPE
                        sel['Key']        = key
                        sel['selection'] = info['selection']
                        sel['legend'] = info['legend']
                        legendlist.append(info['legend'])
                        sel['targetwidgetid'] = info.get('targetwidgetid', None)
                        sel['scanselection'] = info.get('scanselection', False) 
                        sel['imageselection'] = info.get('imageselection', False) 
                        ddict['selectionlist'].append(sel)
                    else:
                        del self.selections[key][i]
            
                self.sigUpdated.emit(ddict)
            else:
                print("No info????")
        
if __name__ == "__main__":
    try:
        specname=sys.argv[1]
        arrayname=sys.argv[2]        
    except:
        print("Usage: SpsDataSource <specversion> <arrayname>")
        sys.exit()
    app=qt.QApplication([])
    obj = QSpsDataSource(specname)    
    def mytest(ddict):
        print(ddict['Key'])
    app.mytest = mytest
    data = obj.getDataObject(arrayname,poll=True)
    obj.sigUpdated.connect(mytest) 
    app.exec_()
    
