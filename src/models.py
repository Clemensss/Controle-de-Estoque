from array import array
from decimal import Decimal
from pony.orm import *
from datetime import date


db = Database()
#-------------------------- DATA BASE ------------------------
class Medicamento(db.Entity):
    nomeMedicamento = Required(str)

    ratioDose    = Required(int)

    #quantidade e tipo de armazenamento
    nomeEmbalagem = Required(str)
    embalagens = Required(int, default=0)
    precoPorEmbalagem = Optional(float, default=0)
    #quantidade de dosagem
    nomeDose = Required(str)
    doses = Required(int, default=0)
    
    entrada   = Set(lambda: Entrada)
    saida     = Set(lambda: Saida)

    @property
    def name(self):
        return self.nomeMedicamento

class Paciente(db.Entity):
    nome = Required(str)
    sobrenome=Required(str)
    cpf = Optional(str)
    info = Optional(LongStr)
    saida = Set('Saida')

    @property
    def name(self):
        return ('{} {}'.format(self.nome, 
                              self.sobrenome))
    @property
    def nomeArr(self):
        return [self.nome,self.sobrenome]

class Saida(db.Entity):
    id = PrimaryKey(int, auto=True)
    med = Required(Medicamento)
    pac = Required(Paciente)
    dosesTipo = Required(str)
    doses = Required(int)
    data = Required(date)

class Entrada(db.Entity):
    id = PrimaryKey(int, auto=True)
    med = Required(Medicamento)
    estoqueTipo = Required(str)
    estoque = Required(int)
    data = Required(date)

#db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.bind(provider='sqlite', filename=':memory:')
db.generate_mapping(create_tables=True)

