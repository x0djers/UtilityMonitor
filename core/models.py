import enum
from datetime import datetime, timezone

from sqlalchemy.types import Enum as SQLEnum
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SeverityEnum(enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class StatusEnum(enum.Enum):
    NEW = "NEW"
    IN_PROCESS = "IN_PROCESS"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[float | int] = mapped_column(Float, nullable=False)

    devices: Mapped[list["Device"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class ResourceType(Base):
    __tablename__ = "resource_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    device_models: Mapped[list["DeviceModel"]] = relationship(
        back_populates="resource_type"
    )
    tariff_plans: Mapped[list["TariffPlan"]] = relationship(
        back_populates="resource_type"
    )


class DeviceModel(Base):
    __tablename__ = "device_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type_id: Mapped[int] = mapped_column(
        ForeignKey("resource_types.id"), nullable=False
    )
    lifespan: Mapped[int] = mapped_column(Integer, nullable=False)

    resource_type: Mapped["ResourceType"] = relationship(
        back_populates="device_models"
    )
    devices: Mapped[list["Device"]] = relationship(back_populates="model")


class TariffPlan(Base):
    __tablename__ = "tariff_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_type_id: Mapped[int] = mapped_column(
        ForeignKey("resource_types.id"), nullable=False
    )
    tariff: Mapped[float | int] = mapped_column(Float, nullable=False)

    resource_type: Mapped["ResourceType"] = relationship(
        back_populates="tariff_plans"
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"),
                                         nullable=False)
    model_id: Mapped[int] = mapped_column(ForeignKey("device_models.id"),
                                          nullable=False)
    install_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(timezone.utc)
    )

    room: Mapped["Room"] = relationship(back_populates="devices")
    model: Mapped["DeviceModel"] = relationship(back_populates="devices")
    service_works: Mapped[list["ServiceWork"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )


class WorkType(Base):
    __tablename__ = "work_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_works: Mapped[list["ServiceWork"]] = relationship(
        back_populates="work_type"
    )


class ServiceWork(Base):
    __tablename__ = "service_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"),
                                           nullable=False)
    work_type_id: Mapped[int] = mapped_column(ForeignKey("work_types.id"),
                                              nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(timezone.utc)
    )

    device: Mapped["Device"] = relationship(back_populates="service_works")
    work_type: Mapped["WorkType"] = relationship(
        back_populates="service_works"
    )


class Measurement(Base):
    __tablename__ = "measurements"

    # Составной первичный ключ для TimescaleDB гипертаблицы
    time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"),
                                           primary_key=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    device: Mapped["Device"] = relationship(back_populates="measurements")


class IncidentType(Base):
    __tablename__ = "incident_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[SeverityEnum] = mapped_column(
        SQLEnum(SeverityEnum), nullable=False
    )

    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="incident_type"
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"),
                                           nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("incident_types.id"),
                                         nullable=False)
    detection_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    resolution_time: Mapped[datetime | None] = mapped_column(DateTime,
                                                             nullable=True)
    status: Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum), nullable=False, default=StatusEnum.NEW
    )

    device: Mapped["Device"] = relationship(back_populates="incidents")
    incident_type: Mapped["IncidentType"] = relationship(
        back_populates="incidents"
    )