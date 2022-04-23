from models import *
import random
@db_session
def populate():
    names = 0
    with open('src/names.txt') as f:
        for line in enumerate(f):
            addPaciente(line[1][:-1], 'Schrage{}'.format(line[0]))
            names+=1

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
    def __init__(self, delFunc, delKids, addFunc,addEmptyFunc, editFunc, getFunc):
        self.undoList = []
        self.redoList = []
        self.addFunc=addFunc
        self.addEmptyFunc=addEmptyFunc
        self.editFunc=editFunc
        self.delFunc=delFunc
        self.delKids=delKids
        self.getFunc=getFunc

    @db_session
    def deleteWChildren(self,id):
        self.delKids(id)
    @db_session
    def delete(self, id):
        self.redoList = []
        current = self.getFunc(id)
        current = current.to_dict(with_collections=True)
        if(self.delFunc(id)):
            self.undoList.append({'type': 'add', 
                'obj' : current})

    @db_session
    def add(self, args):
        self.redoList = []
        id = self.addFunc(*args)
        self.undoList.append({'type': 'del', 'obj' : id})
        print('id {}'.format(id))

    @db_session
    def edit(self, id, dict):
        self.redoList = []
        current = self.getFunc(id)

        self.undoList.append({'type': 'edit', 
            'obj' : current.to_dict(with_collections=True)})

        self.editFunc(id, dict)

    @db_session
    def undoRedo(self,p):
        obj = p['obj']
        tipo = p['type']

        if  tipo == 'edit':
            id = obj['id']
            obj.pop('id',None)
            newDict = obj
            prev = self.getFunc(id)
            prev = prev.to_dict(with_collections=True)
            self.editFunc(id, newDict)
            return {'type' : 'edit',
                'obj' : prev}


        elif tipo == 'del':
            prev = self.getFunc(obj)
            prev = prev.to_dict(with_collections=True)
            self.delFunc(obj)
            return {'type' : 'add',
                'obj' : prev}

        elif tipo == 'add':
            self.addEmptyFunc(obj['id']) 
            newId = obj['id'] 
            obj.pop('id',None)
            self.editFunc(newId, obj)
            return {'type' : 'del', 'obj':newId}

    def undo(self):
        if self.undoList != []:
            p = self.undoList.pop()
            self.redoList.append(self.undoRedo(p))
            
    def redo(self):
        if self.redoList != []:
            p = self.redoList.pop()
            self.undoList.append(self.undoRedo(p))
        


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
        if obj != None:
            queryDict[d[field]] = obj.name    #changes name
        else:
            queryDict[d[field]] = 'Objeto não encontrado'    #changes name
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
by_date = lambda o : desc(o.data)

#queries

@db_session
def getAllMedNames():
    l = []
    for i in Medicamento.select().order_by(lambda i : i.id):
        l.append(i.name)
    return l
@db_session
def getAllPacNames():
    l = []
    for i in Paciente.select().order_by(lambda i : i.id):
        l.append(i.name)
    return l

@db_session
def getObj(obj, id):
    o = obj.get(id=id)
    if(o == None): 
        return None
    return o

gMedObj = lambda id: getObj(Medicamento, id)
gPacObj = lambda id: getObj(Paciente,   id)
gEntObj = lambda id: getObj(Entrada,    id)
gSaiObj = lambda id: getObj(Saida,       id)

#thats also the reason i made all those super complicated functions, so it looks nice
qAllMed = lambda : queryAllToDict(Medicamento)
qAllPac = lambda : queryAllToDict(Paciente, order=lambda c : c.nome)
qAllEnt = lambda : queryAllToDict(Entrada, order=by_date)
qAllSai = lambda : queryAllToDict(Saida,   order=by_date)

changeMedName = {'objClass': Medicamento, 'field' : 'med'}
changePacName = {'objClass': Paciente,    'field' : 'pac'}
qAllChangeEnt = lambda : queryAllToDict(Entrada, order=by_date, change=[changeMedName])
qAllChangeSai = lambda : queryAllToDict(Saida,   order=by_date, change=[changeMedName,changePacName])

#------------------- editing elements -------------
@db_session
def editObj(obj, id, d, query=None):
    o = obj.get(id=id)
    if(o == None): return False
    #get the objects if needed 
    if query != None and type(d) == dict:
        for key in d:
            if key in query:
                if type(d[key]) == list:
                    nv = [] 
                    for id in d[key]:
                        nv.append(query[key].get(id=id))
                    d[key] =nv
                else:
                        d[key] = query[key].get(id=d[key])

    o.set(**d)
    return True
QUERY_EDIT_MED = {'entrada':Entrada, 'saida':Saida}
eMedObj = lambda id, dict: editObj(Medicamento,id, dict,QUERY_EDIT_MED)
QUERY_EDIT_PAC = {'saida':Saida}
ePacObj = lambda id, dict: editObj(Paciente,   id, dict,QUERY_EDIT_PAC)
QUERY_EDIT_ENT = {'med':Medicamento,'pac':Paciente}
eEntObj = lambda id, dict: editObj(Entrada,    id, dict,QUERY_EDIT_ENT)
QUERY_EDIT_SAI = {'pac':Paciente}
eSaiObj = lambda id, dict: editObj(Saida,      id, dict,QUERY_EDIT_SAI)
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

def delKids(obj,id):
    o = obj.get(id=id)
    if(o == None): return False
    o.deleteRelation()
    return True

delKidsMed = lambda id: delKids(Medicamento,id)
delKidsPac = lambda id: delKids(Paciente   ,id)   
delKidsEnt = lambda id: delKids(Entrada    ,id)     
delKidsSai = lambda id: delKids(Saida      ,id)        
#------------------- adding elements -------------

@db_session
def addEmptyObj(obj, id):
    o = obj.get(id=id)
    if(o != None): return False
    o = obj(id=id)

aMedObj = lambda id: addEmptyObj(Medicamento,id)
aPacObj = lambda id: addEmptyObj(Paciente   ,id)   
aEntObj = lambda id: addEmptyObj(Entrada    ,id)     
aSaiObj = lambda id: addEmptyObj(Saida      ,id)        

@db_session
def addMedicamento(nome, embalagem, dose, ratio, preco):
    q = Medicamento.get(nomeMedicamento=nome)
    if(q == None): 
        obj = Medicamento(
                nomeMedicamento=nome.upper(),
                nomeEmbalagem=embalagem.upper(), 
                nomeDose=dose.upper(), 
                ratioDose=ratio, 
                precoPorEmbalagem=preco)
        commit()
        print(obj.id)
        return obj.id
    return None 

@db_session
def addPaciente(nome, sobrenome, cpf='111-111-111-11', info=''):
    q = Paciente.get(nome=nome, sobrenome=sobrenome)
    if(q == None): 
        obj = Paciente(nome=nome.upper(), sobrenome=sobrenome.upper(), cpf=cpf, info=info)
        commit()
        return obj.id
    return None 

@db_session
def addEntrada(medId, embalagens, data):

    med = Medicamento.get(id=medId)
    if(med == None): return None 

    
    obj = Entrada(med=med, estoque=embalagens, 
            estoqueTipo=med.nomeEmbalagem,data=data)
    commit()
    return obj.id

@db_session
def addSaida(medId, pacientId, doses, data):
    med = Medicamento.get(id=medId)
    pac = Paciente.get(id=pacientId)
    if(pac == None or med == None): return None

    obj = Saida(med=med, pac=pac, dosesTipo=med.nomeDose,doses=doses, data=data)
    commit()
    return obj.id
