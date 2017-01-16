__author__ = 'Jackson'

'''
This script accesses the event data for the upcoming shows at Fiske Planetarium and notifies the user if any shows have
been added or modified since the script's last execution.
'''

import urllib2
from BeautifulSoup import BeautifulSoup
import HTMLParser
import datetime
from time import strptime
import numpy
import ctypes
import sys

#helper method for events that are shown for multiple days
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

#taken from user2140260's comment @ http://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python
#displays information in a popup window
def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxW(0, text, title, style)

#this function gets all of the current events and stores them in a dictionary
def getCurrentShows():
    currentShows = {}

    #connect to the website and get all the html data
    url = 'http://www.calendarwiz.com/calendars/ucfeeder.php?crd=fiske&theme=Master%20Theme&uc_hideloc=1'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    text = response.read()
    soup = BeautifulSoup(text)

    #the event data is stored in 'td' tags where the 'class' attribute is 'cwuceeventtitle'
    data = soup.findAll('td',attrs={'class':'cwuceeventtitle'})

    #loop through each td in the data and extract the necessary information
    for td in data:
        title = HTMLParser.HTMLParser().unescape(td.find('a').contents[0])
        link = td.find('a')['href']
        date = td.findAll('div', text=True)[2]
        split = date.split(" ")

        #shows that span more than one day appear as one event on the website, but I chose to store each showing as a
        #different event in the dictionary
        if 'to' in date:    #shows that span more than one day have a 'to' in the date
            firstMonth = split[2]
            firstDayOfMonth = split[3]
            secondMonth = split[6]
            secondDayOfMonth = split[7].strip(',')
            year = split[8]
            startTime = split[11]
            endTime = split[13]
            startDate = datetime.date(int(year), strptime(firstMonth, '%b').tm_mon, int(firstDayOfMonth))
            endDate = datetime.date(int(year), strptime(secondMonth, '%b').tm_mon, int(secondDayOfMonth))
            for single_date in daterange(startDate, endDate):
                dayOfWeek = single_date.strftime("%a")
                dayOfMonth = single_date.strftime("%d").lstrip("0")
                month = single_date.strftime("%b")
                year = single_date.strftime("%Y")
                time = dict([('Day of the Week', dayOfWeek), ('Day of the Month', dayOfMonth), ('Month', month),
                             ('Year', year), ('Start Time', startTime), ('End Time', endTime)])
                show = dict([('Title', title), ('Link', link), ('Date', time)])
                key = dayOfMonth + '.' + month + '.' + year + '.' + startTime
                currentShows[key] = show

        #code for extracting single day event data
        else:
            dayOfWeek = split[1].strip(',')
            month = split[2]
            dayOfMonth = split[3].strip(',')
            year = split[4]
            startTime = split[7]
            endTime = split[9]
            time = dict([('Day of the Week', dayOfWeek), ('Day of the Month', dayOfMonth), ('Month', month),
                             ('Year', year), ('Start Time', startTime), ('End Time', endTime)])
            show = dict([('Title', title), ('Link', link), ('Date', time)])
            key = dayOfMonth + '.' + month + '.' + year + '.' + startTime
            currentShows[key] = show

    return currentShows

#this function gets the shows that are new or have been changed
def getNewShows(oldShows, currentShows):
    newShows = []
    changedShows = []

    #loop through all of the current shows comparing them with the stored shows
    for key, show in currentShows.iteritems():

        #if a show does not appear in the stored events, it is new
        if oldShows.get(key) is None:
            newShows.append(show)

        #if a show appears in the stored events but has a different title, it has been modified
        else:
            oldShow = oldShows.get(key)
            if oldShow.get('Title') != show.get('Title'):
                changedShows.append(show)
    return [newShows, changedShows]

#this function formats the data to display to the user
def formatText(newShows, changedShows):
    text = u''
    if newShows:
        text += 'New Shows:\n'
        for show in newShows:
            formatIndividualShowText(show)
    if changedShows:
        text += 'Updated Shows:\n'
        for show in changedShows:
            formatIndividualShowText(show)
    if text == '':
        text = u'No New Shows'
    return text

#this function formats the text of individual shows
def formatIndividualShowText(show):
    text = u''
    title = show.get('Title')
    #link = show.get('Link')
    date = show.get('Date')
    dayOfWeek = date.get('Day of the Week')
    dayOfMonth = date.get('Day of the Month')
    month = date.get('Month')
    year = date.get('Year')
    startTime = date.get('Start Time')
    endTime = date.get('End Time')
    text += title + "\n"
    text += (dayOfWeek + " " + month + " " + dayOfMonth + ", " + year + " from " + startTime + " - " + endTime + "\n\n")
    return text


#main

#try loading the previous event data from the file 'shows.npy'
try:
    oldShows = numpy.load('shows.npy').item()
#if the file does not exist, create the file and store the current event data in it
#then alert the user and exit
except IOError:
    numpy.save('shows.npy', getCurrentShows())
    alert = u'No previous event data was detected.\n'
    alert += 'The current event data has been saved, and the script should work as intended.'
    Mbox(u'Alert', alert, 1)
    sys.exit()
currentShows = getCurrentShows()    #get the shows currently listed on the Fiske Planetarium website
data = getNewShows(oldShows, currentShows)  #get the shows that are new or modified
newShows = data[0]
changedShows = data[1]
text = formatText(newShows, changedShows)   #format the information for display to the user
Mbox(u'New Shows at Fiske Planetarium', text, 1)    #display the information
numpy.save('shows.npy', currentShows)   #save the current event data in the file 'shows.npy'


#example show for testing
'''
show = {}
show['Title'] = 'Test'
show['Link'] = 'test.test'
show['Date'] = {}
show['Date']['Day of the Week'] = 'Tue'
show['Date']['Day of the Month'] = '17'
show['Date']['Month'] = 'Feb'
show['Date']['Year'] = '1996'
show['Date']['Start Time'] = '12:00pm'
show['Date']['End Time'] = '1:00pm'
'''




