from tkinter import messagebox
import sqlite3
from xlsxwriter.workbook import Workbook
from unittest.loader import VALID_MODULE_NAME
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from models import DB_NAME
import sip
import funcoesdb
import sys

MINIMo = 5
eqEntrada = [
    ('med'        , 'Medicamento'),
    ('estoqueTipo', 'Tipo embalagens'),
    ('estoque'    , 'Embalagens'),
    ('data'       , 'Data'),
]
eqSaida = [
    ('med'   , 'Medicamento'),
    ('pac'   , 'Paciente'),
    ('dosesTipo', 'Tipo de dose'),
    ('doses' , 'Doses dadas'),
    ('data'  , 'Data'),
]
eqMedicamentos = [
   ('nomeMedicamento', 'Nome'),
   ('nomeEmbalagem', 'Tipo de Embalagem'),
   ('embalagens', 'Quantidade de embalagens'),
   ('nomeDose', 'Tipo de dose' ),
   ('ratioDose', 'Quantidade de doses por embalagem'),
   ('doses', 'Quantidade de doses'),
   ('precoPorEmbalagem', 'Preço')
]
eqPacientes = [
   ('nome', 'Nome'),
   ('sobrenome', 'Sobrenome'),
   ('cpf', 'CPF' ),
   ('info', 'Informações adicionais'),
]

