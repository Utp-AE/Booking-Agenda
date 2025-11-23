# backend/app/deps.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from . import models


def check_no_overlap(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    exclude_reservation_id: int | None = None,
):
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de fin debe ser mayor que la hora de inicio.",
        )

    q = db.query(models.Reservation).filter(
        models.Reservation.start_time < end_time,
        models.Reservation.end_time > start_time,
    )
    if exclude_reservation_id:
        q = q.filter(models.Reservation.id != exclude_reservation_id)

    if db.query(q.exists()).scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una reserva en ese rango de tiempo (choque de horario).",
        )