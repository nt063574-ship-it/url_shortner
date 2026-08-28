
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import string
import random
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


DATABASE_URL = "sqlite:///./shortener.db"



engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)


class URLCreate(BaseModel):
    original_url: HttpUrl


class URLResponse(BaseModel):
    original_url: HttpUrl
    short_code: str
    short_url:str
    clicks: int

    class Config:
        from_attributes = True


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")



def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(
        random.choice(characters)
        for _ in range(length)
    )


@app.get("/")
def urlshortner():
    return FileResponse("static/index.html")


@app.post("/shorten", response_model=URLResponse)
def shorten_url(
    url: URLCreate,
    db: Session = Depends(get_db)
):
    short_code = generate_short_code()

    while db.query(URL).filter(
        URL.short_code == short_code
    ).first():
        short_code = generate_short_code()

    new_url = URL(
        original_url=str(url.original_url),
        short_code=short_code,
        clicks=0
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
        "original_url": new_url.original_url,
        "short_code": new_url.short_code,
        "short_url": f"https://url-shortner-dfk1.onrender.com/{new_url.short_code}",
        "clicks": new_url.clicks
    }

@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db)
):
    url_entry = (
        db.query(URL)
        .filter(URL.short_code == short_code)
        .first()
    )

    if not url_entry:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    url_entry.clicks += 1
    db.commit()

    return RedirectResponse(url=url_entry.original_url)

@app.get("/stats/{short_code}")
def get_stats(
    short_code: str,
    db: Session = Depends(get_db)
):
    url_entry = (
        db.query(URL)
        .filter(URL.short_code == short_code)
        .first()
    )

    if not url_entry:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    

    return {
        "original_url": url_entry.original_url,
        "short_code": url_entry.short_code,
        "short_url": f"https://url-shortner-dfk1.onrender.com/{url_entry.short_code}",
        "clicks": url_entry.clicks
    }
