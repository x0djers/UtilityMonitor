from datetime import datetime, timedelta, timezone

from core.database import get_session, init_db
from core.models import (
    Device,
    DeviceModel,
    IncidentType,
    ResourceType,
    Room,
    SeverityEnum,
    TariffPlan,
    WorkType,
)


def seed_data() -> None:
  """Заполняет базу данных тестовыми справочниками и приборами учета."""
  now = datetime.now(timezone.utc)

  with get_session() as session:
    if session.query(ResourceType).count() > 0:
      print("Справочники уже заполнены, генерация пропущена.")
      return

    water_cold = ResourceType(name="Холодная вода", unit="м³")
    water_hot = ResourceType(name="Горячая вода", unit="м³")
    electricity = ResourceType(name="Электроэнергия", unit="кВт·ч")
    session.add_all([water_cold, water_hot, electricity])
    session.flush()

    tariffs = [
        TariffPlan(resource_type_id=water_cold.id, tariff=42.50),
        TariffPlan(resource_type_id=water_hot.id, tariff=185.00),
        TariffPlan(resource_type_id=electricity.id, tariff=5.40),
    ]
    session.add_all(tariffs)

    model_water = DeviceModel(
        manufacturer="Пульсар",
        name="ПУ-15",
        resource_type_id=water_cold.id,
        lifespan=72,
    )
    model_hot_water = DeviceModel(
        manufacturer="Бетар",
        name="СГВ-15",
        resource_type_id=water_hot.id,
        lifespan=48,
    )
    model_elec = DeviceModel(
        manufacturer="Меркурий",
        name="201.8",
        resource_type_id=electricity.id,
        lifespan=120,
    )
    session.add_all([model_water, model_hot_water, model_elec])
    session.flush()

    room_kitchen = Room(name="Кухня", area=14.5)
    room_bath = Room(name="Санузел", area=5.2)
    room_hall = Room(name="Прихожая / Щитовая", area=7.8)
    session.add_all([room_kitchen, room_bath, room_hall])
    session.flush()

    devices = [
        Device(
            room_id=room_kitchen.id,
            model_id=model_water.id,
            install_date=now - timedelta(days=365),
        ),
        Device(
            room_id=room_bath.id,
            model_id=model_hot_water.id,
            install_date=now - timedelta(days=240),
        ),
        Device(
            room_id=room_hall.id,
            model_id=model_elec.id,
            install_date=now - timedelta(days=500),
        ),
    ]
    session.add_all(devices)

    inc_types = [
        IncidentType(
            name="Умеренная аномалия расхода", severity=SeverityEnum.WARNING
        ),
        IncidentType(
            name="Критическая утечка / авария", severity=SeverityEnum.CRITICAL
        ),
        IncidentType(
            name="Информационное уведомление", severity=SeverityEnum.INFO
        ),
    ]
    session.add_all(inc_types)

    work_types = [
        WorkType(
            name="Поверка прибора",
            description="Плановая метрологическая поверка счетчика.",
        ),
        WorkType(
            name="Замена элемента питания",
            description="Замена литиевой батареи модуля передачи данных.",
        ),
        WorkType(
            name="Осмотр и очистка фильтра",
            description="Профилактическая очистка сетчатого фильтра.",
        ),
    ]
    session.add_all(work_types)

    session.commit()
    print("База данных успешно инициализирована и "
          "заполнена тестовыми данными.")


def main() -> None:
  init_db()
  seed_data()


if __name__ == "__main__":
  main()