#NOT RELEASED FOR USE
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import sys
from screeninfo import get_monitors
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox, QFileDialog, QAbstractScrollArea, QSpinBox, QCheckBox, QInputDialog, QLabel, QGridLayout, QComboBox, QFrame, QApplication, QMainWindow, QDialog, QWidget, QTableWidget, QDockWidget, QTableWidgetItem, QFormLayout, QLineEdit, QPushButton, QPlainTextEdit, QSpacerItem
import json
import csv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class mainProgram(QMainWindow):
    def __init__(self):
        super(mainProgram, self).__init__()
        self.tableHeaders = ['Website','Username','Password','Card Number']
        '''Defines headers for the main table \n'''


        self.intro = collect_information(['*Password'],flags=['file','format'])
        self.intro.exec()
        password = self.intro.data_entry[0].text()
        salt = b'\xc7\xb7\x06IY4\x1b\xac\x97\x11\x9c\x8f\xc5\x07\xec\x0f'
        self.key = generateKey(password,salt)

        if self.intro.newFile == False:
            with open(self.intro.database,'r') as file:
                fileString = file.read()
            self.dataBytes = Fernet(self.key).decrypt(fileString)
        else:
            with open(self.intro.database, 'r') as file:
                self.dataBytes = bytes(file.read(),'utf-8')
               

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
        self.saveButton = QPushButton('Save Changes',clicked=self.save)

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
        self.dockLayout.addRow(self.saveButton)
        self.dockMenu.setLayout(self.dockLayout)
        self.dock = QDockWidget('Menu')
        self.dock.setWidget(self.dockMenu)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock) 
    
    def save(self):
        decryptedString = ''
        for header in self.tableHeaders:
            decryptedString = decryptedString + header + ','
        decryptedString = decryptedString[:-1] + '\r\n'
        for rowIndex in range(self.tableWidget.rowCount()):
            for columnIndex in range(self.tableWidget.columnCount()):
                decryptedString = decryptedString + self.tableWidget.item(rowIndex, columnIndex).text() + ','
            decryptedString = decryptedString[:-1] + '\r\n'
        decryptedString = decryptedString[:-2]
        print(decryptedString)
        with open(self.intro.database, 'w') as encrypted_file:
            encrypted_file.write(Fernet(self.key).encrypt(bytes(decryptedString,'utf-8')).decode('utf-8'))

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
        self.dataList = self.dataBytes.decode('utf-8').split('\n')
        for index in range(len(self.dataList)):
            self.dataList[index] = self.dataList[index].split(',')

        self.dataFields = self.dataList[0]
        self.dataGrid = self.dataList[1:]


        self.tableWidget.setColumnCount(len(self.dataFields))
        self.tableWidget.setRowCount(len(self.dataGrid))
        self.tableWidget.setHorizontalHeaderLabels(self.tableHeaders)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setTabKeyNavigation(False)


        for rowIndex, row in enumerate(self.dataGrid):
            for columnIndex, column in enumerate(row):
                self.tableWidget.setItem(rowIndex, columnIndex,QTableWidgetItem(self.dataGrid[rowIndex][columnIndex]))


        #self.tableWidget.itemChanged.connect(self.tableItemChanged)
        self.tableWidget.itemSelectionChanged.connect(self.tableItemSelectionChanged)
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.setColumnWidth(i,int(self.xSize/4)-100)

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



def encrypt(fileString, key):
    return Fernet(key).encrypt(fileString)

def generateKey(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=390000)
    password = bytes(password,'utf-8')
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

class signalClass(QWidget):
    signal1 = QtCore.pyqtSignal()  




class collect_information(QDialog):
    def __init__(self, layout_terms: list = [], flags: list = [], title: str = '', parent=None):
        super(collect_information, self).__init__(parent)
        self.layout1 = QGridLayout(self)
        self.data_entry = [QLineEdit(self) for i in layout_terms]
        self.setWindowTitle(title)
        self.database = ''
        self.newFile = False

        #Buttons
        self.buttons = [QPushButton("Cancel", self), QPushButton("Enter", self)]
        self.buttons[0].clicked.connect(self.reject)
        self.buttons[1].clicked.connect(self.accept)
        self.buttons[0].setAutoDefault(False)
        self.buttons[1].setAutoDefault(True)
        
        for i in flags:
            if i == 'file':
                self.buttons.append(QPushButton("Choose Database:", self))
                self.buttons[-1].clicked.connect(self.choose_database)
                self.buttons[-1].setAutoDefault(False)
            if i == 'format':
                self.buttons.append(QPushButton("Create New Database:",self))
                self.buttons[-1].clicked.connect(self.create_new_database)
                self.buttons[-1].setAutoDefault(False)
        
        for index, term in enumerate(layout_terms):
            if layout_terms[index][0] == '*':
                self.data_entry[index].setEchoMode(QLineEdit.Password)
            self.layout1.addWidget(QLabel(term.strip("*")),index,0)
            self.layout1.addWidget(self.data_entry[index],index,1)
        
        for i in self.buttons[2:]:
            self.layout1.addWidget(i, self.layout1.rowCount(),0)
        
        rows = self.layout1.rowCount()
        self.layout1.addWidget(self.buttons[0],rows+1, 0)
        self.layout1.addWidget(self.buttons[1],rows+1, 1)

    def choose_database(self):
        self.newFile = False
        self.database = QFileDialog()
        self.database.setFileMode(QFileDialog.ExistingFile)
        self.database.setNameFilter("*.csv")
        if self.database.exec() == 1:
            self.database = self.database.selectedFiles()[0]

    def create_new_database(self):
        self.newFile = True
        self.database = QFileDialog.getSaveFileName()[0]
        #if self.database != '.csv':
        with open(self.database,'w') as file:
            file.write('Website,Username,Password,Card\nDeleteMe,DeleteMe,DeleteMe,DeleteMe')     
        
    def return_values(self):
        return [i.text() for i in self.data_entry]
        

if  __name__ == "__main__":
    app = QApplication(sys.argv)
    #signals = signalClass()
    application = mainProgram()
    application.show()
    sys.exit(app.exec())



