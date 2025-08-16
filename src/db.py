import os
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError


load_dotenv(".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    link = Column(String(255), unique=True, nullable=False)
    date = Column(Date, nullable=True)
    rating = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Playlist(id={self.id}, name='{self.name}', link='{self.link}')>"


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_playlist(name: str, link: str, date: date, rating: int):

    db = next(get_db_session())

    new_playlist = Playlist(name=name, link=link, date=date, rating=rating)
    
    try:
        db.add(new_playlist)
        db.commit()
        db.refresh(new_playlist)
        return new_playlist
    except IntegrityError:
        db.rollback()
        return None
    finally:
        db.close()

def remove_playlist(playlist_id: int):
    db = next(get_db_session())
    playlist_to_delete = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if playlist_to_delete:
        try:
            db.delete(playlist_to_delete)
            db.commit()
            print(f" '{playlist_to_delete.name}' (ID: {playlist_id}) removed.")
            return True
        except Exception as e:
            db.rollback()
            print(f" Removendo: {e}")
            return False
        finally:
            db.close()
    else:
        db.close()
        return False

def list_playlists():
    db = next(get_db_session())
    try:
        playlists = db.query(Playlist).all()
        return playlists
    finally:
        db.close()

def init_db():
    print("Initializing database and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("DB criada.")

def edit_rating(playlist_id: int, new_rating: int):

    db = next(get_db_session())
    
    try:
        playlist_to_edit = db.query(Playlist).filter(Playlist.id == playlist_id).first()

        if not playlist_to_edit:
            print(f"Valor inválido.")
            return False

        if not (0 <= new_rating <= 10):
            print(f"Valor inválido.")
            return False
        
        playlist_to_edit.rating = new_rating
        db.commit()
        return True
            
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        return False
        
    finally:
        db.close()