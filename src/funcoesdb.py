from models import *
import random
@db_session
def populate():
    names = 0
    with open('src/names.txt') as f:
        for line in enumerate(f):
            addPaciente(line[1][:-1], 'Schrage{}'.format(line[0]))
            names+=1

    commit()
    med = [
    addMedicamento(
        'Protocolo de Menopausa',
        'caixa', 'injetavel',1,0),
    addMedicamento(
        'Protocolo de Aumento de produção de serotonina',
        'caixa', 'injetavel',1,0),
    addMedicamento(
        'Protocolo de Ganho de massa',
        'caixa', 'injetavel',1,0),
    addMedicamento(
        'Complexo B',
        'caixa', 'pilula',9,0)]

    commit()
    for i in range(10):
        addEntrada(
            random.randint(1, len(med)),
            random.randint(10, 30), data='2022-04-{}'.format(random.randint(1,30))
        )
    
    commit()

    for i in range(10):
        addSaida(
            random.randint(1, len(med)), 
            random.randint(1, names), 
            random.randint(1, 5), data='2022-04-{}'.format(random.randint(1,30))
        )

class dbInterface:
    def __init__(self, objType, delFunc, addFunc, editFunc, getFunc):
        self.undoList = []
        self.cache = []
        self.objType = objType
        self.addFunc=addFunc
        self.editFunc=editFunc
        self.delFunc=delFunc
        self.getFunc=getFunc

    @db_session
    def delete(self, id):
        current = self.getFunc(id)
        if(self.delFunc(id)):
            self.undoList.append({'type': 'add', 
                'obj' : current.to_dict(exclude='id', with_collections=True)})

    def add(self, args):
        id = self.addFunc(*args)
        self.undoList.append({'type': 'del', 'obj' : id})

    @db_session
    def edit(self, id, dict):
        current = self.getFunc(id)

        self.undoList.append({'type': 'edit', 
            'obj' : current.to_dict(with_collections=True)})

        self.editFunc(id, dict)

    @db_session
    def undoRedo(self,p):
        obj = p['obj']
        prev = self.getFunc(obj.id)
        tipo = p['type']

        if  tipo == 'edit':
            id = obj['id']
            newDict = obj.pop('id',None)
            self.editFunc(id, newDict)

        elif tipo == 'del':
            self.delFunc(obj['id'])

        elif tipo == 'add':
            args = [None for _ in range(10)]
            newId = self.addFunc(*args) 
            self.editFunc(newId, obj)

    def undo(self):
        if self.undoing != []:
            p = self.undoing.pop()
            
    def redo_h(self,p):
        if p[1] == 'edit':
            self.editFunc(*(p[0])) 
        elif p[1] == 'del':
            self.addFunc(*(p[0])) 
        elif p[1] == 'add':
            self.delFunc(*(p[0])) 
    def redo(self):
        if self.cache != []:
            p = self.cache.pop()
        


#-----------------queries --------------------------------------------
#abstractions
@db_session
def changeName(d, *args):
    for el in args:
        d[el] = d[el].name
    return d

@db_session
def queryAll(obj, order=None):
    return select(p for p in obj).order_by(order)[:]

#this is surely the dumbest thing ive ever done but it was a lot of fun and tendinitis
#creates dicts from queries, substitus name of entity when asked
@db_session
def changeNameDict(change, queryDict, field, objclass):
    for d in change:
        objIdQuery, objClass = queryDict[d[field]], d[objclass]

        obj = objClass.get(id=objIdQuery) #query
        queryDict[d[field]] = obj.name    #changes name
    return queryDict

@db_session
def queryAllToDict(obj, order=None, change=None):
        arr = []
        query = queryAll(obj, order)
        for q in query:
            queryDict = q.to_dict(with_collections=(change != None))
            if(change!= None): 
                queryDict = changeNameDict(change, queryDict, 'field', 'objClass')
            arr.append(queryDict)
        return arr

#change field obj to str with the name
by_date = lambda o : o.data

#queries

