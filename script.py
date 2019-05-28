#imports
from urllib.request import urlopen
from bs4 import BeautifulSoup
import wget
import zipfile
import os
import redis
import pandas as pd

#Url from where file is to be fetched.
url = 'https://www.bseindia.com/markets/equity/EQReports/Equitydebcopy.aspx'

#Parsing page to find zip file link.
conn = urlopen(url)
html = conn.read()
soup = BeautifulSoup(html,"lxml")

#Find the zip file link.
tag = soup.find(id='btnhylZip')
#Get the link to zip file.
link = tag.get('href',None)

#Download zip file using wget.
zip_name = wget.download(link)
print()

#Unzip file to csv-files folder.
zip_ref = zipfile.ZipFile(zip_name, 'r')
zip_ref.extractall("csv-files/")
#Save name of the csv file.
csv_file = zip_ref.namelist()[0]
zip_ref.close()

print(csv_file[0:-4])

#Delete zip file.
os.remove(zip_name)

#Read csv file using pandas.
df = pd.read_csv("csv-files/"+csv_file)

#Keep only the required columns.
df = df[['SC_CODE', 'SC_NAME', 'OPEN', 'HIGH', 'LOW', 'CLOSE']].copy()

#Calculate percantage difference between opening and closing price.
df['PERCENTAGE'] = round(((df['CLOSE'] - df['OPEN'])/ df['OPEN'])*100, 2)

df_compute = df.copy()

#Compute top ten gainers.
df_gain = df_compute.nlargest(10,['PERCENTAGE']).copy()
#Compute top ten loosers.
df_loose = df_compute.nsmallest(10,['PERCENTAGE']).copy()


#Connect to redis database.
r = redis.from_url(os.environ.get("REDIS_URL"))


for index, row in df.iterrows():
	#Save every row in data frame with SC_CODE as key.
	r.hmset(row['SC_CODE'],row.to_dict())
	#Save SC_CODE using SC_NAME prefixed with equity as key for searching.
	r.set("equity:"+row['SC_NAME'],row['SC_CODE'])

#Delete old gainers and loosers.
for key in r.scan_iter("gain:*"):
	r.delete(key)
for key in r.scan_iter("loose:*"):
	r.delete(key)

#Save SC_CODE of gainers using SC_NAME with gain prefix.
for index, row in df_gain.iterrows():
	r.set("gain:"+row['SC_NAME'],row['SC_CODE'])

#Save SC_CODE of loosers using SC_NAME with loose prefix.
for index, row in df_loose.iterrows():
	r.set("loose:"+row['SC_NAME'],row['SC_CODE'])

#Save last updated string in redis database.
r.set("latest",csv_file[2:4]+"-"+csv_file[4:6]+"-20"+csv_file[6:8])

