from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, make_transient
from database import Base
from models import (
    User, Actor, Film, Genre, Country,
    Link, Feedback, GenreFilm, ActorFilm, FilmList
)

# Настройка путей
engine_src = create_engine('sqlite:///database___')
engine_dst = create_engine('sqlite:///database___.db')

SessionSrc = sessionmaker(bind=engine_src)
SessionDst = sessionmaker(bind=engine_dst)


def migrate():
    # Создаем таблицы в новой базе, если их нет
    Base.metadata.create_all(engine_dst)

    s_src = SessionSrc()
    s_dst = SessionDst()

    # Проверяем, какие таблицы реально существуют в исходном файле database___
    inspector = inspect(engine_src)
    existing_tables = inspector.get_table_names()

    models_to_migrate = [
        Country, Genre, Actor, User, Film,
        Link, Feedback, GenreFilm, ActorFilm, FilmList
    ]

    print(f"Найдено таблиц в источнике: {existing_tables}")
    print("-" * 30)

    try:
        for model in models_to_migrate:
            table_name = model.__tablename__

            # Проверка: есть ли такая таблица в базе-источнике?
            if table_name not in existing_tables:
                print(f"⚠️  Пропускаем {table_name}: таблица отсутствует в database___")
                continue

            # Если таблица есть, переносим данные
            items = s_src.query(model).all()
            print(f"✅ Перенос {table_name}: {len(items)} записей...")

            for item in items:
                s_src.expunge(item)
                make_transient(item)
                s_dst.merge(item)

            s_dst.commit()

        print("-" * 30)
        print("Миграция завершена успешно!")

    except Exception as e:
        s_dst.rollback()
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        s_src.close()
        s_dst.close()


if __name__ == "__main__":
    migrate()