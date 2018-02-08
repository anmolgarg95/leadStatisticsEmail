#!/Python27/python

import smtplib
from getConn import connection
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from jinja2 import Template	
import datetime
import json
from operator import itemgetter

c, conn = connection()
##################################################			sql Query Functions
def agentLeads(date):	
	query = ("SELECT aid ,COUNT(*),COUNT(DISTINCT email) FROM affiliate_query WHERE timeSubmitted LIKE '%s' GROUP BY aid" % date)
	c.execute(query)
	result = c.fetchall()
	result = list(result)
	return result
	"""obj = []
	for row in result:
		dic = {
			'agentName' : str(row[0]),
			'totalLeads' : str(row[1]),
			'uniqueLeads' : str(row[2])
			}
		obj.append(dic)
	return	json.dumps(obj)
"""
def destinationLeads(date):
	query = ("SELECT destination, COUNT(destination) AS TotalLeads, COUNT(DISTINCT email) AS UniqueLeads FROM affiliate_query WHERE timeSubmitted LIKE '%s' AND destination != '' GROUP BY destination ORDER BY TotalLeads DESC LIMIT 5" % date)
	c.execute(query)
	result = c.fetchall()
	obj = []
	for row in result:
		dic = {
			'destName' : str(row[0]),
			'totalLeads' : str(row[1]),
			'uniqueLeads' : str(row[2]),
			}
		obj.append(dic)
	return	json.dumps(obj)

def platformLeads(date):
	query = ("SELECT platform,count(platform) from affiliate_query where timeSubmitted like '%s' group by platform" % date)
	c.execute(query)
	result = c.fetchall()
	result = list(result)
	return	result

def leadData(date):
	query = ("SELECT leadData, COUNT(*) AS total_num, COUNT(DISTINCT email) AS dist_num FROM affiliate_query WHERE timeSubmitted LIKE '%s' GROUP BY leadData" % date)
	c.execute(query)
	result = c.fetchall()
	result = list(result)
	return	result

###################################################			date-Part
todayDate = datetime.date.today() 
yesterdayDate = str(todayDate - datetime.timedelta(days = 1))
print yesterdayDate
yesterdayDate += "%"

###################################################			Reading the template
file= open("lead_template.html","r")
templateData = file.read()
file.close()

###################################################			Calling sqlQuery Agent Leads
varAgentLeads = agentLeads(yesterdayDate)
sizeAgents = len(varAgentLeads)
print sizeAgents

###################################################			Callling sqlQuery Destination Leads
varDestinationLeads = json.loads(destinationLeads(yesterdayDate))
rows = 5
cols = 3
leadsDestination=[]
for row in range(rows): 
	leadsDestination += [[0]*cols]
i=0
for row in varDestinationLeads:
	leadsDestination[i][0] = row['destName']
	leadsDestination[i][1] = row['totalLeads']
	leadsDestination[i][2] = row['uniqueLeads']
	i+=1

###################################################			Calling sqlQuery Platform Leads
varPlatformLeads = platformLeads(yesterdayDate)

platformLeadsDict = {}
platformLeadsDict["Android"] = 0
platformLeadsDict["Windows"] = 0
platformLeadsDict["Others"] = 0
for row in varPlatformLeads:
	if(row[0]=="iPad"):
		platformLeadsDict["iPad"] = row[1]
	elif(row[0]=="iPhone"):
		platformLeadsDict["iPhone"] = row[1]
	elif(row[0]=="MacIntel"):
		platformLeadsDict["MacBook"] = row[1]
	elif(row[0][0]=='L'):
		platformLeadsDict["Android"] += row[1]
	elif(row[0][0]=='W'):
		platformLeadsDict["Windows"] += row[1]
	else:
		platformLeadsDict["Others"] += row[1]

platformLeadsList = sorted(platformLeadsDict.items(), key=itemgetter(1),reverse = True)

###################################################			Calling sqlQuery for page Leads
varLeadData = leadData(yesterdayDate)

pageNames = []
for row in varLeadData:
	splitted = str.split(row[0],'_')
	pageNames.append(splitted[0])

totalLeadsDict = {}
uniqueLeadsDict ={}
i=0

for pageName in pageNames: 
	if pageName not in totalLeadsDict.keys():
		totalLeadsDict[pageName] = int(varLeadData[i][1])
		uniqueLeadsDict[pageName] = int(varLeadData[i][2])
	else:
		totalLeadsDict[pageName] = int(varLeadData[i][1]) + totalLeadsDict.get(pageName)
		uniqueLeadsDict[pageName] = int(varLeadData[i][2]) + uniqueLeadsDict.get(pageName)
	i+=1

totalLeadsList = sorted(totalLeadsDict.items(), key=itemgetter(1),reverse = True)
uniqueLeadsList = sorted(uniqueLeadsDict.items(), key=itemgetter(1),reverse = True)

##################################################			For button leads

buttonNames = []
for row in varLeadData:
	splitted = str.split(row[0],'_')
	buttonNames.append(splitted[2])

totalLeadsDict_button = {}
uniqueLeadsDict_button ={}

i=0
for buttonName in buttonNames: 
	if buttonName not in totalLeadsDict_button.keys():
		totalLeadsDict_button[buttonName] = int(varLeadData[i][1])
		uniqueLeadsDict_button[buttonName] = int(varLeadData[i][2])
	else:
		totalLeadsDict_button[buttonName] = int(varLeadData[i][1]) + totalLeadsDict_button.get(buttonName)
		uniqueLeadsDict_button[buttonName] = int(varLeadData[i][2]) + uniqueLeadsDict_button.get(buttonName)
	i+=1

totalLeadsList_button = sorted(totalLeadsDict_button.items(), key=itemgetter(1),reverse = True)
uniqueLeadsList_button = sorted(uniqueLeadsDict_button.items(), key=itemgetter(1),reverse = True)

###################################################			Email Part		
fromaddr = "" #Email Id from which mail is to be sent
fromPass = "" #Password for your email
toaddr = "anmol@holidify.com"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Leads Summary for "+yesterdayDate[:-1]
body = ""
template = Template(templateData)
afterRendering = template.render(varAgentLeads=varAgentLeads,sizeAgents = sizeAgents ,leadsDestination=leadsDestination,platformLeadsList= platformLeadsList,totalLeadsList =totalLeadsList, uniqueLeadsList = uniqueLeadsList,totalLeadsList_button = totalLeadsList_button,uniqueLeadsList_button = uniqueLeadsList_button)

part1 = MIMEText(body, 'plain')
part2 = MIMEText(afterRendering, 'html')
 
msg.attach(part1)
msg.attach(part2)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, fromPass)
server.sendmail(fromaddr, toaddr, msg.as_string())
print "sent!"
server.quit()

###################################################
