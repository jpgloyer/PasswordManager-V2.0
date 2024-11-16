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
import winreg


class mainProgram(QMainWindow):
    def __init__(self):
        super(mainProgram, self).__init__()
                 

        self.intro = collect_information(['*Password'],flags=['file','format'])
        self.intro.exec() 


        self.generateKey()


        self.selectFileAndStoreLocation()

               
        #Initial Setup
        self.buildMainWindow()
        self.buildInitialTable()
        self.buildRightDock()




    def selectFileAndStoreLocation(self):
                #Start File Selection Section
        self.registryKey = winreg.HKEY_CURRENT_USER
        self.registrySubKey = "Software\\PasswordManager"
        try:
            self.create_registry_key(self.registrySubKey)
        except:
            pass
        if self.intro.newFile == False:
            if self.intro.database != '': #User manually selected file
                with open(self.intro.database,'r') as file:
                    fileString = file.read()
                self.write_registry_value('DatabaseLocation',self.intro.database)
            else: #User did not select file or create new file
                self.intro.database = self.read_registry_value('DatabaseLocation')
                with open(self.intro.database,'r') as file:
                    fileString = file.read()
            self.dataBytes = Fernet(self.key).decrypt(fileString) #------------------------------------THIS LINE ERRORS ON A BAD PASSWORD-------------
        else: #User created new file
            with open(self.intro.database, 'r') as file:
                self.dataBytes = bytes(file.read(),'utf-8')
            self.write_registry_value('DatabaseLocation',self.intro.database)
        #End File Selection Section

    def create_registry_key(self, path):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        except PermissionError:
            print('Error')
            pass

    def read_registry_value(self, value_name):
        try:
            with winreg.OpenKey(self.registryKey, self.registrySubKey) as reg_key:
                value, _ = winreg.QueryValueEx(reg_key, value_name)
                print(value)
                return value
        except:
            print('Error')

            pass

    def write_registry_value(self, value_name, value_data):
        try:
            with winreg.OpenKey(self.registryKey, self.registrySubKey, 0, winreg.KEY_WRITE) as reg_key:
                winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, value_data)
        except:
            print('Error')

            pass
        
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
        self.importDataButton = QPushButton('Import CSV',clicked=self.importData)
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
        self.dockLayout.addRow(self.importDataButton)
        self.dockMenu.setLayout(self.dockLayout)
        self.dock = QDockWidget('Menu')
        self.dock.setWidget(self.dockMenu)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock) 
    
    def importData(self):
        fileSelect = QFileDialog()
        fileSelect.setNameFilter('*.csv')
        fileSelect.exec()
        with open(fileSelect.selectedFiles()[0], 'r') as file:
            newPasswords = file.read()
            newPasswords = newPasswords.split()
            for index, row in enumerate(newPasswords):
                newPasswords[index] = row.split(',')
        for rowIndex, row in enumerate(newPasswords[1:]):
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            for columnIndex, column in enumerate(newPasswords[rowIndex]):
                cell = QTableWidgetItem(column)
                self.tableWidget.setItem(self.tableWidget.rowCount()-1,columnIndex,cell)

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
        with open(self.intro.database, 'w') as encrypted_file:
            encrypted_file.write(Fernet(self.key).encrypt(bytes(decryptedString,'utf-8')).decode('utf-8'))

    def resizeCell(self):
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def buildMainWindow(self):
        self.monitor = get_monitors()
        self.monitorXSize = int(self.monitor[0].width)
        self.monitorYSize = int(self.monitor[0].height)
        self.xShift = int(self.monitorXSize*.1)
        self.yShift = int(self.monitorYSize*.1)
        self.xSize = int(self.monitorXSize*.8)
        self.ySize = int(self.monitorYSize*.8)
        self.setGeometry(QtCore.QRect(self.xShift,self.yShift,self.xSize,self.ySize))
        self.setWindowTitle('Add Material to Contract')
    
    def buildInitialTable(self):
        self.tableWidget = QTableWidget()  
        self.currentlySelectedCell = [0,0]
        self.tableHeaders = ['Website','Username','Password','Card Number']
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
                cell = QTableWidgetItem(self.dataGrid[rowIndex][columnIndex])
                if columnIndex == 2:
                    cell.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                self.tableWidget.setItem(rowIndex, columnIndex,cell)

        self.tableWidget.itemSelectionChanged.connect(self.tableItemSelectionChanged)
        self.tableWidget.resizeRowsToContents()
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.setColumnWidth(i,int(self.xSize/4)-100)
        
        self.setCentralWidget(self.tableWidget)

    def updateDeleteRowButton(self):
        if self.tableWidget.rowCount()>1:
            self.deleteEntryButton.setText('Delete Item: '+self.tableWidget.item(self.currentlySelectedCell[0],0).text())

    def tableItemSelectionChanged(self):
        self.currentlySelectedCell = [self.tableWidget.currentRow(),self.tableWidget.currentColumn()]
        self.updateDeleteRowButton()
        
    def addEntry(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        for index, column in enumerate(self.tableHeaders):
            cell = QTableWidgetItem(self.dockInformation[column].text())
            self.tableWidget.setItem(self.tableWidget.rowCount()-1,index,cell)
        for i in self.dockInformation:
            self.dockInformation[i].setText('')

    def deleteEntry(self):
        self.tableWidget.removeRow(self.currentlySelectedCell[0])

    def generateKey(self):
        self.password = self.intro.data_entry[0].text()
        self.salt = b'\xc7\xb7\x06IY4\x1b\xac\x97\x11\x9c\x8f\xc5\x07\xec\x0f'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                        length=32,
                        salt=self.salt,
                        iterations=390000)
        self.password = bytes(self.password,'utf-8')
        self.key = base64.urlsafe_b64encode(kdf.derive(self.password))

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

    def closeEvent(self, event):
        sys.exit(app.exec())

    def choose_database(self):
        self.newFile = False
        self.database = QFileDialog()
        self.database.setFileMode(QFileDialog.ExistingFile)
        self.database.setNameFilter("*.csv")
        if self.database.exec() == 1:
            self.database = self.database.selectedFiles()[0]

    def create_new_database(self):
        self.newFile = True
        #Move below to selectFileAndStoreLocation ------------------------------------------------------------------
        self.database = QFileDialog.getSaveFileName()[0]
        if self.database != '':
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



