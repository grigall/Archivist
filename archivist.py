from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QPushButton, QFileDialog, QTableWidget, QMenuBar, QMenu, QStatusBar, QAction, QMainWindow, QMessageBox, QTableWidgetItem, QDateEdit, QLineEdit, QComboBox
from PyQt5.QtGui import QCursor
import sys
import os
from archivist_reports import print_report
from archivist_analysis import eoy_stats, get_yoy_stats, open_csv, this_year, load_genres, load_formats
from pandas import read_csv, read_json, DataFrame


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        #Global Variables
        self.DEFAULT_SAVE_PATH = os.path.expanduser('~\Documents')
        self.FILE_SAVE = '' #str
        self.FILE_ACTIVE = '' #str
        self.DATAFRAME_IN = DataFrame(None)
        self.DATAFRAME_OUT = DataFrame(None)
        self.DEFAULT_SETTINGS = ''
        self.EOY = ''
        self.YOY = ''
        self.GENRES = load_genres(PATH=r'C:\Users\ML2021\Documents\Projects\Python\GUI_Apps\Archivist\book_genres.csv') #Loads as pandas DataFrame
        self.FORMATS = load_formats(PATH=r'C:\Users\ML2021\Documents\Projects\Python\GUI_Apps\Archivist\book_formats.csv') #Loads as pandas DataFrame
        
        #Base window settings
        self.setObjectName("MainWindow")
        self.setWindowTitle("The Archivist")
        #self.setWindowModality(QtCore.Qt.NonModal)
        self.resize(400, 660)

        #Central Widget
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        
        #=============================================================================#
        #       INTERACTIVE FIELDS
        #=============================================================================#

        self.lblTitle = QLabel(self.centralwidget)
        self.lblTitle.setGeometry(QtCore.QRect(10, 10, 381, 16))
        self.lblTitle.setObjectName("lblTitle")
        self.lineTitle = QLineEdit(self.centralwidget)
        self.lineTitle.setGeometry(QtCore.QRect(10, 30, 381, 20))
        self.lineTitle.setObjectName("lineTitle")
        
        self.lineAuthor = QLineEdit(self.centralwidget)
        self.lineAuthor.setGeometry(QtCore.QRect(10, 80, 181, 20))
        self.lineAuthor.setObjectName("lineAuthor")
        self.lblAuthor = QLabel(self.centralwidget)
        self.lblAuthor.setGeometry(QtCore.QRect(10, 60, 181, 20))
        self.lblAuthor.setObjectName("lblAuthor")

        self.lblLength = QLabel(self.centralwidget)
        self.lblLength.setGeometry(QtCore.QRect(210, 60, 81, 16))
        self.lblLength.setObjectName("lblLength")
        self.lineLength = QLineEdit(self.centralwidget)
        self.lineLength.setGeometry(QtCore.QRect(210, 80, 81, 20))
        self.lineLength.setAlignment(QtCore.Qt.AlignCenter)
        self.lineLength.setObjectName("lineLength")
        
        self.lblPubDate = QLabel(self.centralwidget)
        self.lblPubDate.setGeometry(QtCore.QRect(310, 60, 81, 20))
        self.lblPubDate.setObjectName("lblPubDate")
        self.linePubDate = QLineEdit(self.centralwidget)
        self.linePubDate.setGeometry(QtCore.QRect(310, 80, 81, 20))
        self.linePubDate.setAlignment(QtCore.Qt.AlignCenter)
        self.linePubDate.setObjectName("linePubDate")
        
        self.lblGenre = QLabel(self.centralwidget)
        self.lblGenre.setGeometry(QtCore.QRect(10, 110, 181, 16))
        self.lblGenre.setObjectName("lblGenre")
        self.comboGenre = QComboBox(self.centralwidget)
        self.comboGenre.setGeometry(QtCore.QRect(10, 130, 181, 22))
        self.comboGenre.setObjectName("comboGenre")
        
        self.lblGenre2 = QLabel(self.centralwidget)
        self.lblGenre2.setGeometry(QtCore.QRect(210, 110, 181, 20))
        self.lblGenre2.setObjectName("lblGenre2")
        self.comboGenre2 = QComboBox(self.centralwidget)
        self.comboGenre2.setGeometry(QtCore.QRect(210, 130, 181, 22))
        self.comboGenre2.setObjectName("comboGenre2")

        self.comboFormat = QComboBox(self.centralwidget)
        self.comboFormat.setGeometry(QtCore.QRect(10, 180, 181, 22))
        self.comboFormat.setObjectName("comboFormat")
        self.lblFormat = QLabel(self.centralwidget)
        self.lblFormat.setGeometry(QtCore.QRect(10, 160, 181, 16))
        self.lblFormat.setObjectName("lblFormat")
        
        self.dateRead = QDateEdit(self.centralwidget)
        self.dateRead.setGeometry(QtCore.QRect(210, 180, 181, 22))
        self.dateRead.setObjectName("dateRead")
        self.lblDateRead = QLabel(self.centralwidget)
        self.lblDateRead.setGeometry(QtCore.QRect(210, 160, 181, 20))
        self.lblDateRead.setObjectName("lblDateRead")
        
        self.btnAddBook = QPushButton(self.centralwidget)
        self.btnAddBook.setGeometry(QtCore.QRect(4, 212, 391, 41))
        self.btnAddBook.setObjectName("btnAddBook")
        
        self.tblArchive = QTableWidget(self.centralwidget)
        self.tblArchive.setGeometry(QtCore.QRect(10, 260, 381, 361))
        self.tblArchive.setObjectName("tblArchive")
        self.tblArchive.setColumnCount(9)
        self.tblArchive.setRowCount(0)


        self.lblTitle.setText("Title")
        self.lblAuthor.setText("Author(s)")
        self.lblLength.setText("Length (Pages)")
        self.lblPubDate.setText("Publication Year")
        self.lblGenre.setText("Primary Genre")
        self.lblGenre2.setText("Secondary Genre")
        self.lblFormat.setText("Book Format")
        self.dateRead.setDisplayFormat("yyyy-MM-dd")
        self.lblDateRead.setText("Date Read")
        self.btnAddBook.setText("Save to Archive")

        #Set Default List and Date Values
        self.dateRead.setDate(QtCore.QDate.currentDate())
        
        for idx in range(0, len(self.GENRES)):
            self.comboGenre.addItem('')
            self.comboGenre.setItemText(idx, self.GENRES.loc[idx, 'Genre'])
            self.comboGenre2.addItem('')
            self.comboGenre2.setItemText(idx, self.GENRES.loc[idx, 'Genre'])

        for idx in range(0, len(self.FORMATS)):
            self.comboFormat.addItem('')
            self.comboFormat.setItemText(idx, self.FORMATS.loc[idx, 'Format'])            
                       
        #=============================================================================#
        #       MENU OPTIONS    
        #=============================================================================#       
        self.menubar = QMenuBar(self.centralwidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 440, 21))
        self.menubar.setObjectName("menubar")

        #Top Level Menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuAnalyse = QMenu(self.menubar)
        self.menuAnalyse.setObjectName("menuAnalyse")

        self.menuReport = QMenu(self.menubar)
        self.menuReport.setObjectName("menuReport")

        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionOpen = QAction(self)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave_As = QAction(self)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionPreferences = QAction(self)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionImport = QAction(self)
        self.actionImport.setObjectName("actionImport")
        self.actionStatistics = QAction(self)
        self.actionStatistics.setObjectName("actionStatistics")
        self.actionVisualise = QAction(self)
        self.actionVisualise.setObjectName("actionVisualise")
        self.actionPrint_Report = QAction(self)
        self.actionPrint_Report.setObjectName("actionPrint_Report")
        
        #File Submenu
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addAction(self.actionImport)

        #Analyse Submenu
        self.menuAnalyse.addAction(self.actionStatistics)
        self.menuAnalyse.addAction(self.actionVisualise)

        #Report Submenu
        self.menuReport.addAction(self.actionPrint_Report)

        #Add all top level menus to menu bar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAnalyse.menuAction())
        self.menubar.addAction(self.menuReport.menuAction())

        self.menuFile.setTitle("File")
        self.menuAnalyse.setTitle("Analyse")
        self.menuReport.setTitle("Report")
        self.actionOpen.setText("Open")
        self.actionSave_As.setText("Save As...")
        self.actionPreferences.setText("Preferences")
        self.actionImport.setText("Import")
        self.actionStatistics.setText("Statistics")
        self.actionVisualise.setText("Visualise")
        self.actionPrint_Report.setText("Print Report")

        #Menu Item functionality
        self.actionOpen.triggered.connect(lambda: self.getFile(menuOption='Open'))
        self.actionImport.triggered.connect(lambda: self.getFile(menuOption='Import'))
        self.actionSave_As.triggered.connect(lambda: self.saveFile('Comma-separated Values (*.CSV)', table=self.tblArchive))
        self.actionStatistics.triggered.connect(lambda: self.analyseFile(self.FILE_ACTIVE)) #Takes path-like object
        self.actionPrint_Report.triggered.connect(lambda: self.printReport(self.EOY, self.YOY))
        self.btnAddBook.clicked.connect(lambda: self.saveBookData())

        #=============================================================================#
        #       CSS and WINDOW INSTANTIATION    
        #=============================================================================#    

        #Show window last of all
        self.css()
        self.show()

    def clearFields(self):
        self.lineTitle.clear()
        self.lineAuthor.clear()
        self.lineLength.clear()
        self.linePubDate.clear()

    def saveBookData(self, *args, **kwargs):
        bookList = []

        self.tblArchive.setHorizontalHeaderLabels(('Title','Length','Pub_Date','Genre','Genre_2','Author','Format','Year_Read','Date_Read'))
        #Add all values to list
        bookList.append(self.lineTitle.text()) #Title
        bookList.append(int(self.lineLength.text())) #Length in Pages int   
        bookList.append(int(self.linePubDate.text())) #Publication Year int
        bookList.append(self.comboGenre.currentText()) #Primary Genre
        bookList.append(self.comboGenre2.currentText()) #Secondary Genre
        bookList.append(self.lineAuthor.text()) #Author(s) 
        bookList.append(self.comboFormat.currentText()) #Format
        bookList.append(self.dateRead.date().year()) #Year Read int
        bookList.append(self.dateRead.date().toString('yyyy-MM-dd')) #Date Read

        #Analyse table rows and add new entries
        if self.tblArchive.rowCount() == 0:
            newRowCount = 0
        else:
            newRowCount = self.tblArchive.rowCount()
        self.tblArchive.insertRow(newRowCount)
        for idx in range(0, len(bookList)):
            self.tblArchive.setItem(newRowCount, idx, QTableWidgetItem(str(bookList[idx])))
        
        #Clear Input Fields
        self.clearFields()

        #Update Active File
        self.FILE_ACTIVE = self.readTable(self.tblArchive)

    def writeTable(self, dataframe, targetTable):
        #Adjust table parameters to conform to imported file
        targetTable.setColumnCount(len(dataframe.columns))
        targetTable.setRowCount(0) #Will erase any data present in table already
        targetTable.setHorizontalHeaderLabels(tuple(dataframe.columns.tolist()))

        for idx in dataframe.index.tolist():
            targetTable.insertRow(targetTable.rowCount())
            for col in range(0,len(dataframe.columns)):
                targetTable.setItem(idx, col, QTableWidgetItem(str(dataframe.iloc[idx, col])))

    def readTable(self, table):
        read_table_headers = [table.horizontalHeaderItem(i).text() for i in range(9)]

        temp_data = []
        for idx in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(idx, col)
                if item is not None:
                    try:
                        new_item = int(item.text()) #Converts Length, Pub_Date, and Year_Read to integers
                    except:
                        new_item = item.text()
                    row_data.append(new_item)
                else:
                    row_data.append('')
            temp_data.append(row_data)
        
        targetDataframe = DataFrame(temp_data, columns=read_table_headers)
        return targetDataframe
        

    def errorMsg(self, TITLE, TEXT) -> str:
        msg = QMessageBox()
        msg.setWindowTitle(TITLE)
        msg.setText(TEXT)
        x = msg.exec_()



    def getFile(self, *args, **kwargs):
        if kwargs['menuOption'] == 'Open':
            ftypes = 'Comma-separated Values (*.CSV);; Tab-separated Values (*.TSV, *.TXT)'
        elif kwargs['menuOption'] == 'Import':
            ftypes = 'JavaScript Object Notation (*.JSON);; Microsoft Excel Spreadsheet (*.XLSX)'
        else:
            pass
        #Open file dialog
        file = QFileDialog.getOpenFileName(self, 'Open File', self.DEFAULT_SAVE_PATH, ftypes)

        if file:
            if kwargs['menuOption'] == 'Open':
                self.FILE_ACTIVE = str(file[0])
                self.DATAFRAME_IN = read_csv(self.FILE_ACTIVE, sep='\t')
            elif kwargs['menuOption'] == 'Import':
                self.FILE_ACTIVE = str(file[0])
            else:
                pass

            self.writeTable(self.DATAFRAME_IN, self.tblArchive) #Write imported data to table widget

    def saveFile(self, FILTER, **kwargs):
        if kwargs['table']:
            df_out = self.readTable(kwargs['table'])
        else:
            pass
        #Open file dialog
        directory = QFileDialog.getSaveFileName(self, "Select Directory", self.DEFAULT_SAVE_PATH, filter=FILTER)
        if directory:
            if kwargs['table']:
                df_out.to_csv(directory[0], sep='\t', encoding='utf-8', index=False)
            else:
                self.FILE_SAVE = str(directory[0])
        else:
            pass
        
    def analyseFile(self, active_file):
        if len(active_file) == 0 and self.tblArchive.rowCount() > 0:
            df_out = self.readTable(self.tblArchive)
            self.EOY = eoy_stats(df_out, this_year())
            self.YOY = get_yoy_stats(self.EOY)
            self.errorMsg('Attention', 'File Analysed!')
        elif len(active_file) > 0:
            if type(active_file) == str:
                self.EOY = eoy_stats(open_csv(active_file), this_year()) #When active_file is path-like object
            else:
                self.EOY = eoy_stats(active_file, this_year()) #When active_file is DataFrame
            self.YOY = get_yoy_stats(self.EOY)
            self.errorMsg('Attention', 'File Analysed!')
        else:
            self.errorMsg('Missing File Error', 'Must Open, Import, or Create file first!')
        
    def printReport(self, EOY_STATS, YOY_STATS):
        if type(EOY_STATS) == str or type(YOY_STATS) == str:
            self.errorMsg('Analysis Error', 'Must analyse a file first!')
        else:
            self.saveFile('Portable Document Format (*.PDF)', table=False)
            self.errorMsg('Attention', 'Report saved to:\n'+self.FILE_SAVE)
            print_report(self.FILE_SAVE, EOY_STATS, YOY_STATS)

    def css(self):
        with open('The_Archivist.css') as file:
            sheet = file.read()
            self.setStyleSheet(sheet)

app = QApplication(sys.argv)

ui = UI()

sys.exit(app.exec_())
