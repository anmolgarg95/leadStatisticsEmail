#!/Python27/python

import MySQLdb

def connection():
	conn = MySQLdb.connect("localhost","anmol","root","holidify_db_v3")
	c = conn.cursor()
	return c,conn