@db_session
def getAllMedNames():
    l = []
    for i in Medicamento.select().order_by(lambda i : desc(i.id)):
        l.append(i.name)
    return l
@db_session
def getAllPacNames():
    l = []
    for i in Paciente.select().order_by(lambda i : desc(i.id)):
        l.append(i.name)
    return l

@db_session
def getObj(obj, id):
    o = obj.get(id=id)
    if(o == None): 
        return False
    return o

gMedObj = lambda id: getObj(Medicamento, id)
gPacObj = lambda id: getObj(Paciente,   id)
gEntObj = lambda id: getObj(Entrada,    id)
gSaiObj = lambda id: getObj(Saida,       id)

#thats also the reason i made all those super complicated functions, so it looks nice
qAllMed = lambda : queryAllToDict(Medicamento)
qAllPac = lambda : queryAllToDict(Paciente)
qAllEnt = lambda : queryAllToDict(Entrada, order=by_date)
qAllSai = lambda : queryAllToDict(Saida,   order=by_date)

changeMedName = {'objClass': Medicamento, 'field' : 'med'}
changePacName = {'objClass': Paciente,    'field' : 'pac'}
qAllChangeEnt = lambda : queryAllToDict(Entrada, order=by_date, change=[changeMedName])
qAllChangeSai = lambda : queryAllToDict(Saida,   order=by_date, change=[changeMedName,changePacName])

#------------------- editing elements -------------
@db_session
def editObj(obj, id, d):
    o = obj.get(id=id)
    if(o == None): return False
    o.set(**d)
    return True

eMedObj = lambda id, dict: editObj(Medicamento,id, dict)
ePacObj = lambda id, dict: editObj(Paciente,   id, dict)
eEntObj = lambda id, dict: editObj(Entrada,    id, dict)
eSaiObj = lambda id, dict: editObj(Saida,      id, dict) 
#------------------- deleting elements -------------
@db_session
def delObj(obj,id):
    o = obj.get(id=id)
    if(o == None): return False
    o.delete()
    return True

dMedObj = lambda id: delObj(Medicamento,id)
dPacObj = lambda id: delObj(Paciente   ,id)   
dEntObj = lambda id: delObj(Entrada    ,id)     
dSaiObj = lambda id: delObj(Saida      ,id)        

#------------------- adding elements -------------

@db_session
def addMedicamento(nome, embalagem, dose, ratio, preco):
    q = Medicamento.get(nomeMedicamento=nome)
    if(q == None): 
        obj = Medicamento(
                nomeMedicamento=nome,
                nomeEmbalagem=embalagem, 
                nomeDose=dose, 
                ratioDose=ratio, 
                precoPorEmbalagem=preco)
        return obj.id
    return None 

@db_session
def addPaciente(nome, sobrenome, cpf='111-111-111-11', info=''):
    q = Paciente.get(nome=nome, sobrenome=sobrenome)
    if(q == None): 
        obj = Paciente(nome=nome, sobrenome=sobrenome, cpf=cpf, info=info)
        return obj.id
    return None 

@db_session
def addEntrada(medId, embalagens, data=date.today()):

    med = Medicamento.get(id=medId)
    if(med == None): return None 

    med.embalagens += embalagens
    med.doses      += med.ratioDose * med.embalagens 
    commit()
    

    obj = Entrada(med=med, estoque=embalagens, 
            estoqueTipo=med.nomeEmbalagem,data=data)
    return obj.id

@db_session
def addSaida(medId, pacientId, doses, data=date.today()):
    print("fsaida")
    med = Medicamento.get(id=medId)
    pac = Paciente.get(id=pacientId)
    if(pac == None or med == None): return None

    t = med.doses - doses
    t2 = med.embalagens 

    if(t <= 0): t2 -=1
    if(t2 < 0): t2 = 0

    med.doses = t
    med.embalagens = t2

    commit()
    obj = Saida(med=med, pac=pac, dosesTipo=med.nomeDose,doses=doses, data=data)
    return obj.id

populate()