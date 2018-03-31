"""
Deze Applicatie verzorgd een koppeling tussen:
* Radio Audtomatisering
* MySQL Database
* FTP Server
Daarnaast word een XML gegenereerd voor koppeling Website -> Fileserver
Deel van commentaar volgt in het Engels, statussen worden in het Nederlands gegeven.
"""

__version__ = '1.2'
__author__ = 'Sander Post'

import schedule
import ftplib
import mysql.connector
import datetime
import tzlocal
import threading
import xml.etree.ElementTree
import os
from time import sleep


class Model:

    # Define class variables
    status = 'Initialiseren..'
    time = 'Initialiseren..'
    xml_handle = "C:\\Users\\Gebruiker\\Desktop\\Executable Uitzending Gemist\\uitzendingen.xml"
    ftp_username = ""               # username
    ftp_password = ""               # password
    ftp_server = ""                 # server
    sql_username = ""               # username
    sql_password = ""               # password
    sql_server = ""                 # server
    sql_database = ""               # databasename
    path = '\\\\ZENLEX-SERVER\\Zenlex\\Item Collectie\\herhaaluren\\'
    timezone = tzlocal.get_localzone()  # Local timezone used for datetime conversions

    # Run a method in a different thread
    # @staticmethod
    def run_threaded(self, job_func):
        try:
            job_thread = threading.Thread(target=job_func)
            job_thread.start()
        except Exception:
            pass

    # Return current weeknumber
    @staticmethod
    def get_week():
        weeknumber = datetime.datetime.today().isocalendar()[1]
        return weeknumber

    # Print the XML tree
    def print_xml(self):
        tree = xml.etree.ElementTree.parse(self.xml_handle)
        root = tree.getroot()
        for week in root:
            for day in week:
                for program in day:
                    for detail in program:
                        print(detail.text)

    # =============================================================================
    # XML Handling
    # =============================================================================
    # Update XML
    # Args: param1  (int)       search week
    #       param2  (str)       search day
    #       param3  (str)       search program
    #       param4  (datetime)  search hour
    #       param5  (str)       database filename inside url
    def update_xml(self, s_week, s_day, s_program, s_hour, url):
        tree = xml.etree.ElementTree.parse(self.xml_handle)
        root = tree.getroot()
        # First case let's assume everything exists
        try:
            for week in root:
                if week.get('weeknummer') == str(s_week):
                    for day in week:
                        # Let's check if the day in this week exists
                        if day.tag == str(s_day):
                            for program in day:
                                # Let's loop through all our programs
                                for detail in program:
                                    # Need to find the right hour
                                    if detail.tag == str('tijd') and detail.text == str(s_hour):
                                        # If I exist exit all loops
                                        raise StopIteration
                                # Let's assume this hour hasn't been added yet
                            else:
                                attrib = {}
                                programma_element = day.makeelement('programma', attrib)
                                naam_element = programma_element.makeelement('naam', attrib)
                                url_element = programma_element.makeelement('url', attrib)
                                tijd_element = programma_element.makeelement('tijd', attrib)
                                naam_element.text = str(s_program)
                                url_element.text = str(url)
                                tijd_element.text = str(s_hour)
                                programma_element.append(naam_element)
                                programma_element.append(url_element)
                                programma_element.append(tijd_element)
                                day.append(programma_element)
                                tree.write(self.xml_handle)
                                raise StopIteration
                    # Let's assume the day in this week doesn't exist
                    else:
                        self.write_day(tree, week, s_week, s_day, s_program, s_hour, url)
                        # If I exist exit all the loops
                        raise StopIteration
            # Week element does not exist (probably start new week)
            else:
                self.write_week(root, tree, s_week, s_day, s_program, s_hour, url)
                # If I exist exit all loops
                raise StopIteration
        except StopIteration:
            self.status = 'XML is bijgewerkt'
            pass

    # Write a week element to the root node
    # Args: param1  (element)   root node
    #       param2  (element)   tree XML filehandle
    #       param3  (int)       search week
    #       param4  (str)       search day
    #       param5  (str)       search program
    #       param6  (datetime)  search hour
    #       param7  (str)       database filename inside url
    def write_week(self, root, tree, week, s_day, s_program, s_hour, url):
        attrib = {'weeknummer': str(week)}
        newweek = root.makeelement('week', attrib)
        root.append(newweek)
        tree.write(self.xml_handle)
        self.update_xml(week, s_day, s_program, s_hour, url)

    # Write a day element to the week node
    # Args: param1  (element)   tree XML filehandle
    #       param2  (element)   week node
    #       param3  (int)       search week
    #       param4  (str)       search day
    #       param5  (str)       search program
    #       param6  (datetime)  search hour
    #       param7  (str)       database filename inside url
    def write_day(self, tree, week, s_week, dag, s_program, s_hour, url):
        attrib = {}
        element = week.makeelement(dag, attrib)
        week.append(element)
        tree.write(self.xml_handle)
        self.update_xml(s_week, dag, s_program, s_hour, url)

    # =============================================================================
    # FTP Handling
    # =============================================================================
    # Write the audio file to the FTP server
    # Creates subdirectory if it doesn't exist
    # Args: param1  (str)       programname
    #       param2  (str)       local filename
    #       param3  (str)       database name of the file
    def ftp_upload(self, programma, filename, dbfilename):
        filehandle = open(self.path + filename + '.mp3', 'rb')
        session = ftplib.FTP(self.ftp_server, self.ftp_username, self.ftp_password)

        try:
            self.status = 'Verbonden met FTP server'
            session.cwd('Uitzendingen/' + programma)
        except ftplib.error_perm:
            session.mkd('Uitzendingen/' + programma)
            session.cwd('Uitzendingen/' + programma)
            self.status = 'Nieuwe map voor ' + programma + ' aangemaakt'

        CHUNKSIZE = 100000
        session.storbinary('STOR ' + (dbfilename + '.mp3'), filehandle, blocksize=CHUNKSIZE)

        self.status = filename + ' met succes opgelsagen onder de volgende naam: ' + dbfilename
        filehandle.close()
        session.quit()

    # =============================================================================
    # FTP Upload XML
    # =============================================================================
    def xml_upload(self):
        file = 'uitzendingen.xml'
        filehandle = open('C:\\Users\\Gebruiker\\Desktop\\Executable Uitzending Gemist\\uitzendingen.xml', 'rb')
        session = ftplib.FTP(self.ftp_server, self.ftp_username, self.ftp_password)

        CHUNKSIZE = 100000
        try:
            self.status = 'Verbonden met FTP server'
            session.cwd('Uitzendingen/')
            session.storbinary('STOR ' + file, filehandle, blocksize=CHUNKSIZE)
            self.status = 'XML met succes geupdate'
        except:
            pass

        filehandle.close()
        session.quit()

    # =============================================================================
    # SQL Handling
    # =============================================================================
    # This method checks weither an hour on a day exists in the database
    # Returns:  str:        programname witch matched our day and hour
    def link_program(self):
        session = mysql.connector.connect(user=self.sql_username, password=self.sql_password,
                                          database=self.sql_database, host=self.sql_server)
        cursor = session.cursor()

        query = "SELECT programmanaam, uur, dag FROM uitzendingen"
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            if str(row[1]) == (datetime.datetime.now(self.timezone) - datetime.timedelta(hours=1)).strftime('%H:00:00')\
                    and str(row[2]) == (datetime.datetime.now(self.timezone).strftime('%w')):
                cursor.close()
                session.close()
                return row[0]
            else:
                continue
        else:
            pass

    # =============================================================================
    # This method prints time and status
    # Used to show program activity
    def update_status(self):
        unix_timestamp = datetime.datetime.now().timestamp()
        local_time = datetime.datetime.fromtimestamp(unix_timestamp, self.timezone)
        r_var = datetime.datetime.strftime(local_time, '%H:%M:%S')
        # No status to show here. Just using this to update the UI.
        self.time = r_var
        self.status = 'Wachten op volgende uitzending...'

    # This method create our database file name
    # Args: param1  (str)       local filename
    # Returns:      (str)       database filename
    def create_file_details(self, filename):
        datehandle = datetime.datetime.fromtimestamp(os.path.getmtime(self.path + filename + '.mp3'),
                                                     self.timezone).strftime('%d%m%Y')
        timehandle = datetime.datetime.strptime(filename[-6:-4], '%H').strftime('%H')
        return str(datehandle) + str(timehandle)

    # This method checks weither the file exists locally
    # Args: param1  (str)       local filename
    # Returns:      (bool)      true if exists false otherwise
    def check_if_exists(self, filename):
        if os.path.isfile(self.path + filename + '.mp3'):
            self.status = 'Het volgende item: ' + filename + '.mp3 gevonden'
            return True
        else:
            self.status = 'Het item: ' + filename + '.mp3 is helaas niet gevonden'
            return False

    # This method links daynumber with Dutch full weekname
    # Returns:      (str)       full Dutch weekname
    def get_day(self):
        day_x = int(datetime.datetime.now(self.timezone).strftime('%w'))
        if day_x == 0:
            return 'Zondag'
        elif day_x == 1:
            return 'Maandag'
        elif day_x == 2:
            return 'Dinsdag'
        elif day_x == 3:
            return 'Woensdag'
        elif day_x == 4:
            return 'Donderdag'
        elif day_x == 5:
            return 'Vrijdag'
        elif day_x == 6:
            return 'Zaterdag'

    # =============================================================================
    # 'Do Something' Method
    # =============================================================================
    # This method does the hourly search for ftp upload and xml update
    # Kind of 'Come Together - Beatles'
    def hour_search(self):
        # Not the efficient way of waiting
        # But wait to run job every hour XX:02
        self.status = 'Twee minuten wachten tot afronden programma opname automatisering'

        # Let's do the upload job
        # First get current hour - 1
        hour_x = (datetime.datetime.now(self.timezone) - datetime.timedelta(hours=1)).strftime('%H')
        # Get the dutch translation of the day name to check filename
        day_name = self.get_day()
        # Get the weeknumber to update XML (USE ISO8601 ELSE: %U)
        weeknumber = (datetime.datetime.now(self.timezone).strftime('%V'))
        filename = 'Programma Opname; ' + day_name + ' ' + hour_x + ' uur'
        # If this audio file exists let's invoke the uploading session
        if self.check_if_exists(filename):
            if not self.link_program():
                pass
            else:
                self.ftp_upload(programma=self.link_program(), filename=filename,
                                dbfilename=self.create_file_details(filename))
                self.update_xml(weeknumber, day_name, self.link_program(),
                                hour_x, ('https://unwdmi.nl:60000/uitzendingen/' + (self.link_program()) + '/' +
                                self.create_file_details(filename) + '.mp3'))
        else:
            pass
        # Clear status
        self.status = ''

    # =============================================================================
    # Schedule all my jobs
    # =============================================================================

    def job_scheduler(self):
        schedule.every(5).seconds.do(self.update_status)
        schedule.every().hour.at(':02').do(self.hour_search)
        schedule.every().hour.at(':08').do(self.xml_upload)

        while True:
            schedule.run_pending()
            sleep(1)
