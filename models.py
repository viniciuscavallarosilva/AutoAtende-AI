from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


def agora_utc():
    return datetime.now(timezone.utc)


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    telefone = Column(String(30), unique=True, nullable=True)
    criado_em = Column(DateTime(timezone=True), default=agora_utc)

    conversas = relationship("Conversa", back_populates="cliente")
    agendamentos = relationship("Agendamento", back_populates="cliente")


class Conversa(Base):
    __tablename__ = "conversas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    status = Column(String(30), default="aberta")
    iniciada_em = Column(DateTime(timezone=True), default=agora_utc)

    cliente = relationship("Cliente", back_populates="conversas")
    mensagens = relationship("Mensagem", back_populates="conversa")


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    conversa_id = Column(Integer, ForeignKey("conversas.id"), nullable=False)
    papel = Column(String(20), nullable=False)
    conteudo = Column(Text, nullable=False)
    criada_em = Column(DateTime(timezone=True), default=agora_utc)
    resposta_id = Column(String(255), nullable=True)

    conversa = relationship("Conversa", back_populates="mensagens")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    veiculo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    data_hora = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="pendente")
    criado_em = Column(DateTime(timezone=True), default=agora_utc)

    cliente = relationship("Cliente", back_populates="agendamentos")
