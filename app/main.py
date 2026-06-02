from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from .models import URL
from .schemas import URLRequest
from .utils import encode_base62
from .cache import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten")
def shorten_url(req: URLRequest, db: Session = Depends(get_db)):
    url = URL(long_url=req.long_url)
    db.add(url)
    db.commit()
    db.refresh(url)

    short_code = encode_base62(url.id)

    url.short_code = short_code
    db.commit()

    return {
        "short_url": f"http://13.218.35.128:8000/{short_code}"
    }


@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):

    cached_url = redis_client.get(short_code)

    if cached_url:
        return RedirectResponse(cached_url)

    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(status_code=404)

    redis_client.set(
        short_code,
        url.long_url,
        ex=3600
    )

    return RedirectResponse(url.long_url)