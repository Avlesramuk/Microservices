from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from .models import URL
from .schemas import URLRequest
from .utils import encode_base62

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
        "short_url": f"http://18.208.141.105:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(status_code=404)

    return RedirectResponse(url.long_url)