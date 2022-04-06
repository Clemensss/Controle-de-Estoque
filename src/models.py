from array import array
from email.policy import default
import random
from unicodedata import decimal
from pony.orm import *
from datetime import datetime


db = Database()
#---------------------------funcoes-------------

#-----------------misc ---------------------
def printDBDict(obj):
    def pdict(d):
            for name,thing in d.items():
                print('{}:{}'.format(name,thing), end=' ')
            print('\n')

    if(type(obj) == array): 
        for i in obj: pdict(i)
    else: pdict(obj)
        

#-----------------queries --------------------------------------------

#queries returning big dicts
@db_session
def retEntradas(func=lambda o:o):
    todasEntradas = []
    query = select(e for e in Entrada).filter(func)
    for e in query:
        todasEntradas.append(
            {
                'quan' : e.quan,
                'med' : retMedAtt(e.med.id),
                'data' : e.date
            }
        )
    return todasEntradas

@db_session
def retSaidas(func=lambda o:o):
    todasSaidas = []
    query = select(e for e in Saida).filter(func)
    for e in query:
        todasSaidas.append({}
                'quan' : e.quan,
                'med' : retMedAtt(e.med.id),
                'pac' : retPacAtt(e.pac.id),
                'data' : e.date
        )
    return todasSaidas

@db_session
def retTodosMedicamentos():
    todosMedicamentos = []
    for e in select(e for e in Medicamento):
        todosMedicamentos.append(retMedAtt(e.id))
    return todosMedicamentos

@db_session
def retTodosPacientes():
    todosPaciente = []
    for e in select(e for e in Paciente):
        todosPaciente.append(retPacAtt(e.id))
    return todosPaciente

#functions that return single element queries
#todo
@db_session
def retMedAtt(id):
    med = Medicamento.get(id=id)
    return {
            'name': med.name,
            'quan': med.quan
            }

@db_session
def retPacAtt(id):
    pac = Paciente.get(id=id)
    return {
            'name': pac.name,
            'cpf': pac.cpf,
            'info' : pac.info
            }

@db_session
def retPac(name):
    return Paciente.get(name=name) 

@db_session
def retMed(name):
    return Medicamento.get(name=name) 
#------------------- editing element -------------
def editObj(obj, change, field):
    q = obj.
#------------------- adding elements -------------
@db_session
def addMed(name):
    q = Medicamento.get(name=name)
    if(q): return q
    return Medicamento.get(name=name)

@db_session
def addPac(nome, cpf):
    if(Paciente.exists(cpf=cpf) == False):
        return Paciente(nome=nome, cpf=cpf)
    return False

@db_session
def addEntrada(medicamento, quan, date=datetime.now()):
    med = Medicamento.get(tipo=medicamento[0], subs=medicamento[1])
    med.quan += quan
    commit()

    return Entrada(med=med, quan=quan, date=date)

@db_session
def addSaida(medicamento, paciente_cpf, quan, data=datetime.now()):
    med = Medicamento.get(tipo=medicamento[0], subs=medicamento[1])
    med.quan -= quan
    commit()

    pac = Paciente.get(cpf=paciente_cpf)

    return Saida(med=med, pac=pac, quan=quan, data=data)

# --------- abstrations --------------
def query(obj,att,func:lambda o:o):
    t = []
    for e in select(e for e in obj).filter(func):
        t.append((att))
    return t

#-------------------------- DATA BASE ------------------------
class Medicamento(db.Entity):
    id = PrimaryKey(int, auto=True)

    nome = Required(str)
    tipo = Required(str, default='')

    dosagem = Optional(str)
    preco   = Optional(decimal)

    quan = Required(int, default=0)
    entrada = Set('Entrada')
    saida = Set('Saida')

    @property
    def nomeCompleto(self):
        return ('{} {} {}'.format(
            self.nome, 
            self.tipo,
            self.dosagem))
    
    @property
    def retMedDict(self):
        return {
            'name': self.name, 
            'tipo': self.tipo,
            'quantidade': self.quan
            }

def queryAllDict(obj, d):
    return query(obj, d)
    

class Paciente(db.Entity):
    id = PrimaryKey(int, auto=True)
    nome = Required(str)
    sobrenome=Required(str)
    cpf = Required(str)
    info = Optional(LongStr)
    saida = Set('Saida')

    @property
    def nomeCompleto(self):
        return ('{} {}'.format(self.nome, self.sobrenome))
    @property
    def retPacDict(self):
        return {
            'name': self.name, 
            'cpf': self.tipo,
            'quantidade': self.quan
            }


class Saida(db.Entity):
    id = PrimaryKey(int, auto=True)
    quan = Required(int)
    med = Set(Medicamento)
    pac = Required(Paciente)
    data = Required(datetime)

class Entrada(db.Entity):
    id = PrimaryKey(int, auto=True)
    quan = Required(int)
    med = Set(Medicamento)
    date = Required(datetime)

    @property
    def entDict(self):
        return {
                'quan' : self.quan,
                'med' : self.med.id,
                'data' : self.date
            }

def retEntradas(func=lambda o:o):
    todasEntradas = []
    query = select(e for e in Entrada).filter(func)
    for e in query:
        todasEntradas.append(
        )
    return todasEntradas

@db_session
def retSaidas(func=lambda o:o):
    todasSaidas = []
    query = select(e for e in Saida).filter(func)
    for e in query:
        todasSaidas.append({}
                'quan' : e.quan,
                'med' : retMedAtt(e.med.id),
                'pac' : retPacAtt(e.pac.id),
                'data' : e.date
        )
    return todasSaidas

@db_session
@db_session
def retTodosPacientes():
    todosPaciente = []
    for e in select(e for e in Paciente):
        todosPaciente.append(retPacAtt(e.id))
    return todosPaciente

#functions that return single element queries
#todo
@db_session
def retMedAtt(id):
    med = Medicamento.get(id=id)
    return {
            'name': med.name,
            'quan': med.quan
            }

@db_session
def retPacAtt(id):
    pac = Paciente.get(id=id)
    return {
            'name': pac.name,
            'cpf': pac.cpf,
            'info' : pac.info
            }

@db_session
def retPac(name):
    return Paciente.get(name=name) 

@db_session
def retMed(name):
    return Medicamento.get(name=name) 
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

def populate():
    with open('src/names.txt') as f:
        count = 0
        for line in f:
            addPac(line[:-1],str(count))
            count+=1

    addMed('ampola glutationa')
    addMed('ampola curcumina')

    for i in range(10):
        addEntrada(('ampola','curcumina'),random.randint(5,20))
