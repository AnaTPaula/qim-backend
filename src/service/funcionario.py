import logging

from config import get_config
from controller.api_helper import ApiError
from model.model import Funcionario, Usuario


def find(empresa_id: str):
    session = get_config().get_session()
    try:
        items = session.query(Funcionario).filter_by(empresa_fk=empresa_id).all()
        return [item.serialize for item in items]
    except Exception as ex:
        logging.error(ex)
        raise ApiError()
    finally:
        session.close()


def get_item(empresa_id: str, funcionario_id: int):
    session = get_config().get_session()
    try:
        item = session.query(Funcionario).filter_by(empresa_fk=empresa_id, usuario_fk=funcionario_id).first()
        return item.serialize if item else {}
    except Exception as ex:
        logging.error(ex)
        raise ApiError()
    finally:
        session.close()


def create(body: dict):
    session = get_config().get_session()
    try:
        usuario = Usuario(tipo='funcionario')
        usuario.set_hash_password(senha=body['senha'])
        session.add(usuario)
        session.commit()
    except Exception as ex:
        logging.error(ex)
        session.rollback()
        session.close()
        raise ApiError()
    try:
        item = Funcionario(usuario_fk=usuario.id,
                           nome_usuario=body['nomeUsuario'],
                           acesso=body['acesso'],
                           empresa_fk=body['empresaId'])
        session.add(item)
        session.commit()
        return item.serialize
    except Exception as ex:
        logging.error(ex)
        session.rollback()
        session.delete(usuario)
        session.commit()
        raise ApiError()
    finally:
        session.close()


def update(body: dict):
    session = get_config().get_session()
    try:
        item = session.query(Funcionario).filter_by(empresa_fk=body['empresaId'], usuario_fk=body['id']).first()
        item.nome_usuario = body['nomeUsuario']
        item.acesso = body['acesso']
        if body.get('senha'):
            item.usuario.set_hash_password(senha=body['senha'])
        session.add(item)
        session.commit()
        return item.serialize
    except Exception as ex:
        logging.error(ex)
        session.rollback()
        raise ApiError()
    finally:
        session.close()


def remove(empresa_id: str, funcionario_id: int):
    session = get_config().get_session()
    try:
        item = session.query(Funcionario).filter_by(empresa_fk=empresa_id, usuario_fk=funcionario_id).first()
        usuario = session.query(Usuario).filter_by(id=funcionario_id).first()
        if item and usuario:
            session.delete(usuario)
            session.commit()
        return item
    except Exception as ex:
        logging.error(ex)
        session.rollback()
        raise ApiError()
    finally:
        session.close()
