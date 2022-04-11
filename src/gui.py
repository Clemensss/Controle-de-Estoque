from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from functools import cached_property
import sip
import funcoesdb
import sys

tabNames = ['Estoque','Entrada','Saida','Pacientes']
MINIMo = 5
ordemNomesEntrada = [
    {'med'        : 'Medicamento'}          ,
    {'estoqueTipo': 'Tipo'}                 ,
    {'estoque'    : 'Entrada'},
    {'data'       : 'Data'}                 
]
ordemNomesSaida = [
    {'med'   : 'Medicamento'},
    {'pac'   : 'Paciente'},
    {'dosesTipo': 'Tipo'},
    {'doses' : 'Doses dadas'},
    {'data'  : 'Data'}
]
eqMedicamentos = [
   ('nomeMedicamento', 'Nome'),
   ('embalagens', 'Quantidade de embalagens'),
   ('nomeEmbalagem', 'Tipo'),
   ('precoPorEmbalagem', 'Preço'),
   ('nomeDose', 'Tipo' ),
   ('doses', 'Quantidade de doses')
]
eqPacientes = [
   ('nome', 'Nome'),
   ('sobrenome', 'Sobrenome'),
   ('cpf', 'CPF' ),
   ('info', 'Informações adicionais')
]
BUTTONS = ["Adicionar", 'Editar', 'Deletar']
class  MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Controle de Estoque")
        #self.showMaximized()

        tabwizard = TabWizard()
        self.setCentralWidget(tabwizard)
        tabs = [
            ListAndInfo(eqMedicamentos,1, funcoesdb.qAllMed()),
            TableEstoque(lambda: funcoesdb.qAllEnt(), ordemNomesEntrada),
            TableEstoque(lambda: funcoesdb.qAllSai(), ordemNomesSaida),
            ListAndInfo(eqPacientes, 2, funcoesdb.qAllPac())
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
            button.clicked.connect(lambda event:self.iClick(button.objectName()))

        lay.addWidget(bs)

    def iClick(self, event):
        print(event)
        self.popup = AdderPopUp(MedAddField, 'Adicionar novo medicamento')
        self.popup.signal.connect(lambda event: print(event))
        self.popup.exec_()

MedAddField = [
    ("Nome", None),
    ("Tipo de Embalagem", None),
    ("Tipo de Dosagem", None),
    ("Preco por Embalagem", QDoubleValidator()),
    ("Quantas doses por embalagem", QIntValidator()),
]

#I truly hate gui
class AdderPopUp(QDialog):
    signal = pyqtSignal(list)
    def __init__(self, objField, wName, parent=None):
        super().__init__(parent)

        self.setWindowTitle(wName)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.lay = QVBoxLayout(self)
        self.fields = [] 
        self.objField = objField

        self.genInput()
        
    def clearLayout(self):
        for i in reversed(range(self.lay.count())): 
            if type(self.lay.itemAt(i).widget()) == QLineEdit:
                self.lay.itemAt(i).widget().setText('')

    def genInput(self):
        for name,val in self.objField:
            self.lay.addWidget(QLabel(name))
            line = QLineEdit()
            
            if val != None:
                line.setValidator(val)
            self.lay.addWidget(line)

            self.fields.append(line)

        bWid = QWidget()
        bLay = QHBoxLayout(bWid)
        buttons=QPushButton("Salvar"), QPushButton("Cancelar")

        for b in buttons: 
            bLay.addWidget(b)

        buttons[0].clicked.connect(self.saveClick) 
        buttons[1].clicked.connect(self.close)
        self.lay.addWidget(bWid)

    def saveClick(self):
        message = ''
        error = False
        for i in range(len(self.objField)):
            m=''
            if(self.fields[i].hasAcceptableInput() == False):
                m ='Valor de {} inválido\n'.format((self.objField[i])[0])
                error = True
            if(self.fields[i].isModified() == False):
                m='Valor de {} não preenchido\n'.format((self.objField[i])[0])
                error = True
            message += m
        if(error):
            self.clearLayout()
            er = QMessageBox(self)
            er.setAttribute(Qt.WA_DeleteOnClose)
            er.setText(message)
            er.exec()
            
        else:
            self.signal.emit([i.text() for i in self.fields])
            




#creates a table widget using a db query func and 
#a reference list of dicts as guide for the structure
class TableEstoque(QTableWidget):
    def __init__(self, dbFunc, dbNewNames, *args):
        QTableWidget.__init__(self, *args)
        self.dbData = dbFunc()
        self.dbNewNames = dbNewNames
        self.setColumnCount(len(dbNewNames))
        self.setRowCount(len(self.dbData))

        self.setHorizontalHeaderLabels([[v for _,v in i.items()][0] for i in dbNewNames])
        self.setData()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)


    #takes output dich_db_entity and turn it into 
    #a table widget, referecing dbNewNames, for the
    #col order and row headers
    def setData(self):
        for c,d in enumerate(self.dbNewNames):
            dbName = [v for v,_ in d.items()][0]
            for r,dbItemDict in enumerate(self.dbData):
                print(str(dbItemDict[dbName]))
                tItem = QTableWidgetItem(str(dbItemDict[dbName]))
                self.setItem(r,c, tItem)

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
        for names in nameOrder:
            if names[0] in dbDict:
                dbData, dataName = dbDict[names[0]], names[1]
                l = '{}: {}\n'.format(dataName, dbData)
                info += l
        self.label = QLabel(info, self)
        self.label.resize(200,200)
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
                dbName, dataName = dbDict[nameOrder[i][0]], nameOrder[i][1]
                if dbName != None:
                    l += str(dbName)
                    if i+1 < firstShow: l+=' '
                
            self.addItem(QListWidgetItem(l))
            
    def iClick(self):
        i = self.indexFromItem(self.currentItem())
        d = self.dbData[i.row()]
        self.signal.emit(d)

if __name__ == '__main__':
    funcoesdb.populate()
    app = QApplication(sys.argv)
    app.setApplicationName("Controle de Estoque")
    window = MainWindow()
    
    app.exec_()