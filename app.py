from flask import Flask, request, render_template
import mysql.connector
from mysql.connector import Error
import pymysql
import re

from pymysql.cursors import DictCursor

app = Flask(__name__)

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='surgodriti',
            database='supplierParts',
            cursorclass=DictCursor
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insert1')
def insert1():
    conn = get_db_connection()
    cursor = None
    if conn is None:
        return render_template("insert_result.html", 
                             msg="Failed to connect to database",
                             query_type="Insert 1",
                             success=False)
    try:
        cursor = conn.cursor()
        query = "INSERT INTO SHIPMENT (Sno, Pno, Qty, Price) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, ('s2', 'p3', 200, 0.006))
        conn.commit()
        return render_template("insert_result.html", 
                             msg="Successfully inserted shipment record: Sno=s2, Pno=p3, Qty=200, Price=0.006",
                             query_type="Insert 1",
                             success=True)
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:  # Duplicate entry error code
            return render_template("insert_result.html", 
                                 msg="The insert query was not successful - Duplicate entry exists",
                                 query_type="Insert 1",
                                 success=False)
        return render_template("insert_result.html", 
                             msg=f"Failed to insert shipment record: {str(e)}",
                             query_type="Insert 1",
                             success=False)
    except Error as e:
        return render_template("insert_result.html", 
                             msg=f"Failed to insert shipment record: {str(e)}",
                             query_type="Insert 1",
                             success=False)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/insert2')
def insert2():
    conn = get_db_connection()
    cursor = None
    if conn is None:
        return render_template("insert_result.html", 
                             msg="Failed to connect to database",
                             query_type="Insert 2",
                             success=False)
    try:
        cursor = conn.cursor()
        query = "INSERT INTO SHIPMENT (Sno, Pno, Qty, Price) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, ('s4', 'p2', 100, 0.005))
        conn.commit()
        return render_template("insert_result.html", 
                             msg="Successfully inserted shipment record: Sno=s4, Pno=p2, Qty=100, Price=0.005",
                             query_type="Insert 2",
                             success=True)
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:  # Duplicate entry error code
            return render_template("insert_result.html", 
                                 msg="The insert query was not successful - Duplicate entry exists",
                                 query_type="Insert 2",
                                 success=False)
        return render_template("insert_result.html", 
                             msg=f"Failed to insert shipment record: {str(e)}",
                             query_type="Insert 2",
                             success=False)
    except Error as e:
        return render_template("insert_result.html", 
                             msg=f"Failed to insert shipment record: {str(e)}",
                             query_type="Insert 2",
                             success=False)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/update_status')
def update_status():
    conn = get_db_connection()
    cursor = None
    if conn is None:
        return render_template("insert_result.html", 
                             msg="Failed to connect to database",
                             query_type="Update Status",
                             success=False)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE SUPPLIER SET Status = Status * 1.10")
        affected_rows = cursor.rowcount
        conn.commit()
        return render_template("insert_result.html", 
                             msg=f"Successfully updated status for {affected_rows} suppliers (increased by 10%)",
                             query_type="Update Status",
                             success=True)
    except Error as e:
        return render_template("insert_result.html", 
                             msg=f"Failed to update supplier status: {str(e)}",
                             query_type="Update Status",
                             success=False)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/suppliers')
def display_suppliers():
    conn = get_db_connection()
    cursor = None
    if conn is None:
        return render_template("suppliers.html", 
                             suppliers=None, 
                             error="Failed to connect to database",
                             success=False)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SUPPLIER")
        suppliers = cursor.fetchall()
        if not suppliers:
            return render_template("suppliers.html", 
                                 suppliers=None,
                                 msg="No suppliers found in the database",
                                 success=True)
        return render_template("suppliers.html", 
                             suppliers=suppliers,
                             msg=f"Successfully retrieved {len(suppliers)} suppliers",
                             success=True)
    except Error as e:
        return render_template("suppliers.html", 
                             suppliers=None,
                             error=f"Failed to retrieve suppliers: {str(e)}",
                             success=False)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/part_query', methods=['GET', 'POST'])
def part_query():
    suppliers = None
    part_no = None
    if request.method == 'POST':
        part_no = request.form['part_no']
        conn = get_db_connection()
        cursor = None
        if conn is None:
            return render_template("part_query.html", 
                                 suppliers=None, 
                                 part_no=part_no, 
                                 error="Failed to connect to database",
                                 success=False)
        try:
            cursor = conn.cursor()
            query = """
                SELECT S.* FROM SUPPLIER S
                JOIN SHIPMENT SH ON S.Sno = SH.Sno
                WHERE SH.Pno = %s
            """
            cursor.execute(query, (part_no,))
            suppliers = cursor.fetchall()
            if not suppliers:
                return render_template("part_query.html", 
                                     suppliers=None,
                                     part_no=part_no,
                                     msg=f"No suppliers found for part {part_no}",
                                     success=True)
            return render_template("part_query.html", 
                                 suppliers=suppliers,
                                 part_no=part_no,
                                 msg=f"Successfully found {len(suppliers)} suppliers for part {part_no}",
                                 success=True)
        except Error as e:
            return render_template("part_query.html", 
                                 suppliers=None,
                                 part_no=part_no,
                                 error=f"Failed to query suppliers for part {part_no}: {str(e)}",
                                 success=False)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return render_template("part_query.html", 
                         suppliers=suppliers, 
                         part_no=part_no,
                         success=None)

if __name__ == '__main__':
    app.run(debug=True)
