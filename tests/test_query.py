import sqlite3
from ndt_bin.query import BinQuery
def test_combined_search_is_parameterized(tmp_path):
    p=tmp_path/"x.sqlite"; c=sqlite3.connect(p); c.execute("create table bins (bin text, country text, issuer text, scheme text, type text, level text, bin_length text, prepaid text)"); c.execute("insert into bins values ('004078','UNITED STATES','SHIFT4 PAYMENTS','VISA','DEBIT','GIFT','6','true')"); c.commit(); c.close()
    q=BinQuery(p); result=q.search(bin="004",country="UNITED",scheme="VISA",prepaid=True); assert result["total"]==1; assert result["items"][0]["bin"]=="004078"
