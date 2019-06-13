import requests, zipfile, io, os
import redis
import datetime
import pandas as pd
import cherrypy

filename = None

def create_connection():
	try:
		#redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
		redis_db = redis.from_url(os.environ.get("REDIS_URL"))  # for connection in heroku
		return redis_db
	except Exception as e:
		print (e)

def push_to_redis():
	# create a connection to the localhost Redis server instance, by
	try:
		redis_db = create_connection()
		redis_db.flushall()
		#print ("reading file from local.")
		df = pd.read_csv(filename+'.CSV')
		#print ("file readed from local.")
		#print ("top 10 rows.",df.head(10))
		for row in df.itertuples(index=True, name='Pandas'):
		#    print(getattr(row, "SC_CODE"), getattr(row, "SC_NAME"),getattr(row, "OPEN"),getattr(row, "HIGH"),getattr(row, "LOW"),getattr(row, "CLOSE"))
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
				push_to_redis()
			else:
				prev_filename = 'EQ'+str((datetime.date.today()-datetime.timedelta(1)).strftime('%d%m%y'))
				if(os.path.exists(prev_filename+'.CSV')):
				# push_to_redis()
					filename = prev_filename
					#push_to_redis()
					print("Showing yesterdays data.")
		except exception as e:
			print (e)

def get_stock_data(stock_name):
	result = []
	redis_db = create_connection()
	print("getting data from redis.")
	while(redis_db.llen(stock_name)!=0):
		result.append((redis_db.lpop(stock_name).decode("utf-8")))
	return result

class parser(object):
	
	
	@cherrypy.expose
	@cherrypy.tools.json_out()
	@cherrypy.tools.json_in()
	def index(self):
		request_json = cherrypy.request.json
		stock_name = request_json["stock_name"]
		fetchCSV()
		result = get_stock_data(stock_name)
		return {"filename":filename,"result":list(result)}


if __name__ == '__main__':
	cherrypy.config.update({'server.socket_host': '0.0.0.0',})
	cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')),})
	cherrypy.quickstart(parser())