BUTTONS = ["Adicionar", 'Editar', 'Deletar']
class  MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Controle de Estoque")
        #self.showMaximized()

        tabwizard = TabWizard()
        self.setCentralWidget(tabwizard)
        tabNames = ['Estoque','Entrada','Saída','Pacientes']
        tabs = [
            ListAndInfo(eqMedicamentos,1,funcoesdb.qAllMed),
            TableEstoque( eqEntrada, funcoesdb.qAllChangeEnt),
            TableEstoque( eqSaida,   funcoesdb.qAllChangeSai),
            ListAndInfo(eqPacientes, 2,funcoesdb.qAllPac)
        ]
        medChanges = {
            'ratioDose':int,
            'precoPorEmbalagem':float,
        }
        medExcludes = ['id','doses','entrada','saida','embalagens']
        pacExcludes = ['id','saida']

        entChanges = {
            'med':funcoesdb.getAllMedNames(),
            'embalagens':int,
            'estoque':int,
            'data' : 'date'
        }
        entExcludes = ['id', 'estoqueTipo']

        saidaChanges = {
            'med':funcoesdb.getAllMedNames(),
            'pac':funcoesdb.getAllPacNames(),
            'doses': int,
            'data' : 'date'
        }

        saidaExcludes = ['id','dosesTipo']
        interfaceMed = funcoesdb.dbInterface(
                                    funcoesdb.dMedObj,
                                    funcoesdb.delKidsMed,
                                    funcoesdb.addMedicamento, 
                                    funcoesdb.aMedObj, 
                                    funcoesdb.eMedObj, 
                                    funcoesdb.gMedObj)
        interfaceEnt = funcoesdb.dbInterface(
                                    funcoesdb.dEntObj, 
                                    funcoesdb.delKidsEnt,
                                    funcoesdb.addEntrada, 
                                    funcoesdb.aEntObj,
                                    funcoesdb.eEntObj, 
                                    funcoesdb.gEntObj)
        interfaceSai = funcoesdb.dbInterface(
                                    funcoesdb.dSaiObj, 
                                    funcoesdb.delKidsSai,
                                    funcoesdb.addSaida, 
                                    funcoesdb.aSaiObj,
                                    funcoesdb.eSaiObj, 
                                    funcoesdb.gSaiObj)
        interfacePac = funcoesdb.dbInterface(
                                    funcoesdb.dPacObj, 
                                    funcoesdb.delKidsPac,
                                    funcoesdb.addPaciente, 
                                    funcoesdb.aPacObj,
                                    funcoesdb.ePacObj, 
                                    funcoesdb.gPacObj)

        tabwizard.addPage(Page(tabs[0], BUTTONS, eqMedicamentos, interfaceMed, medChanges,medExcludes), tabNames[0])
        tabwizard.addPage(Page(tabs[1], BUTTONS, eqEntrada, interfaceEnt, entChanges,entExcludes), tabNames[1])
        tabwizard.addPage(Page(tabs[2], BUTTONS, eqSaida, interfaceSai,saidaChanges,saidaExcludes), tabNames[2])
        tabwizard.addPage(Page(tabs[3], BUTTONS, eqPacientes, interfacePac, excludeadd=pacExcludes), tabNames[3])

        self.show()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&Arquivo", self)
        menuBar.addMenu(fileMenu)
        exp = QAction("&Exportar como excel...", self)
        imp = QAction("&Importar banco...", self)
        fileMenu.addAction(exp)
        fileMenu.addAction(imp)
        exp.triggered.connect(self.exp)
        imp.triggered.connect(open)
    def exp(self):
        fileName = None
        dialog = QFileDialog(self, "Exportar como excel")
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            fileName = dialog.selectedFiles()
            self.exp_excel(fileName[0])
    
    def exp_excel(self, path):
        workbook = Workbook('output2.xlsx')
        worksheet = workbook.add_worksheet()
        conn=sqlite3.connect('test.sqlite')
        cursor = conn.cursor() # Create the cursor
        tables = list(cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")) # Get all table names
        tables = list(map(lambda x: x[0], tables)) # convert the list of tuple to list of str
        for table in tables:
            try: worksheet = workbook.add_worksheet(name=table[0:31]) # Sheet names in excel can have up to 31 chars
            except:pass
            for row_number, row in enumerate(cursor.execute('SELECT * FROM '+table)): # row is a tuple here
                for column_number, item in enumerate(row):
                    try: worksheet.write(row_number, column_number, item) # Write the cell in the current sheet
                    except:pass
        workbook.close()


class TabWizard(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def addPage(self, page, title):
        if not isinstance(page, Page):
            raise TypeError(f"{page} must be Page object")
        self.addTab(page, title)
        page.clicked.connect(lambda event: self.iClick(event))

    def iClick(self, event):
        print(event)

class Page(QWidget):
    clicked = pyqtSignal(str)
    def __init__(self, mWidget, buttons, eqName, dbInterface, changes=None,excludeadd = None, parent=None):
        super().__init__(parent)

        self.mainW = mWidget
        lay = QVBoxLayout(self)
        self.popup=None
        self.dbInterface = dbInterface
        lay.addWidget(mWidget)
        self.selection = None
        self.eqName = eqName
        self.changes = changes
        self.excludeadd= excludeadd

        bs = QWidget()
        laybs = QHBoxLayout(bs)
        laybs.setAlignment(Qt.AlignLeft)
        laybs.setSpacing(100)

        bAdicionar = QPushButton(buttons[0])
        bAdicionar.setObjectName('add')
        bAdicionar.clicked.connect(self.handleClick)
        laybs.addWidget(bAdicionar)

        bEditar = QPushButton(buttons[1])
        bEditar.setObjectName('edit')
        bEditar.clicked.connect(self.handleClick)
        laybs.addWidget(bEditar)

        bDeletar = QPushButton(buttons[2])
        bDeletar.setObjectName('del')
        bDeletar.clicked.connect(self.handleClick)
        laybs.addWidget(bDeletar)

        bDesfazer = QPushButton('Desfazer')
        bDesfazer.setObjectName('desfazer')
        bDesfazer.clicked.connect(self.handleClick)
        laybs.addWidget(bDesfazer)

        bRefazer = QPushButton('Refazer')
        bRefazer.setObjectName('refazer')
        bRefazer.clicked.connect(self.handleClick)
        laybs.addWidget(bRefazer)

        bAtualizar = QPushButton('Atualizar')
        bAtualizar.setObjectName('atualizar')
        bAtualizar.clicked.connect(self.handleClick)
        laybs.addWidget(bAtualizar)

        lay.addWidget(bs)

        self.mainW.selection.connect(lambda d: self.handleSelection(d))

    def handleSelection(self, d):
        self.selection = d
        print(d)

    def handleClick(self):
        b = self.sender()
        name = b.objectName()
        change = False 
        if name == 'edit':
            if self.selection != None:
                self.popup = EditPopUp(self.selection['data'], self.eqName, self.changes)
                print(self.selection['id'])
                self.popup.signal.connect(lambda d : self.dbInterface.edit(self.selection['id'], d))
                self.popup.exec_()
                change = True
                print('edit')
        elif name == 'del':
            if self.selection != None:
                self.dbInterface.delete(self.selection['id'])
                change = True
                print('del')
        elif name == 'add':
            self.popup = AdderPopUp(self.eqName,self.changes,self.excludeadd)
            self.popup.signal.connect(lambda l : self.dbInterface.add(l))
            self.popup.exec_()
            change = True
            print('add')
        elif name == 'desfazer':
            self.dbInterface.undo()
            change = True
        elif name == 'refazer':
            self.dbInterface.redo()
            change = True
        elif name == 'atualizar':
            change = True

        if change:
            self.mainW.refresh()

#creates a table widget using a db query func and 
#a reference list of dicts as guide for the structure
class TableEstoque(QTableWidget):
    selection = pyqtSignal(dict)
    def __init__(self, eqNames, dbfunc,*args):
        QTableWidget.__init__(self, *args)
        self.dbfunc = dbfunc
        self.dbData = dbfunc()
        self.eqNames = eqNames
        self.setColumnCount(len(eqNames))
        self.setRowCount(len(self.dbData))

        self.setHorizontalHeaderLabels([name for _, name in eqNames])
        self.setData()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clicked.connect(self.handleClick)

    def refresh(self):
        self.dbData = self.dbfunc()
        self.setRowCount(len(self.dbData))
        self.setData()
        self.resizeRowsToContents()
    #takes output dich_db_entity and turn it into 
    #a table widget, referecing dbNewNames, for the
    #col order and row headers
    def handleClick(self):
        ci = self.currentItem()
        id = (self.dbData[ci.row()])['id']
        itemName = (self.eqNames[ci.column()])[0]
        itemData = ci.text()
        self.selection.emit({'id': id, 'data': {itemName:itemData}})

    def setData(self):
        for col,(dbName,_) in enumerate(self.eqNames):
            for row,dbItemDict in enumerate(self.dbData):
                tableData = str(dbItemDict[dbName])
                self.setItem(row,col,QTableWidgetItem(tableData))

class ListAndInfo(QWidget):
    selection = pyqtSignal(dict)
    def __init__(self, nameOrder, firstShow, dbfunc, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.nameOrder = nameOrder
        self.dbfunc = dbfunc
        self.dbData = dbfunc()
        self.firstShow = firstShow

        self.lay = QHBoxLayout(self)

        self.lista = Lista(self.nameOrder, firstShow, self.dbData)
        self.lay.addWidget(self.lista)
        self.info = None

        self.lista.signal.connect(lambda d: self.handleClick(d))

    def refresh(self):
        self.dbData = self.dbfunc()
        if(self.info != None):
            self.lay.removeWidget(self.info)
            sip.delete(self.info)
        self.info = None
        self.lay.removeWidget(self.lista)
        self.lista.setParent(None)
        sip.delete(self.lista)
        self.lista = None
        self.lista = Lista(self.nameOrder, self.firstShow, self.dbData)
        self.lay.addWidget(self.lista)
        self.lista.signal.connect(lambda d: self.handleClick(d))

    def handleClick(self, d):
        if(self.info != None):
            self.lay.removeWidget(self.info)
            sip.delete(self.info)

        self.info = Info(self.nameOrder, d)
        self.lay.addWidget(self.info)
        self.info.move(self.maximumWidth()-20, self.maximumHeight() -20)
        self.selection.emit({'id': d['id'], 'data': d})

class Info(QWidget):
    def __init__(self, nameOrder, dbDict, *args, **kwargs):
        super().__init__(*args, *kwargs)
        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)
        info = ''
        for dbName,infoName in nameOrder:
            if dbName in dbDict:
                dbData = dbDict[dbName]
                l = '{}: {}\n'.format(infoName, dbData)
                info += l
        self.label = QLabel(info, self)
        self.label.resize(200,200)
        self.label.move(20,20)
        lay.addWidget(self.label)

class Lista(QListWidget):
    signal = pyqtSignal(dict)
    def __init__(self, nameOrder, firstShow, dbData, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.itemClicked.connect(lambda:self.handleClick())
        self.dbData = dbData

        for dbDict in dbData:
            listItemName = ''
            for i in range(firstShow):
                dbData    = dbDict[nameOrder[i][0]]

                if dbData != None:
                    listItemName += str(dbData)
                    if i+1 < firstShow: listItemName+=' '
                
            self.addItem(QListWidgetItem(listItemName))
            
    def handleClick(self):
        listIndex = self.indexFromItem(self.currentItem())
        dbDict = self.dbData[listIndex.row()]
        self.signal.emit(dbDict)

#datadict = dict with edit fields
#eqName = equivalt names 
#changes = [('field_to_be_filled', query_data, already in list form)]
class EditPopUp(QDialog):
    signal = pyqtSignal(dict)
    def __init__(self, dataDict, eqName, changes=None, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.lay = QVBoxLayout(self)
        self.dataDict = dataDict
        self.inputs = {}

        for key,value in dataDict.items():
            #pick name I want out of eqName
            labelName = (eqName[inTupleList(key, eqName, 0)])[1]
            label = QLabel(labelName)
            input = QLineEdit()
            if changes != None: 
                if key in changes:
                    data = changes[key]
                    if data == 'date':
                        input = QDateEdit(QDate.currentDate())
                    elif data == int:
                        input.setValidator(QIntValidator())
                    elif data == float:
                        input.setValidator(QDoubleValidator())
                    elif type(data) == list:
                        completer = QCompleter(data)
                        completer.setCaseSensitivity(Qt.CaseInsensitive)
                        input.setCompleter(completer)   
                        input.setText(str(value))
                    self.inputs[key] = (input, data)
                        
                elif type(input) == QLineEdit:
                    input.setText(str(value))
                    self.inputs[key] = input

            self.lay.addWidget(label)
            self.lay.addWidget(input)
        bs = QWidget()
        laybs = QHBoxLayout(bs)
        bAdicionar = QPushButton('Salvar')
        bAdicionar.clicked.connect(self.getInput)
        laybs.addWidget(bAdicionar)

        bCancelar = QPushButton('Cancelar')
        bCancelar.clicked.connect(self.close)
        laybs.addWidget(bCancelar)

        self.lay.addWidget(bs)

    def getInput(self):
        output = {}
        for key in self.dataDict:
            item = self.inputs[key]
            append = None
            if type(item) == tuple:
                it = item[0]
                data = item[1]
                if data == 'date':
                    t = it.date()
                    append = t.toPyDate()
                elif data == int:
                    if it.hasAcceptableInput() == False:
                        messagebox(self, 'Entrada não é válida, usar números inteiros')
                        break
                    append = int(it.text())
                elif data == float:
                    if it.hasAcceptableInput() == False:
                        messagebox(self, 'Entrada não é válida, usar números decimais')
                        break
                    append = float(it.text())
                elif type(data) == list:
                    text = it.text()
                    print(text)
                    changed = False
                    for i,t in enumerate(data):
                        if text == t:
                            append = i+1
                            change = True
                    if not change:
                        messagebox(self, 'Entrada não é válida, usar medicamento/paciente já existente')
                    
            else:
                append = item.text()

            if append != None:
                output[key] = append 
        self.signal.emit(output)
        print(output)
        self.close()

def inTupleList(field_name, list, index):
    for i, data in enumerate(list):
        if data[index] == field_name:
            return i
    return -1

#name that appear on popup, query, validator
#I truly hate gui
#fieldchanges = dict with dbnames and a list of dicts with
#item data and item id, if its a string name 'date', make
#a date object

class AdderPopUp(QDialog):
    signal = pyqtSignal(list)
    def __init__(self, eqField, changes=None, exclude=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Adicionar novo item')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.inputs = []

        self.lay = QVBoxLayout(self)
        for key, name in eqField:
            label = QLabel(name)
            input = QLineEdit()
            append = input
            if key in exclude:
                continue
            if changes != None: 
                if key in changes:
                    data = changes[key]
                    if data == 'date':
                        input = QDateEdit(QDate.currentDate())
                        append = (input, data)
                    elif data == int:
                        input.setValidator(QIntValidator())
                        append = (input, data)
                    elif data == float:
                        input.setValidator(QDoubleValidator())
                        append = (input, data)
                    elif type(data) == list:
                        completer = QCompleter(data)
                        completer.setCaseSensitivity(Qt.CaseInsensitive)
                        input.setCompleter(completer)   
                        append = (input, data)

            self.lay.addWidget(label)
            self.lay.addWidget(input)
            self.inputs.append(append)
        bs = QWidget()
        laybs = QHBoxLayout(bs)
        bAdicionar = QPushButton('Adicionar')
        bAdicionar.clicked.connect(self.getInput)
        laybs.addWidget(bAdicionar)

        bCancelar = QPushButton('Cancelar')
        bCancelar.clicked.connect(self.close)
        laybs.addWidget(bCancelar)

        self.lay.addWidget(bs)

    def getInput(self):
        output = []
        for item in self.inputs:
            append = None
            if type(item) == tuple:
                it = item[0]
                data = item[1]
               #if it.isModified() == False and data != 'date':
               #    messagebox(self, 'Por favor preencher todos os campos')
               #    break
                if data == 'date':
                    t = it.date()
                    append = t.toPyDate()
                elif data == int:
                    if it.hasAcceptableInput() == False:
                        messagebox(self, 'Entrada não é válida, usar números inteiros')
                        return
                    append = int(it.text())
                elif data == float:
                    if it.hasAcceptableInput() == False:
                        messagebox(self, 'Entrada não é válida, usar números decimais')
                        return
                    append = float(it.text())
                elif type(data) == list:
                    text = it.text()
                    for i,t in enumerate(data):
                        if text == t:
                            append = i+1
            else:
                if item.isModified() == False:
                    messagebox(self, 'Por favor preencher todos os campos')
                    return
                append = item.text()
            output.append(append) 
        self.signal.emit(output)
        print(output)
        self.close()


    def clearLayout(self):
        for i in reversed(range(self.lay.count())): 
            if type(self.lay.itemAt(i).widget()) == QLineEdit:
                self.lay.itemAt(i).widget().setText('')

def messagebox(lay, message):
    m= QMessageBox(lay)
    m.setText(message)
    m.exec_()
if __name__ == '__main__':
    #funcoesdb.populate()
    app = QApplication(sys.argv)
    app.setApplicationName("Controle de Estoque")
    window = MainWindow()
    
    app.exec_()