from fastapi import FastAPI, Query
from .query import BinQuery
app=FastAPI(title="NDT BIN Database", version="1.0.0")
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/api/v1/bins")
def bins(bin: str|None=None,country: str|None=None,issuer: str|None=None,scheme: str|None=None,type: str|None=None,level: str|None=None,bin_length: int|None=None,prepaid: bool|None=None,page: int=Query(1,ge=1),page_size: int=Query(50,ge=1,le=200),sort: str="bin"):
    q=BinQuery(); result=q.search(bin=bin,country=country,issuer=issuer,scheme=scheme,type=type,level=level,bin_length=bin_length,prepaid=prepaid,page=page,page_size=page_size,sort=sort); q.close(); return result
