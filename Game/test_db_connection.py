import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='lbsApi',
        port=3306
    )
    print("成功连接到数据库")
    conn.close()
except pymysql.MySQLError as e:
    print("无法连接到数据库:", e)