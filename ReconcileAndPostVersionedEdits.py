import arcpy, time, smtplib, random


# get a list of connected users.
userList = arcpy.ListUsers("Database Connections/###.sde")

# get a list of usernames of users currently connected and make email addresses
emailList = [user.Name for user in arcpy.ListUsers("Database Connections/###.sde")]
filteredEmail = []
for users in  emailList:
    try:
      #print users.split('\\',1)[1].split('"',1)[0] + "@wirapids.org"
      if users.split('\\',1)[1].split('"',1)[0] == 'ARCGIS':
          #do not mail to 'ARCGIS' user (web services)
          pass
      else:
        filteredEmail =  users.split('\\',1)[1].split('"',1)[0] + "@wirapids.org"
    except:
        #do not mail to 'DBO' user (me)
      pass

print filteredEmail    
# take the email list and use it to send an email to connected users.
SERVER = "mail.wirapids.org"
FROM = "SDE Admin <ccantey@wirapids.org>"
TO = filteredEmail
SUBJECT = "Maintenance is about to be performed"
MSG = "Auto generated Message.\n\rGIS: Server maintenance will be performed in 15 minutes, please save all edits and maps. \nReconciling and posting all edited versions of OS@gisWiRapids.sde. \n\nPlease log off of all ArcGIS applications."

# Prepare actual message
MESSAGE = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, MSG)

# Send the mail if filteredEmail
try:
    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, MESSAGE)
    server.quit()
except:
    pass

#block new connections to the database.
arcpy.AcceptConnections('Database Connections/###.sde', False)

# wait 15 minutes
time.sleep(900)

#disconnect all users from the database.
arcpy.DisconnectUser('Database Connections/###.sde', "ALL")

#reconcile users to QC
arcpy.ReconcileVersions_management("Database Connections/###.sde","ALL_VERSIONS","DBO.QC","DBO.Chris;DBO.Joe;DBO.Kraig;DBO.Marc","LOCK_ACQUIRED","NO_ABORT","BY_OBJECT","FAVOR_EDIT_VERSION","POST","KEEP_VERSION","#")
print 'reconciled & posted users to QC'

#reconcile QC to DEFAULT
arcpy.ReconcileVersions_management("Database Connections/###.sde","ALL_VERSIONS","dbo.DEFAULT","DBO.QC","LOCK_ACQUIRED","NO_ABORT","BY_OBJECT","FAVOR_TARGET_VERSION","POST","KEEP_VERSION","c:/temp/reconcilelog.txt")
print 'reconciled & posted QC to DEFAULT'

#compress database
arcpy.Compress_management('Database Connections/###.sde')
print 'DB compressed'

#Allow the database to begin accepting connections again
arcpy.AcceptConnections('Database Connections/###.sde', True)




