from models import *

@db_session
def populate():
    with open('src/names.txt') as f:
        for line in enumerate(f):
            addPaciente(line[1][:-1], 'Schrage{}'.format(line[0]))

    med = [addMedicamento(
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
# abstrations 

def iter_index(obj, i):
    itr = iter(obj)
    for e in range(i):
        next(itr)
    return next(itr)

queryAll = lambda obj: obj.select()
#------------
@db_session
def queryAllEntrada():
    for q in queryAll(Entrada):
        print(q.entradaDict())
@db_session
def queryAllMedicamento():
    for q in queryAll(Medicamento):
        print(q.medicamentoDict())

#------------------- adding elements -------------

@db_session
def addMedicamento(nome, estoque, dose, ratio, preco=0):
    q = Medicamento.get(nome=nome)
    if(q == None): 
        m = Medicamento(nome=nome)
        commit()
        addEstocagem(m.id, estoque, dose, ratio, preco)
        return m
    return q

@db_session
def addEstocagem(medicamento_id, estoque, dose, ratio, preco):
    return Estocagem(
        medicamento=Medicamento[medicamento_id],
        nomeEstoque=estoque, 
        nomeDose=dose, 
        ratioEstoque=ratio[0],
        ratioDose=ratio[1])

@db_session
def addPaciente(nome, sobrenome, cpf='111-111-111-11', info=''):
    q = Paciente.get(nome=nome, sobrenome=sobrenome)
    if(q): return q
    return Paciente(nome=nome, sobrenome=sobrenome, cpf=cpf, info=info)


@db_session
def addEntrada(med, estoque, data=datetime.now()):

    est = iter_index(med.estocagem, 0)

    ratioEstoque = est.ratioEstoque 
    ratioDose    = est.ratioDose
    est.estoque += ratioEstoque * estoque
    est.doses   += ratioDose * est.estoque

    commit()

    return Entrada(med=med, 
                   estoque=estoque, 
                   estoqueTipo=est.nomeEstoque,
                   data=data)

@db_session
def addSaida(med, paciente, doses, data=datetime.now()):
    t = med.estocagem.doses - doses
    t2 = med.estocagem.estoque 
    if(t <= 0): t2 -=1
    if(t2 < 0): t2 = 0

    med.estocagem.doses = t
    med.estocagem.estoque = t2
    commit()

    pac = Paciente.get(nome=paciente[0], sobrenome=paciente[1])
    if(pac == None): pac = Paciente(nome='Paciente', sobrenome='NaoEspecificado')
    return Saida(med=med, 
                pac=pac, 
                dosesTipo=med.estocagem.nomeDose,
                doses=doses, 
                data=data)

#populate()