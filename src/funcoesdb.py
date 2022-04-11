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
        'caixa', 'injetavel',1),
    addMedicamento(
        'Protocolo de Aumento de produção de serotonina',
        'caixa', 'injetavel',1),
    addMedicamento(
        'Protocolo de Ganho de massa',
        'caixa', 'injetavel',1),
    addMedicamento(
        'Complexo B',
        'caixa', 'pilula',9)]

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
#thats also the reason i made all those super complicated functions, so it looks nice
qAllMed = lambda : queryAllToDict(Medicamento)
qAllPac = lambda : queryAllToDict(Paciente)

changeMedName = {'objClass': Medicamento, 'field' : 'med'}
changePacName = {'objClass': Paciente,    'field' : 'pac'}
qAllEnt = lambda : queryAllToDict(Entrada, order=by_date, change=[changeMedName])
qAllSai = lambda : queryAllToDict(Saida,   order=by_date, change=[changeMedName,changePacName])

#------------------- editing elements -------------
@db_session
def editObj(obj, id, field, edit):
    o = obj.get(id=id)
    if(type(field) != str or o == None): return False
    d = {field:edit}
    o.set(**d)
    return True

eMedObj = lambda id, field, edit: editObj(Medicamento,id, field, edit)
ePacObj = lambda id, field, edit: editObj(Paciente,   id, field, edit)
eEntObj = lambda id, field, edit: editObj(Entrada,    id, field, edit)
eSaiObj = lambda id, field, edit: editObj(Saida,      id, field, edit) 
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
def addMedicamento(nome, embalagem, dose, ratio, preco=0):
    q = Medicamento.get(nomeMedicamento=nome)
    if(q == None): 
        Medicamento(
                nomeMedicamento=nome,
                nomeEmbalagem=embalagem, 
                nomeDose=dose, 
                ratioDose=ratio, 
                precoPorEmbalagem=preco)
        return True,'Medicamento adicionado'
    return False,   'Medicamento ja existe'

@db_session
def addPaciente(nome, sobrenome, cpf='111-111-111-11', info=''):
    q = Paciente.get(nome=nome, sobrenome=sobrenome)
    if(q == None): 
        Paciente(nome=nome, sobrenome=sobrenome, cpf=cpf, info=info)
        return True,'Paciente adicionado'
    return False,   'Paciente ja existe'

@db_session
def addEntrada(medId, embalagens, data=date.today()):

    med = Medicamento.get(id=medId)
    if(med == None): return False,"Medicamento nao existe"

    med.embalagens += embalagens
    med.doses      += med.ratioDose * med.embalagens 
    commit()
    

    Entrada(med=med, estoque=embalagens, 
            estoqueTipo=med.nomeEmbalagem,data=data)
    return True, "Tudo certo"

@db_session
def addSaida(medId, pacientId, doses, data=date.today()):
    print("fsaida")
    med = Medicamento.get(id=medId)
    pac = Paciente.get(id=pacientId)
    if(pac == None): return False,"Paciente nao existe"
    if(med == None): return False,"Medicamento nao existe"

    t = med.doses - doses
    t2 = med.embalagens 

    if(t <= 0): t2 -=1
    if(t2 < 0): t2 = 0

    med.doses = t
    med.embalagens = t2

    commit()
    Saida(med=med, pac=pac, dosesTipo=med.nomeDose,doses=doses, data=data)
    return True, "Tudo certo"
populate()