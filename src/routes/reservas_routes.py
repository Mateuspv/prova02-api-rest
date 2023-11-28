import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")


@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas


@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )
        
        reserva_existente = session.exec(select(Reserva).where(Reserva.documento == reserva.documento)).first()

        if reserva_existente:
            return JSONResponse(
                content={"message": f"Já existe uma reserva para o documento {reserva.documento}."},
                status_code=400,
            )    

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


@reservas_router.post("/{id_reserva}/checkin/{num_poltrona}")
def faz_checkin(id_reserva: int, num_poltrona: int):
    with get_session() as session:
        
        reserva = session.exec(select(Reserva).where(Reserva.id == id_reserva)).first()

        if not reserva:
            return JSONResponse(
                status_code=404,
                content="Reserva não encontrada.",
            )

        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                status_code=404,
                detail="Voo não encontrado.",
            )  
        
        poltrona_field = f"poltrona_{num_poltrona}"

        if getattr(voo, poltrona_field) is None:
            setattr(voo, poltrona_field, reserva.codigo_reserva)
            session.commit()
            return {"message": "Check-in realizado com sucesso."}
        else:
            return JSONResponse(
            status_code=400,
            content=f"A poltrona {num_poltrona} já está ocupada.",
        )
             
@reservas_router.patch("/{id_reserva}/checkin/{num_poltrona}")
def faz_checkin(id_reserva: int, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(select(Reserva).where(Reserva.id == id_reserva)).first()

        if not reserva:
            return JSONResponse(
                status_code=404,
                content="Reserva não encontrada.",
            )

        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                status_code=404,
                detail="Voo não encontrado.",
            ) 

        poltrona_field = f"poltrona_{num_poltrona}"

        if getattr(voo, poltrona_field) is None:
            setattr(voo, poltrona_field, reserva.codigo_reserva)
            session.commit()
            return {"message": "Check-in realizado com sucesso."}
        else:
            return JSONResponse(
            status_code=400,
            content=f"A poltrona {num_poltrona} já está ocupada.",
        )