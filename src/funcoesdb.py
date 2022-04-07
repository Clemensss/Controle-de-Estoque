from models import *

def populate():
    with open('src/names.txt') as f:
        count = 0
        for line in f:
            addPac(line[:-1], 'Schrage', str(count))
            count+=1

    addMed('ampola glutationa', 10)
    addMed('ampola curcumina', 10)

    for i in range(10):
        addEntrada(('ampola curcumina'),random.randint(5,20))
# --------- abstrations --------------
def query(obj,func=lambda o:o):
    return obj.select(e for e in obj).filter(func)

def queryAllDict(obj):
    for el in query(obj):
        print(el)

@db_session
def queryPacientes():
    queryAllDict(Paciente)

@db_session
def addMed(nome, quan, arma='caixa', dosagem='1 mg',preco=0):
    q = Medicamento.get(nome=nome)
    if(q): return q
    return Medicamento(nome=nome, quan=quan, arma=arma, dosagem=dosagem,preco=preco)

@db_session
def addPac(nome, sobrenome, cpf, info=''):
    q = Paciente.get(nome=nome, sobrenome=sobrenome)
    if(q): return q
    return Paciente(nome=nome, sobrenome=sobrenome, cpf=cpf, info=info)

@db_session
def addEntrada(medicamento, quan, data=datetime.now()):
    med = Medicamento.get(nome=medicamento)
    med.quan += quan
    commit()

    return Entrada(med=med, quan=quan, data=data)

@db_session
def addSaida(medicamento, paciente, quan, data=datetime.now()):
    med = Medicamento.get(nome=medicamento)
    med.quan -= quan
    commit()

    pac = Paciente.get(nome=paciente[0], sobrenome=paciente[1])

    return Saida(med=med, pac=pac, quan=quan, data=data)


#if __name__ == '__main__':
    #populate()