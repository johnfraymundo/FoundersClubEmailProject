
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import eml_parser
import re
import smtplib
import datetime


"""

ugly code but it works, if given more time would make really sexy for all possible library 
reciept email variations for different libraries
to handle outliers.

Would convert to class and method structure in future to reduce redundancy using get methods
instead of returning dictionary to make things seamless 

"""

def eml_processor(filename):
    """
    input of filename
    opens .eml file from project library root (would source eml file directly from email in the future) and processes it through
    the email library where it is separated into header information dict and body information dict. Header info contains contact info for the sender and receiver and
    other useful data. While body information includes library info like the name of the library, associated fees, etc and book information which is decomposed from html using
    beautiful soup
    """
    with open(filename) as f:
       emailInfoDict = eml_parser.eml_parser.decode_email(filename, True)   #Mostly to retrieve header info and body info

    #email header info and body sections split into two dicts
    ########################################################################
    content = emailInfoDict["body"][0]["content"]
    headerinfo = emailInfoDict["header"]                                    #associated keys of header portion of emailInfoDict are 'received_domain', 'received_foremail', 'date', 'received', 'from', 'subject', 'received_ip', 'header', 'to', 'delivered_to'
    ########################################################################

    #Header and Contact information decomposer
    ########################################################################
    emailDate = str(headerinfo["date"])
    emailfrom = str(headerinfo["from"])
    emailto = str(headerinfo["to"][0])
    emailSubject = str(headerinfo["subject"])
    ########################################################################

    #Email Body Decomposer
    ########################################################################
    soup = BeautifulSoup(content, 'html.parser')
    library = striphtml(str(soup.center.contents[0]))
    contact = str(soup.h3.string)
    h4data = soup.findAll("h4")

    checkedoutdata = (h4data[0].string)
    finesfeesowed = str(h4data[1].string)
    TotalChecked = str(h4data[2].string)
    bookstatus = str(h4data[3].string)
    bookdata = striphtml(str(h4data[4]))
    #########################################################################
    #Book Data Decomposer
    #########################################################################
    processedbd = str.splitlines(bookdata)

    for x in processedbd:
        if (x == ''):
            processedbd.remove(x)
        x.strip()

    title = processedbd[0].strip().strip("Title:")
    barcode = processedbd[1].strip().strip("Barcode:")
    duedate = processedbd[2].strip().strip("Due Date:")


    headerDict = {"DateRecieved":emailDate, "libraryEmail":emailfrom, "library":library, "librarynumber":contact, "UserEmail":emailto, "EmailSubject":emailSubject}
    contentDict = {"CheckoutDate":checkedoutdata, "fines":finesfeesowed, "#bookscheckedout":TotalChecked, "bookstatus":bookstatus, "title":title, "duedate":duedate, "barcode":barcode}
    return [headerDict,contentDict]

def striphtml(data):
    """
    Strips html headers
    """
    p = re.compile(r"<.*?>")
    return p.sub("", data)


def emailReminders(actionableinfo, custommessage, customsub, remindertype):
    """
    input of [headerDict,contentDict], custommessage string, customsub string, and reminder type
    uses various templates for the type of notificaiton
    generates email using said templates
    sends email using the custom gmail account I made
    """
    a = actionableinfo

    destination = a[0]["UserEmail"]
    gmailAccount = "FoundersClubProjectTestEmail@gmail.com"
    password = "gobuild!"

    remindertemplate = "Hi {} your book {} was taken out on {} from {} and is due on {}.".format(a[0]["UserEmail"], a[1]["title"], a[1]["CheckoutDate"], a[0]["library"], a[1]["duedate"]  )
    latetemplate = "Hi {} your book {} is currently OVERDUE and was taken out on {} and was due on {}. \n Please return your book to {} \n Here is their contact information: \n Phone# and Email:{}".format(a[0]["UserEmail"], a[1]["title"], a[1]["CheckoutDate"], a[1]["duedate"], a[0]["library"], a[0]["librarynumber"])
    feeremindertemplate = "Hi {} you currently have fees from {} ammounting to {}.".format(a[0]["UserEmail"], a[0]["library"], a[1]["fines"])

    subtemplate = "Book Return Reminder for {}".format(a[1]["title"])
    due_week_subtemplate = "You've got a book due in a week!"
    latesubtemplate = "{} is OVERDUE".format(a[1]["title"])
    feesubtemplate = "You have unpaid fees from {}".format(a[0]["library"])
    currentbooktakeoutsub = "Here are the books you've currently have taken out!"

    if (remindertype == "normal"):
        message = remindertemplate
        subject = subtemplate
    elif (remindertype == "late"):
        message = latetemplate
        subject = latesubtemplate
    elif (remindertype == "custom"):
        message = custommessage
        subject = customsub
    elif (remindertype == "feereminder"):
        message = feeremindertemplate
        subject = feesubtemplate
    elif (remindertype == "currentBookTakenout"):
        message = custommessage
        subject = currentbooktakeoutsub
    elif (remindertype == "dueinweek"):
        message = remindertemplate
        subject = due_week_subtemplate
    else:
        message = remindertemplate
        subject = subtemplate

    msg = MIMEMultipart()
    msg["From"] = gmailAccount
    msg["To"] = destination
    msg["Subject"] = subject

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(gmailAccount, password)
    text = msg.as_string()
    server.sendmail(gmailAccount, destination, text)
    server.quit()

def sendDates(actionableinfo):
    """

    Input of [headerDict, contentDict]
    Decides appropriate reminder based on current date and difference between duedate and currentdate

    """
    act = actionableinfo
    today_date = datetime.datetime.now()
    # to test dates set today_date equal to this template "08/23/2018" or "MM/DD/YYYY" change the dates however you like
    #tform = "%m/%d/%Y"
    #convert_today = datetime.datetime.strptime(today_date, form)

    due_date = act[1]["duedate"].rsplit(",")[0]
    form = "%m/%d/%Y"
    converted_form = datetime.datetime.strptime(due_date, form) - datetime.timedelta(days = 1)

    #if running custom date replace today_date with convert_today 
    if(today_date == converted_form):
        return "dueinday"
    elif(today_date > converted_form):
        return "late"
    elif(days_between(today_date,converted_form) == 7):
        return "weekreminder"
    else:
        return "not due today"

def days_between(d1, d2):
    """

    Input of today's date and duedate
    Calculates difference between dates

    """
    return (d2 - d1).days
