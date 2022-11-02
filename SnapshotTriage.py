import datetime
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
import sys
import ccl_bplist
import plistlib
import io
import os
import glob
import sqlite3
from shutil import copy
from time import process_time

parser = argparse.ArgumentParser(description="\
	iOS Snapshot KTX Traige Parser\
	\n\n Parse iOS snapshot plists and matching ktx files."
, prog='SnapTriage.py'
, formatter_class=RawTextHelpFormatter)
parser.add_argument('data_dir_snaps',help="Path  to the Snapshot images Directory")
parser.add_argument('data_dir_appState',help="Path to the applicationState.db Directory..")

args = parser.parse_args()
data_dir = args.data_dir_snaps
appState_dir = args.data_dir_appState
count = 0
pathfound = 0

#create directories
#foldername = str(int(datetime.datetime.now().timestamp()))
foldername = ("iOSSnapshotTriageReports_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

#calculate timestamps
unix = datetime.datetime(1970, 1, 1)
cocoa = datetime.datetime(2001, 1, 1)
delta = cocoa - unix 

for root, dirs, filenames in os.walk(appState_dir):
		for f in filenames:
			if f == "applicationState.db":
				pathfound = os.path.join(root, f)


if pathfound == 0:
		print("No applicationState.db")
else:
		path = os.getcwd()
		try:  
				outpath = f"{path}/{foldername}"
				os.mkdir(outpath)
				os.mkdir(f"{outpath}/ExtractedBplistsFirstLevel")
				os.mkdir(f"{outpath}/ExtractedBplistsSecondLevel")
				os.mkdir(f"{outpath}/Reports")
				os.mkdir(f"{outpath}/Reports/images")
		except OSError:  
			print("Error making directories")



		print("\n--------------------------------------------------------------------------------------")
		print("iOS Snapshot Triage Parser.")
		print("Objective: Triage iOS Snapshot images.")
		print("By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com")
		print(f"Processed images directory: {data_dir}")
		print(f"Snapshots database: {appState_dir}")
		print("\n--------------------------------------------------------------------------------------")
		print("")

		print(f"Database located at: {pathfound}")
		print("Please wait...")

		#connect sqlite databases
		#database = 'applicationState.db'
		db = sqlite3.connect(pathfound)
		cursor = db.cursor()

		cursor.execute('''SELECT
	application_identifier_tab.id,
	application_identifier_tab.application_identifier,
	kvs.value
	FROM kvs, application_identifier_tab, key_tab
	WHERE application_identifier_tab.id = kvs.application_identifier
	and key_tab.key = 'XBApplicationSnapshotManifest'
	and key_tab.id = kvs.key
	''')

		all_rows = cursor.fetchall()

		for row in all_rows:
				bundleid = row[1]
				wbplist = row [2]
				print(f'Processing: {bundleid}')
				with open(f'./{foldername}/ExtractedBplistsFirstLevel/{bundleid}.bplist', 'wb') as output_file:
						output_file.write(wbplist)
				g = open(f'./{foldername}/ExtractedBplistsFirstLevel/{bundleid}.bplist', 'rb')
				plistg = ccl_bplist.load(g)

				with open(f'./{foldername}/ExtractedBplistsSecondLevel/{bundleid}.bplist', 'wb') as output_file:
						output_file.write(plistg)
				g = open(f'./{foldername}/ExtractedBplistsSecondLevel/{bundleid}.bplist', 'rb')
				plistg = ccl_bplist.load(g)
				long = len(plistg['$objects'])

				with open(f'./{foldername}/Reports/{bundleid}.html', 'w') as h:
						h.write('<html><body>')
						h.write('<h2>iOS Snapshots Triage Report </h2>')
						h.write(f'<h3>Application: {bundleid}</h3>')
						h.write(f'Data aggregated per following data source: {pathfound}')
						h.write('<br/>')
						h.write('Press on the image to get full size')
						h.write('<br/>')
						h.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;}</style>')
						h.write('<br/>')

						#opne table
						h.write('<table>')
						for i in range(long):
								test = (plistg['$objects'][i])
								try:
										if test.endswith('@3x.ktx'):
												h.write('<tr><td>Filename:<br><font size="3" color="green">'+str(test)+'</font></td></tr>')
												h.write('<tr>')
												h.write('<td>')
												image = test.split('.')
												imagenew = image[0]
												path2 = os.getcwd()
												imagepath = f'{path}/{data_dir}/{imagenew}.png'
												imageoutpath = f'{outpath}/Reports/images'
												#print ('path2: '+path2)
												#print('image: '+imagepath)
												#print('imagefinal: '+imageoutpath)
												#print('foldername: '+foldername)
												copy(imagepath, imageoutpath)
												h.write(f'<a href=./images/{imagenew}' + '.png target="_blank">')
												h.write(f'<img src=./images/{imagenew}' + '.png width="310" height="552" ')
												h.write('/>')
												h.write('</a>')
												h.write('</td>')
												h.write('</tr>')
															#new html block
															#convert the ktx to jpg and add to html
															#print(test)

								except:
									pass

								try:
										if test.endswith('@2x.ktx'):
												h.write('<tr><td>Filename:<br><font size="3" color="green">'+str(test)+'</font></td></tr>')
												h.write('<tr>')
												h.write('<td>')
												image = test.split('.')
												imagenew = image[0]
												path2 = os.getcwd()
												imagepath = f'{path}/{data_dir}/{imagenew}.png'
												imageoutpath = f'{outpath}/Reports/images'
												#print ('path2: '+path2)
												#print('image: '+imagepath)
												#print('imagefinal: '+imageoutpath)
												#print('foldername: '+foldername)
												copy(imagepath, imageoutpath)
												h.write(f'<a href=./images/{imagenew}' + '.png target="_blank">')
												h.write(f'<img src=./images/{imagenew}' + '.png width="310" height="552" ')
												h.write('/>')
												h.write('</a>')
												h.write('</td>')
												h.write('</tr>')
															#new html block
															#convert the ktx to jpg and add to html
															#print(test)
															#new html block
															#convert the ktx to jpg and add to html

								except:
									pass

								try:
									if test.endswith('.png'):
										h.write('<tr>')
										h.write('<td>')
										h.write('File not found on system. <br> <font size="3" color="green">'+str(test)+'</font>')
										h.write('</td>')
										h.write('</tr>')
										#new html block
										#convert the ktx to jpg and add to html
										#print(test)

								except:
									pass

								try:
									if test['NS.time']:
										dates = test['NS.time']
										dia = str(dates)
										dias = (dia.rsplit('.', 1)[0])
										timestamp = datetime.datetime.fromtimestamp(int(dias)) + delta

										h.write('<tr>')
										h.write('<td>')
										h.write(str(timestamp))
										h.write('</td>')
										h.write('</tr>')

										#print(timestamp)

								except:
									pass
						h.write('<table>')
						h.write('<br/>')
						h.write('Script by: abrignoni.com')
						h.write('</html>')
				count = count + 1
print(f'Total of apps with processed snapshots: {str(count)}')
