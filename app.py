__requires__ = [
	'cherrypy_cors',
]

import requests, zipfile, io, os
import redis
import datetime
import pandas as pd
import cherrypy,cherrypy_cors
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

filename = None

def create_connection():
	try:
		#redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
		redis_db = redis.from_url(os.environ.get("REDIS_URL"))  # for connection in heroku
		return redis_db
	except Exception as e:
		print (e)

def push_to_redis(filename):
	# create a connection to the localhost Redis server instance, by
	try:
		redis_db = create_connection()
		redis_db.flushall()
		redis_db.set("filename",filename)
		df = pd.read_csv(filename+'.CSV')
		for row in df.itertuples(index=True, name='Pandas'):
			SC_NAME = str(getattr(row, "SC_NAME")).strip()
			redis_db.lpush(str(getattr(row, "SC_NAME")).strip(),getattr(row, "SC_CODE"))
			redis_db.lpush(str(getattr(row, "SC_NAME")).strip(),getattr(row, "OPEN"))
			redis_db.lpush(str(getattr(row, "SC_NAME")).strip(),getattr(row, "HIGH"))
			redis_db.lpush(str(getattr(row, "SC_NAME")).strip(),getattr(row, "LOW"))
			redis_db.lpush(str(getattr(row, "SC_NAME")).strip(),getattr(row, "CLOSE"))
	except Exception as e:
		print(e)

def fetchCSV():
	global filename
	filename = 'EQ'+str(datetime.date.today().strftime('%d%m%y'))
	if(not os.path.exists(filename+'.CSV')):
		try:
			url = "https://www.bseindia.com/download/BhavCopy/Equity/"+filename+"_CSV.ZIP"
			print(url)
			response = requests.get(url)
			print(response.status_code)
			if(response.status_code==200):
				z = zipfile.ZipFile(io.BytesIO(response.content))
				z.extractall("/Users/ayushpalak/Downloads/zerodha")
				print("file downloaded and unzipped.")
				push_to_redis(filename)
			else:
				prev_filename = 'EQ'+str((datetime.date.today()-datetime.timedelta(1)).strftime('%d%m%y'))
				redis_db = create_connection()
				_filename = redis_db.get("filename")
				if _filename and (_filename.decode() == prev_filename):
					filename = prev_filename
					print("previous day data already in redis.")
				else:
					if(os.path.exists(prev_filename+'.CSV')):
						filename = prev_filename
						print("previous day data not in redis. Pushing it from yesterdays downloaded file.")
						push_to_redis(filename)
						print("Showing yesterdays data.")
					else:
						print("previous day file not available. showing very old data.")
		except Exception as e:
			print ("catching fetchCSV()",e)

def get_stock_data(stock_name):
	stock_name = stock_name.strip()
	result = []
	redis_db = create_connection()
	print("getting data from redis.")
	l  = redis_db.lrange(stock_name.upper(),0,4)
	l = [i.decode("utf-8") for i in l]
	print (l)
	return l

class parser(object):
	
	def CORS():
		cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

	@cherrypy.expose
	def home(self):
		tmpl = env.get_template('index.html')
		return tmpl.render()

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.json_in()
	def index(self):
		request_json = cherrypy.request.json
		stock_name = request_json["stock_name"]
		fetchCSV()
		result = get_stock_data(stock_name)
		return {"filename":filename,"result":list(result)}

	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.json_in()
	def get_top_10(self):
		result = []
		fetchCSV()
		redis_db = create_connection()
		keys = redis_db.keys()
		keys = [i.decode() for i in keys]
		result = {}
		l = redis_db.scan(9)
		for i in l[1]:
			r = redis_db.lrange(i,0,4)
			r = [item.decode() for item in r]
			result[i.decode()] = r
		return {"result":result,"keys":keys}


if __name__ == '__main__':
	cherrypy_cors.install()
	conf = {
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd()),
			'tools.response_headers.on': True,
			'cors.expose.on': True,
			
			
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './public'
		}
	}
	cherrypy.config.update({'server.socket_host': '0.0.0.0',})
	cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')),})
	cherrypy.quickstart(parser(),'/',conf)