from models import *
import random
@db_session
def populate():
    with open('src/names.txt') as f:
        for line in enumerate(f):
            addPaciente(line[1][:-1], 'Schrage{}'.format(line[0]))

    med = [
    addMedicamento(
        'Protocolo de Menopausa',
        'caixa', 'injetavel',(1,1)),
    addMedicamento(
        'Protocolo de Aumento de produção de serotonina',
        'caixa', 'injetavel',(1,1)),
    addMedicamento(
        'Protocolo de Ganho de massa',
        'caixa', 'injetavel',(1,1)),
    addMedicamento(
        'Complexo B',
        'caixa', 'pilula',(1,9))]

    for i in range(10):
        addEntrada(
            med[random.randint(0, len(med)-1)],
            random.randint(10, 30)
        )

#-----------------queries --------------------------------------------
@db_session
def queryAllToDict(obj, wc=False, ro=False):
    all = []
    for q in select(p for p in obj)[:]:
        print(q.to_dict(with_collections=wc, related_objects=ro))
    return all

qAllMed = lambda : queryAllToDict(Medicamento)
qAllPac = lambda : queryAllToDict(Paciente)
qAllEnt = lambda : queryAllToDict(Entrada, wc=True,ro=True)
qAllSai = lambda : queryAllToDict(Saida,wc=True,ro=True)

#------------------- editing elements -------------
@db_session
def editObj(obj, field, edit):
    obj.set({field:edit})

eMedObj = lambda field, edit: editObj(Medicamento, field, edit)
ePacObj = lambda field, edit: editObj(Paciente, field, edit)
eEntObj = lambda field, edit: editObj(Entrada,  field, edit)
eSaiObj = lambda field, edit: editObj(Saida,    field, edit) 
#------------------- deleting elements -------------
@db_session
def delObj(obj):
    obj.delete()

eMedObj = lambda field, edit: editObj(Medicamento, field, edit)
ePacObj = lambda field, edit: editObj(Paciente, field, edit)
eEntObj = lambda field, edit: editObj(Entrada,  field, edit)
eSaiObj = lambda field, edit: editObj(Saida,    field, edit) 

#------------------- adding elements -------------

@db_session
def addMedicamento(nome, embalagem, dose, ratio, preco=0):
    q = Medicamento.get(nomeMedicamento=nome)
    if(q == None): 
        q = Medicamento(
                nomeMedicamento=nome,
                nomeEmbalagem=embalagem, 
                nomeDose=dose, 
                ratioEmbalagem=ratio[0],
                ratioDose=ratio[1])
    return q 

@db_session
def addPaciente(nome, sobrenome, cpf='111-111-111-11', info=''):
    q = Paciente.get(nome=nome, sobrenome=sobrenome)
    if(q): return q
    return Paciente(nome=nome, sobrenome=sobrenome, cpf=cpf, info=info)


@db_session
def addEntrada(med, embalagens, data=datetime.now()):

    med.embalagens += med.ratioEmbalagem * embalagens
    med.doses      += med.ratioDose * med.embalagens 

    commit()

    return Entrada(med=med, 
                   estoque=embalagens, 
                   estoqueTipo=med.nomeEmbalagem,
                   data=data)

@db_session
def addSaida(med, paciente, doses, data=datetime.now()):
    t = med.doses - doses
    t2 = med.embalagens 
    if(t <= 0): t2 -=1
    if(t2 < 0): t2 = 0

    med.doses = t
    med.embalagens = t2
    commit()

    pac = Paciente.get(nome=paciente[0], sobrenome=paciente[1])
    if(pac == None): pac = Paciente(nome='Paciente', sobrenome='NaoEspecificado')
    return Saida(med=med, 
                pac=pac, 
                dosesTipo=med.nomeDose,
                doses=doses, 
                data=data)

#populate()