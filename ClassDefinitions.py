import sys
from screeninfo import get_monitors
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QFrame, QApplication, QMainWindow, QDialog, QWidget, QTableWidget, QDockWidget, QTableWidgetItem, QFormLayout, QLineEdit, QPushButton
import csv


class mainProgram(QMainWindow):
    def __init__(self, tableHeaders = ['Website','Username','Password','Card']):
        super(mainProgram, self).__init__()

        self.filePath = 'C:\\Users\\jpglo\\Desktop\\Test.csv'        
        try:
            self.getDataFromCSV()
            print(self.data)
        except:
            self.data = [['' for i in tableHeaders]]
        self.tableHeaders = tableHeaders


        self.buildMainWindow()
        self.buildTable()   
        self.buildRightDock()

        self.selectedRow = ''

    def closeEvent(self, *args, **kwargs):
        self.printDataToCSV()

    def getDataFromCSV(self):
        with open(self.filePath, mode='r') as file:
            self.data = list(csv.reader(file))
            

    def printDataToCSV(self):
        with open(self.filePath,'w',newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(self.data)

    def buildMainWindow(self):
        self.monitor = get_monitors()
        self.monitorXSize = int(self.monitor[0].width)
        self.monitorYSize = int(self.monitor[0].height)
        self.xShift = int(self.monitorXSize*.25)
        self.yShift = int(self.monitorYSize*.25)
        self.xSize = int(self.monitorXSize/2)
        self.ySize = int(self.monitorYSize/2)
        self.setGeometry(QtCore.QRect(self.xShift,self.yShift,self.xSize,self.ySize))
        self.setWindowTitle('Passwords')

    def buildTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(len(self.data[0])) 
        for i in range(len(self.data[0])):
            self.tableWidget.setColumnWidth(i,200)
        self.tableWidget.setRowCount(len(self.data))
        
        #----------------------------------------------SET CELL TO HAVE A DROP DOWN MENU-------------------------------------------
        #for i in range(len(self.data)):
        #    for j in range(len(self.data[i])):
        #        combobox = QtGui.QComboBox()
        #       for k in range(0,99):
        #            combobox.addItem(k)
        #        table.setCellWidget(i,j,combobox)

        
        self.tableWidget.setHorizontalHeaderLabels(self.tableHeaders)
        self.tableWidget.itemChanged.connect(self.recordTableChange)
        self.tableWidget.cellClicked.connect(self.cellWasClicked)
        self.setCentralWidget(self.tableWidget)
        self.refreshTable() 

    def cellWasClicked(self, row, column):
        self.selectedRow = row

    def recordTableChange(self, item):
        self.data[item.row()][item.column()] = item.text()

    def buildRightDock(self):
        self.dock = QDockWidget('Menu')
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dockMenu = QWidget()
        self.dockLayout = QFormLayout(self.dockMenu)
        self.dockMenu.setLayout(self.dockLayout)
        self.fields = []
        for i in self.tableHeaders:
            field = QLineEdit(self.dockMenu)
            field.setPlaceholderText(i)
            self.fields.append(field)
            self.dockLayout.addRow(self.fields[-1])
        self.addButton = QPushButton('Add Entry', clicked=self.addEntry)
        self.dockLayout.addRow(self.addButton)
        self.deleteButton = QPushButton('Delete Entry', clicked=self.deleteEntry)
        self.dockLayout.addRow(self.deleteButton)
        self.dock.setWidget(self.dockMenu)

    def refreshTable(self):
        #Iterate over each entry
        for row in range(len(self.data)):
        #Iterate over each entry's data points
            for col in range(len(self.data[row])):
        #Make cell object
                tableWidgetItem = QTableWidgetItem(str(self.data[row][col]))
        #Hide cells in password column  
                if self.tableHeaders[col] == 'Password':
                    tableWidgetItem.setForeground(QtGui.QBrush(QtGui.QColor(255,255,255)))
        #Add cell to table
                self.tableWidget.setItem(row, col, tableWidgetItem)

    def addEntry(self):
        validInput = True
        for i in self.fields:
            if i.text() == '':
                validInput = False
        if validInput:
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.data.append([i.text() for i in self.fields])
            for i in self.fields:
                i.setText('')
        self.refreshTable()

    def deleteEntry(self):
        
        
        if len(self.data)>1:
            selectedEntry = self.data[self.selectedRow][0]
            dialog = deleteDialog(selectedEntry)
            if dialog.delete == 1:
                self.data.pop(self.selectedRow)
        else:
            dialog = QDialog()
            dialog.setFixedSize(300,100)
            dialog.setWindowTitle('Invalid Delete')
            layout = QFormLayout()
            layout.addWidget(QLabel("Cannot Delete Last Entry"))
            button = QPushButton()
            button.setText('OK')
            layout.addWidget(button)
            button.clicked.connect(dialog.accept)
            dialog.setLayout(layout)
            dialog.exec()
        self.buildTable()


class deleteDialog():
    def __init__(self, entry):
        self.delete = 0 #Changes to 1 to confirm delete
        self.dialog = QDialog()
        self.dialog.setWindowTitle('Delete?')
        self.dialogLayout = QFormLayout()
        self.question = QLabel('Type \'CONFIRM\' to Delete Entry for: '+entry+'?')
        self.answer = QLineEdit()
        self.acceptButton = QPushButton()
        self.acceptButton.setText('CONFIRM')
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton()
        self.cancelButton.setText('Cancel')
        self.cancelButton.clicked.connect(self.cancel)
        self.dialogLayout.addWidget(self.question)
        self.dialogLayout.addWidget(self.answer)
        self.dialogLayout.addWidget(self.acceptButton)
        self.dialogLayout.addWidget(self.cancelButton)
        self.dialog.setLayout(self.dialogLayout)
        self.dialog.exec()
    def accept(self):
        if self.answer.text() == 'CONFIRM':
            self.delete = 1
            self.dialog.accept()
        else:
            self.delete = 0
            self.dialog.accept()
    def cancel(self):
        self.delete = 0
        self.dialog.accept()
        


if  __name__ == "__main__":
    app = QApplication([])
    application = mainProgram()
    application.show()
    sys.exit(app.exec())
