from unittest.loader import VALID_MODULE_NAME
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from functools import cached_property
import sip
import funcoesdb
import sys

MINIMo = 5
ordemNomesEntrada = [
    ('med'        , 'Medicamento'),
    ('estoqueTipo', 'Tipo'),
    ('estoque'    , 'Entrada'),
    ('data'       , 'Data'),
]
ordemNomesSaida = [
    ('med'   , 'Medicamento'),
    ('pac'   , 'Paciente'),
    ('dosesTipo', 'Tipo'),
    ('doses' , 'Doses dadas'),
    ('data'  , 'Data'),
]
eqMedicamentos = [
   ('nomeMedicamento', 'Nome'),
   ('nomeEmbalagem', 'Tipo'),
   ('embalagens', 'Quantidade de embalagens'),
   ('nomeDose', 'Tipo' ),
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

        tabNames = ['Estoque','Entrada','Saida','Pacientes']
        tabs = [
            ListAndInfo(eqMedicamentos,1, funcoesdb.qAllMed()),
            TableEstoque(lambda: funcoesdb.qAllEnt(), ordemNomesEntrada),
            TableEstoque(lambda: funcoesdb.qAllSai(), ordemNomesSaida),
            ListAndInfo(eqPacientes, 2, funcoesdb.qAllPac())
        ]
        tabAddFunc = [
            lambda *args : funcoesdb.addMedicamento(*args),
            lambda *args : funcoesdb.addEntrada(*args),
            lambda *args : funcoesdb.addMedicamento(*args),
            lambda *args : funcoesdb.addMedicamento(*args)
        ]
        for i,n in enumerate(tabNames):
            tabwizard.addPage(Page(tabs[i],BUTTONS), n)

        self.show()


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
    def __init__(self, mWidget, buttons, parent=None):
        super().__init__(parent)

        #cache of changed objects
        self.cache = []
        
        lay = QVBoxLayout(self)
        self.popup=None
        lay.addWidget(mWidget)
        bs = QWidget()
        laybs = QHBoxLayout(bs)
        laybs.setAlignment(Qt.AlignLeft)
        laybs.setSpacing(100)
        for b in buttons:
            button = QPushButton(b)
            button.setObjectName(b)
            laybs.addWidget(button)
            button.clicked.connect(self.iClick)

        lay.addWidget(bs)

    def iClick(self):
        b = self.sender()
        print(b.objectName())
        dbData = funcoesdb.qAllEnt()
        self.popup = AdderPopUp(EntAddField, lambda x:x, 'Adicionar nova entrada', dbData)
        self.popup.signal.connect(lambda event: print(event))
        self.popup.exec_()

#name that appear on popup, query, validator
MedAddField = [
   ('Nome', None, None),
   ('Nome da Embalagem', None, None),
   ('Tipo de Dose', None, None),
   ('Quantas doses por embalagem', None, QDoubleValidator()),
   ('Preço por embalagem', None, QIntValidator()),
]

EntAddField = [
   ('Medicamento', 'med', None),
   ('Quandidade de Embalagens', None, QIntValidator()),
   ('Data de entrada', 'date', None),
]

#I truly hate gui
class AdderPopUp(QDialog):
    signal = pyqtSignal(list)
    def __init__(self, nameField, func, wName, dbData=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(wName)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.lay = QVBoxLayout(self)
        self.inputFields = []
        self.inputs = [] 
        self.nameField = nameField
        self.dbData = dbData
        self.genInputField()

    def genInputField(self):
        for fieldName,query,validator in self.nameField:
            self.lay.addWidget(QLabel(fieldName))
            self.genInputLine(validator, query)

        bWid = QWidget()
        bLay = QHBoxLayout(bWid)
        bSalvar   = QPushButton("Salvar")
        bCancelar = QPushButton("Cancelar")

        bLay.addWidget(bSalvar)
        bLay.addWidget(bCancelar)

        bSalvar.clicked.connect(self.saveClick) 
        bCancelar.clicked.connect(self.close)
        self.lay.addWidget(bWid)

    #gen qlineedit inputs, if there is a query
    # it will use to create a completer 
    # if query is set to 'date' it will create
    # a qdateedit field instead
    def genInputLine(self,validator, query):
        input = QLineEdit()

        if query != None:
            if query == 'date':
                input = self.genInputDate() 
            else:
                wordList = self.genInputOptions(query)
                completer = QCompleter(wordList, self)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                input.setCompleter(completer)

        if validator != None:
            input.setValidator(validator)


        self.lay.addWidget(input)
        self.inputFields.append(input)

    def genInputDate(self):
        dateInput = QDateEdit(QDate.currentDate())
        dateInput.setDisplayFormat('dd.MM.yyyy')
        dateInput.setCalendarPopup(True)
        return dateInput

    #creates options without duplicates
    def genInputOptions(self, query):
        if self.dbData != None:
            options = set()
            for dbDict in self.dbData:
                options.update([dbDict[query]])
            return list(options)
        return None

    
    def getInput(self):
        error, message = self.checkInput() 
        if error == False:
            for el in self.inputFields:
                input = None
                if type(el) == QLineEdit:
                    input = el.text()
                elif type(el) == QDateEdit:
                    date = el.date()
                    input = date.toPyDate()

                self.inputs.append(input)
        return error,message
    
    #check if qlineedit inputs are valid an
    def checkInput(self):
        error = False
        message = ''
        for el in enumerate(self.inputFields):
            m = ''
            if type(el) == QLineEdit:   
                if(el.hasAcceptableInput() == False):
                    m ='Valor de {} inválido\n'.format((self.nameField[i])[0])
                    error = True
                if(el.isModified() == False):
                    m='Valor de {} não preenchido\n'.format((self.nameField[i])[0])
                    error = True
            message += m        

        if(error == False):message = 'Sucesso!\n'
        return error, message

    def saveClick(self):
        error, message = self.getInput() 
        if(error):
            self.clearLayout()
            self.inputs, self.inputFields = [], []
        else:
            #self.signal.emit(self.inputs) 
            print(self.inputs)
        self.genMessageBox(message)  

    def genMessageBox(self,message):
        m = QMessageBox(self)
        m.setAttribute(Qt.WA_DeleteOnClose)
        m.setText(message)
        m.exec()

    def clearLayout(self):
        for i in reversed(range(self.lay.count())): 
            if type(self.lay.itemAt(i).widget()) == QLineEdit:
                self.lay.itemAt(i).widget().setText('')

#creates a table widget using a db query func and 
#a reference list of dicts as guide for the structure
class TableEstoque(QTableWidget):
    def __init__(self, dbFunc, dbNewNames, *args):
        QTableWidget.__init__(self, *args)
        self.dbData = dbFunc()
        self.dbNewNames = dbNewNames
        self.setColumnCount(len(dbNewNames))
        self.setRowCount(len(self.dbData))

        self.setHorizontalHeaderLabels([name for _, name in dbNewNames])
        self.setData()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)


    #takes output dich_db_entity and turn it into 
    #a table widget, referecing dbNewNames, for the
    #col order and row headers
    def setData(self):
        for col,(dbName,disName) in enumerate(self.dbNewNames):
            for row,dbItemDict in enumerate(self.dbData):
                tableName = str(dbItemDict[dbName])
                print(tableName)
                self.setItem(row,col,QTableWidgetItem(tableName))

class ListAndInfo(QWidget):
    def __init__(self, nameOrder, firstShow, dbData, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.nameOrder = nameOrder
        self.dbData = dbData
        self.firstShow = firstShow

        self.lay = QHBoxLayout(self)

        self.lista = Lista(self.nameOrder, firstShow, self.dbData)
        self.lay.addWidget(self.lista)
        self.info = None

        self.lista.clicked.connect(lambda event: self.showInfo(event))

    def showInfo(self, i):
        if(self.info != None):
            self.lay.removeWidget(self.info)
            sip.delete(self.info)
        self.info = Info(self.nameOrder, self.dbData[i.row()])
        self.lay.addWidget(self.info)
        self.info.move(self.maximumWidth()-20, self.maximumHeight() -20)

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

        self.itemClicked.connect(lambda:self.iClick())
        self.dbData = dbData

        for dbDict in dbData:
            l = ''
            for i in range(firstShow):
                dbData    = dbDict[nameOrder[i][0]]

                if dbData != None:
                    l += str(dbData)
                    if i+1 < firstShow: l+=' '
                
            self.addItem(QListWidgetItem(l))
            
    def iClick(self):
        listIndex = self.indexFromItem(self.currentItem())
        dbDict = self.dbData[listIndex.row()]
        self.signal.emit(dbDict)

if __name__ == '__main__':
    funcoesdb.populate()
    app = QApplication(sys.argv)
    app.setApplicationName("Controle de Estoque")
    window = MainWindow()
    
    app.exec_()