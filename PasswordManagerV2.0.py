#NOT RELEASED FOR USE
import sys
from screeninfo import get_monitors
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QAbstractScrollArea, QSpinBox, QCheckBox, QInputDialog, QLabel, QGridLayout, QComboBox, QFrame, QApplication, QMainWindow, QDialog, QWidget, QTableWidget, QDockWidget, QTableWidgetItem, QFormLayout, QLineEdit, QPushButton, QPlainTextEdit, QSpacerItem
import json
import csv



class mainProgram(QMainWindow):
    def __init__(self):
        super(mainProgram, self).__init__()
        self.tableHeaders = ['Website','Username','Password','Card Number']
        '''Defines headers for the main table \n'''


        newFileDialog = QMessageBox()
        newFileDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel) 
        newFile = newFileDialog.exec()
        self.data = [{}]

        if not newFile:
            fileDialog = QFileDialog()
            fileDialog.setNameFilter('*.csv')
            fileDialog.exec()
            with open(fileDialog.selectedFiles()[0]) as file:
                self.data = list(csv.DictReader(file))

        else:
            for i in self.tableHeaders:
                self.data[0][i] = ''



        self.monitor = get_monitors()
        '''Defines monitor object that allows automatic screen window sizing per screen size'''
        self.monitorXSize = int()
        '''Defines width of user's monitor'''
        self.monitorYSize = int()
        '''Defines height of user's monitor'''
        self.xShift = int()
        '''Defines x shift used to center window'''
        self.yShift = int()
        '''Defines y shift used to center window'''
        self.xSize = int()
        '''Defines width of window'''
        self.ySize = int()
        '''Defines height of window'''

        self.tableWidget = QTableWidget()                   
        '''Defines Main Scrollable Table'''
        self.tableWidgetItems = [[]] 
        '''Defines objects to be slotted into main table cells'''
        

        self.dock = QDockWidget('Menu')
        '''Defines right-side dock'''
        self.dockMenu = QWidget()
        '''Defines widget to be added to right-side dock'''
        self.dockLayout = QFormLayout()
        '''Defines layout for widget on right-side dock'''
        self.dockItemPanels = [QLineEdit()]
        '''Defines One Text box per panel to allow for new row addition'''
        self.addButton = QPushButton()
        '''Defines button on right-side dock that makes new entry from right-side dock data'''
        self.deviceNames = [QLineEdit()]
        '''Defines text boxes on right-side dock used to enter individual device names'''
        self.deviceNameSlots = 0
        self.spacer = QSpacerItem(0,0)
        '''Defines space between the add section of the right-side dock and the rest of the right-side dock'''
        self.printButton = QPushButton()
        '''Defines button to print the current table to the console'''
        self.deleteButton = QPushButton()


        self.currentlySelectedCell = [0,0]

        self.uniqueItemNumbers = []
        

        #Initial Setup
        self.buildMainWindow()
        self.buildInitialTable()
        self.buildRightDock()


    def buildRightDock(self):
        self.dockLayout = QFormLayout()
        self.dockMenu = QWidget()
        self.website = QLineEdit()
        self.website.setPlaceholderText('Website:')
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username:')
        self.password = QLineEdit()
        self.password.setPlaceholderText('Password:')
        self.card = QLineEdit()
        self.card.setPlaceholderText('Card (Optional):')
        self.addEntryButton = QPushButton('Add Entry:',clicked=self.addEntry)
        self.deleteEntryButton = QPushButton('Delete Entry:',clicked=self.deleteEntry)

        self.dockInformation = {self.tableHeaders[0]:self.website,
                                self.tableHeaders[1]:self.username,
                                self.tableHeaders[2]:self.password,
                                self.tableHeaders[3]:self.card}

        self.dockLayout.addRow(self.website)
        self.dockLayout.addRow(self.username)
        self.dockLayout.addRow(self.password)
        self.dockLayout.addRow(self.card)
        self.dockLayout.addRow(self.addEntryButton)
        self.dockLayout.addRow(self.deleteEntryButton)
        self.dockMenu.setLayout(self.dockLayout)
        self.dock = QDockWidget('Menu')
        self.dock.setWidget(self.dockMenu)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock) 

    def resizeCell(self):
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def buildMainWindow(self):
        self.monitorXSize = int(self.monitor[0].width)
        self.monitorYSize = int(self.monitor[0].height)
        self.xShift = int(self.monitorXSize*.1)
        self.yShift = int(self.monitorYSize*.1)
        self.xSize = int(self.monitorXSize*.8)
        self.ySize = int(self.monitorYSize*.8)
        self.setGeometry(QtCore.QRect(self.xShift,self.yShift,self.xSize,self.ySize))
        self.setWindowTitle('Add Material to Contract')
    
    def buildInitialTable(self):
        self.tableWidget.setColumnCount(len(self.tableHeaders))
        self.tableWidget.setRowCount(len(self.data))
        self.tableWidget.setHorizontalHeaderLabels(self.tableHeaders)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setTabKeyNavigation(False)
        
        for rowIndex, row in enumerate(self.data):
            for columnIndex, column in enumerate(row):
                self.tableWidget.setItem(rowIndex, columnIndex,QTableWidgetItem(self.data[rowIndex][column]))


        #self.tableWidget.itemChanged.connect(self.tableItemChanged)
        self.tableWidget.itemSelectionChanged.connect(self.tableItemSelectionChanged)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

        self.setCentralWidget(self.tableWidget)

    def tableItemSelectionChanged(self):
        self.currentlySelectedCell = (self.tableWidget.currentRow(),self.tableWidget.currentColumn())
        entry = self.tableWidget.itemAt(self.currentlySelectedCell[0],0).text()
        self.deleteEntryButton.setText(f'Delete Entry for: {entry}')
        #self.buildRightDock()
        
    def addEntry(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        for index, column in enumerate(self.tableHeaders):
            cell = QTableWidgetItem(self.dockInformation[column].text())
            self.tableWidget.setItem(self.tableWidget.rowCount()-1,index,cell)
        for i in self.dockInformation:
            self.dockInformation[i].setText('')

    def deleteEntry(self):
        self.tableWidget.removeRow(self.currentlySelectedCell[0])

        

class signalClass(QWidget):
    signal1 = QtCore.pyqtSignal()  


if  __name__ == "__main__":
    app = QApplication(sys.argv)
    #signals = signalClass()
    application = mainProgram()
    application.show()
    sys.exit(app.exec())
