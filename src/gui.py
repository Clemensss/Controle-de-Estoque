from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import funcoesdb
import sys
ordemNomesEntrada = [
    {'med'        : 'Medicamento'}          ,
    {'estoqueTipo': 'Tipo'}                 ,
    {'estoque'    : 'Entrada'},
    {'data'       : 'Data'}                 
]
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Controle de Estoque")
        self.dbq = funcoesdb.qAllEnt()
        print(self.dbq)
        self.entrada = TableEstoque(self.dbq, ordemNomesEntrada)
        self.setCentralWidget(self.entrada) 
        self.show()

class TableEstoque(QTableWidget):
    def __init__(self, dbData, dbNewNames, *args):
        QTableWidget.__init__(self, *args)
        self.dbData = dbData
        self.dbNewNames = dbNewNames
        self.setColumnCount(len(dbNewNames))
        self.setRowCount(len(dbData))

        self.setHorizontalHeaderLabels([[v for _,v in i.items()][0] for i in dbNewNames])
        self.setData()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def setData(self):
        for c,d in enumerate(self.dbNewNames):
            dbName = [v for v,_ in d.items()][0]
            for r,dbItemDict in enumerate(self.dbData):
                print(str(dbItemDict[dbName]))
                tItem = QTableWidgetItem(str(dbItemDict[dbName]))
                self.setItem(r,c, tItem)
        
if __name__ == '__main__':
    funcoesdb.populate()
    app = QApplication(sys.argv)
    app.setApplicationName("Controle de Estoque")
    window = MainWindow()
    
    app.exec_()