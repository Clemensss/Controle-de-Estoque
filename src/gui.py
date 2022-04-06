from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
class MainPart:
    def __init__(self,pos):
        self.win = QMainWindow()
        self.initUI(pos) 
        self.currentPanel = ['Inicio']

    def initUI(self, pos):
        self.win.setGeometry(pos[0],pos[1],pos[2],pos[3])
        self.win.setWindowTitle("Controle de Estoque")

    def addLabel(self, name, pos):
        b = QLabel(self.win)
        b.setText(name)
        b.move(pos[0], pos[1])

    def changePanel(self,item):
        self.currentPanel=item
        print(self.currentPanel)

    def menuBar(self):
        self.win.statusBar() 
        toolbar = QToolBar(self.win)
        toolbar.setGeometry(50, 100, 300, 35)
        toolbar.move(0,0)
        items = ['&Inicio', '&Estoque', '&Entrada', '&Saida', '&Pacientes']
        arr = []
        for i in items:
            action = QAction(i, self.win)
            toolbar.setStatusTip('Ir para sessão de ' + i.lower())
            arr.append(action)

        print(arr) 

        arr[0].triggered.connect(lambda:self.changePanel(items[0]))
        arr[1].triggered.connect(lambda:self.changePanel(items[1]))
        arr[2].triggered.connect(lambda:self.changePanel(items[2]))
        arr[3].triggered.connect(lambda:self.changePanel(items[3]))
        arr[4].triggered.connect(lambda:self.changePanel(items[4]))
        toolbar.addAction(arr[0])
        toolbar.addAction(arr[1])
        toolbar.addAction(arr[2])
        toolbar.addAction(arr[3])
        toolbar.addAction(arr[4])



    def showUI(self):
        self.pacientTable = ShowPacients([500 for _ in range(4)], self.win, genPac())
        #self.menuBar()
        self.win.show()

def genPac():
        pacient_list = []
        with open('src/names.txt') as f:
            for _ in f:
                pacient_list.append(f.readline())
        return pacient_list
class ShowPacients():
    def __init__(self,pos, win, pacient_list):
        self.tableWidget = QTableWidget(win)
        self.tableWidget.setGeometry(pos[0],pos[1],pos[2],pos[3])
        self.pacients = pacient_list

        self.initTable() 

    def initTable(self):
        self.tableWidget.move(20,20)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(len(self.pacients))
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for p in enumerate(self.pacients):
            self.tableWidget.setItem(p[0], 0, QTableWidgetItem(p[1]))
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    size = 500
    m = MainPart([size for _ in range(4)])
    m.showUI()

    sys.exit(app.exec_())
    

    