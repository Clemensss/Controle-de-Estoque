from array import array
from decimal import Decimal
from email.policy import default
from pony.orm import *
from datetime import date
import pony.orm.dbproviders.sqlite
DB_NAME= 'database.sqlite'

db = Database()
#-------------------------- DATA BASE ------------------------
class Medicamento(db.Entity):
    nomeMedicamento = Optional(str)

    ratioDose    = Optional(int)

    #quantidade e tipo de armazenamento
    nomeEmbalagem = Optional(str)
    embalagens = Optional(int, default=0)
    precoPorEmbalagem = Optional(float, default=0)
    #quantidade de dosagem
    nomeDose = Optional(str)
    doses = Optional(int, default=0)
    
    entrada   = Set(lambda: Entrada, cascade_delete=False)
    saida     = Set(lambda: Saida, cascade_delete=False)

    @db_session
    def deleteRelation(self):
        delete(e for e in Entrada if e.med.id == self.id)
        delete(s for s in Saida if s.med.id == self.id)
    @property
    def name(self):
        return self.nomeMedicamento

class Paciente(db.Entity):
    nome = Optional(str)
    sobrenome=Optional(str)
    cpf = Optional(str)
    info = Optional(LongStr)
    saida = Set(lambda: Saida, cascade_delete=False)

    @db_session
    def deleteRelation(self):
        delete(s for s in Saida if s.pac.id == self.id)

    @property
    def name(self):
        return ('{} {}'.format(self.nome, 
                              self.sobrenome))
    @property
    def nomeArr(self):
        return [self.nome,self.sobrenome]

class Saida(db.Entity):
    id = PrimaryKey(int, auto=True)
    med = Optional(Medicamento)
    pac = Optional(Paciente)
    dosesTipo = Optional(str)
    doses = Optional(int)
    data = Optional(date, default=date.today())

    def deleteRelation(self):
        return None
    def before_update(self):
        if self.med != None:
            dose = self.med.doses + self.doses 
            doseEmb = self.med.embalagens * self.med.ratioDose
            rest = doseEmb - dose
            if abs(rest) >= self.med.ratioDose:
                self.med.embalagens += rest // self.med.ratioDose
        
    def after_update(self):
        if self.med != None:
            dose = self.med.doses - self.doses 
            doseEmb = self.med.embalagens * self.med.ratioDose
            rest = doseEmb - dose
            if rest >= self.med.ratioDose:
                self.med.embalagens -= rest // self.med.ratioDose
            if self.med.doses < 0:
                self.med.doses = 0
                self.med.embalagens = 0
            if self.med.embalagens < 0:
                self.med.embalagens = 0

    def after_insert(self):
        if self.med != None:
            dose = self.med.doses - self.doses 
            doseEmb = self.med.embalagens * self.med.ratioDose
            rest = doseEmb - dose
            if rest >= self.med.ratioDose:
                self.med.embalagens -= rest // self.med.ratioDose
            self.med.doses = dose
            if self.med.doses < 0:
                self.med.doses = 0
                self.med.embalagens = 0
            elif self.med.embalagens < 0:
                self.med.embalagens = 0

    def before_delete(self):
        if self.med != None:
            dose = self.med.doses + self.doses 
            doseEmb = self.med.embalagens * self.med.ratioDose
            rest = doseEmb - dose
            if abs(rest) >= self.med.ratioDose:
                self.med.embalagens += rest // self.med.ratioDose
            self.med.doses = dose

class Entrada(db.Entity):
    id = PrimaryKey(int, auto=True)
    med = Optional(Medicamento)
    estoqueTipo = Optional(str)
    estoque = Optional(int)
    data = Optional(date, default=date.today())

    def deleteRelation(self):
        return None
    def before_update(self):
        if self.med != None:
            self.med.embalagens -= self.estoque
            self.med.doses -= self.estoque * self.med.ratioDose
            if self.med.embalagens < 0:
                self.med.embalagens = 0
            if self.med.doses < 0:
                self.med.doses = 0
        print('ENTRADA CHANGED')

    def after_update(self):
        if self.med != None:
            self.med.embalagens += self.estoque
            self.med.doses += self.estoque * self.med.ratioDose

    def after_insert(self):
        if self.med != None:
            self.med.embalagens += self.estoque
            self.med.doses += self.estoque * self.med.ratioDose
        print('ENTRADA INSERTED')

    def before_delete(self):
        if self.med != None:
            self.med.embalagens -= self.estoque
            self.med.doses -= self.estoque * self.med.ratioDose
            if self.med.embalagens < 0:
                self.med.embalagens = 0
            if self.med.doses < 0:
                self.med.doses = 0
        print('ENTRADA DELETED')

db.bind(provider='sqlite', filename=DB_NAME, create_db=True)
#db.bind(provider='sqlite', filename=':memory:')
db.generate_mapping(create_tables=True)

