#!/usr/bin/python -tt

from pysqlite2 import dbapi2 as sqlite3
from time	  import time
import commands, os, sys


class UpsChecker:
	""" class for ups checking and storing data in db """
	connection = 0;
	cursor     = 0;
	path_app   = ''
	path_bin   = ''
	path_db    = ''
	options    = {}
	time_start = time()
	
	def __init__(self):
		""" constructor """
		# set paths
		self.path_app = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
		self.path_bin = self.path_app + '/bin'
		self.path_db  = self.path_app + '/dbase'

		# set connect
		self.connection = sqlite3.connect(self.path_db + "/upsmon.sqlite")
		self.cursor = self.connection.cursor()

		# get option list
		self.cursor.execute("select * from options")
		for row in self.cursor.fetchall():
			self.options[row[1]] = row[0];
		#print self.options;

	def check(self):
		# start of the check
		self.cursor.execute("insert into checks (time_start) values (%i)" % time())
		checkid = self.cursor.lastrowid

		list = commands.getstatusoutput("upsc dpups")[1].strip().split("\n")
		if ( list ):
			for option in list:
				option = option.split(':')
				if self.options.has_key(option[0]):
					if option[0] == 'ups.beeper.status':
						if option[1] == 'disabled':
							option[1] = 0
						else:
							option[1] = 1
							commands.getstatusoutput("upscmd -u monuser -p mustekpass dpups beeper.toggle")
					if option[0] == 'ups.status':
						if option[1] == 'OL': option[1] = 1
						else:				 option[1] = 0
					self.cursor.execute("insert into \"values\" (id_option, id_check, value) values (%i, %i, %s)" % (self.options[option[0]], checkid, option[1]))

		self.cursor.execute("update checks set time_end = %i where id = %i" % (time(), checkid))
		self.connection.commit()
		self.cursor.close()

uc = UpsChecker()
uc.check()
