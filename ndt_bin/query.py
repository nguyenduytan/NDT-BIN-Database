from __future__ import annotations
import sqlite3

class BinQuery:
    def __init__(self, path="data/bins.sqlite"): self.conn=sqlite3.connect(path); self.conn.row_factory=sqlite3.Row
    def search(self, *, bin=None, country=None, issuer=None, scheme=None, type=None, level=None, bin_length=None, prepaid=None, page=1, page_size=50, sort="bin"):
        allowed={"bin","country","issuer","scheme","type","level","bin_length","prepaid"}; clauses=[]; args=[]
        for key,val in (("bin",bin),("country",country),("issuer",issuer),("scheme",scheme),("type",type),("level",level)):
            if val: clauses.append(f"{key} LIKE ? ESCAPE '\\'"); args.append("%"+str(val).replace("%","\\%").replace("_","\\_")+"%")
        if bin_length: clauses.append("bin_length=?"); args.append(str(bin_length))
        if prepaid is not None: clauses.append("prepaid=?"); args.append("true" if prepaid else "false")
        where=" WHERE "+" AND ".join(clauses) if clauses else ""
        order=sort if sort in allowed else "bin"; offset=max(0,page-1)*min(max(page_size,1),200); limit=min(max(page_size,1),200)
        total=self.conn.execute("SELECT COUNT(*) FROM bins"+where,args).fetchone()[0]
        rows=[dict(x) for x in self.conn.execute(f"SELECT * FROM bins{where} ORDER BY {order}, bin LIMIT ? OFFSET ?",args+[limit,offset])]
        return {"items":rows,"total":total,"page":page,"page_size":limit}
    def close(self): self.conn.close()
