from array import array
from email.policy import default
import random
from decimal import Decimal
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
 
#------------------- editing element -------------
#def editObj(obj, change, field):
 #   q = obj.

#-------------------------- DATA BASE ------------------------
class Medicamento(db.Entity):
    nome = Required(str)

    #quantidade e tipo de armazenamento
    estocagem = Set(lambda: Estocagem)
    entrada   = Set(lambda: Entrada)
    saida     = Set(lambda: Saida)

    @property
    def medicamentoDict(self):
        return {
                'nome': self.nome,
                'nomeEstoque' : self.estocagem.nomeEstoque,
                'quantidadeEstoque': self.estocagem.estoque,
                'precoPorEstoque'  : self.estocagem.precoPorEstoque,
                'nomeDose': self.estocagem.nomeDose,
                'quantidadeDoses': self.estocagem.nomeDose
                }

class Estocagem(db.Entity):
    medicamento = Required(Medicamento)

    ratioEstoque = Required(int)
    ratioDose    = Required(int)

    #quantidade de items 
    nomeEstoque = Required(str)
    estoque = Required(int, default=0)
    precoPorEstoque = Required(int)

    #quantidade de dosagem
    nomeDose = Required(str)
    quantidadeDoses = Required(int, default=0)

    @property
    def ratio(self):
        return {'estoque': self.ratioEstoque,
                'dosagem': self.ratioDose}

class Paciente(db.Entity):
    nome = Required(str)
    sobrenome=Required(str)
    cpf = Optional(str)
    info = Optional(LongStr)
    saida = Set('Saida')

    @property
    def nomeCompleto(self):
        return ('{} {}, cpf: {}'.format(
                                self.nome, 
                                self.sobrenome,
                                self.cpf))

    @property
    def pacienteDict(self):
        return {
            'nome': self.nomeCompleto, 
            'cpf': self.cpf,
            'info': self.info
            }


class Saida(db.Entity):
    id = PrimaryKey(int, auto=True)
    med = Set(Medicamento)
    pac = Required(Paciente)
    quan = Required(int)
    data = Required(datetime)

    @property
    def saidaDict(self):
        return {
                'medicamento' : self.med.medicamentoDict,
                'paciente'    : self.pac.pacienteDict,
                'quantindade' : self.quan,
                'data' : self.date
            }

class Entrada(db.Entity):
    id = PrimaryKey(int, auto=True)
    quan = Required(int)
    med = Set(Medicamento)
    data = Required(datetime)

    @property
    def entradaDict(self):
        return {
                'quan' : self.quan,
                'med' : self.med.medicamentoDict,
                'data' : self.date
            }

#functions that return single element queries
#todo
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

