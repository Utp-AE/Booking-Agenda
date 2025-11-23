# backend/app/main.py
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas, auth


# Crear tablas al arrancar la app
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meeting Room Reservations API")

# CORS para que el frontend (localhost:3000) pueda llamar al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # si quieres, puedes limitar a ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========= USUARIOS =========

@app.post("/register", response_model=schemas.UserRead)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    hashed_pw = auth.get_password_hash(user_in.password)
    user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pw,
        is_admin=user_in.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # sub DEBE SER STRING
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ========= LÓGICA PARA EVITAR CHOQUES DE HORARIO (GLOBAL) =========

def check_reservation_conflict(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    exclude_reservation_id: Optional[int] = None,
):
    """
    Verifica si hay otra reserva en el calendario que se solape
    con el intervalo [start_time, end_time), sin importar el usuario.
    """
    query = db.query(models.Reservation).filter(
        models.Reservation.start_time < end_time,
        models.Reservation.end_time > start_time,
    )

    if exclude_reservation_id is not None:
        query = query.filter(models.Reservation.id != exclude_reservation_id)

    conflict = query.first()
    if conflict:
        raise HTTPException(
            status_code=400,
            detail=(
                "Ya existe una reserva en ese rango de tiempo. "
                "Por favor seleccione otro horario."
            ),
        )


# ========= RESERVAS =========

@app.post("/reservations", response_model=schemas.ReservationRead)
def create_reservation(
    reservation_in: schemas.ReservationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    # Si es admin y envía owner_id → crea para ese usuario
    # Si no, siempre crea para sí mismo
    if current_user.is_admin and reservation_in.owner_id is not None:
        owner_id = reservation_in.owner_id
    else:
        owner_id = current_user.id

    check_reservation_conflict(
        db=db,
        start_time=reservation_in.start_time,
        end_time=reservation_in.end_time,
    )

    reservation = models.Reservation(
        title=reservation_in.title,
        description=reservation_in.description,
        start_time=reservation_in.start_time,
        end_time=reservation_in.end_time,
        owner_id=owner_id,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@app.get("/reservations", response_model=List[schemas.ReservationRead])
def list_reservations(
    mine: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    - Si mine = true → siempre muestra solo las reservas del usuario actual.
    - Si mine = false → si es admin, ve todas; si no, igual se limita a las suyas.
    """
    query = db.query(models.Reservation)

    if mine or not current_user.is_admin:
        query = query.filter(models.Reservation.owner_id == current_user.id)

    reservations = query.order_by(models.Reservation.start_time).all()
    return reservations


@app.put("/reservations/{reservation_id}", response_model=schemas.ReservationRead)
def update_reservation(
    reservation_id: int,
    reservation_in: schemas.ReservationBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    # Solo el dueño o el admin pueden editar
    if reservation.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No tiene permisos para modificar esta reserva.")

    check_reservation_conflict(
        db=db,
        start_time=reservation_in.start_time,
        end_time=reservation_in.end_time,
        exclude_reservation_id=reservation_id,
    )

    reservation.title = reservation_in.title
    reservation.description = reservation_in.description
    reservation.start_time = reservation_in.start_time
    reservation.end_time = reservation_in.end_time

    db.commit()
    db.refresh(reservation)
    return reservation


@app.delete("/reservations/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    # Solo el dueño o el admin pueden borrar
    if reservation.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar esta reserva.")

    db.delete(reservation)
    db.commit()
    return {"detail": "Reserva eliminada correctamente."}