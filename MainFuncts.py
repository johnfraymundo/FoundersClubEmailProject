
import emailFunctions as efunct

#If given more time, would incorporate a "direct from email" sourcing method for filename
filename= "library checkout receipt.eml"
testfilename2 = "Fw_ library checkout receiptexample2.eml"
actionableinfo = efunct.eml_processor(filename)

def customNotifications():
    pass

def main():

    if efunct.sendDates(actionableinfo) == "dueinday":
        efunct.emailReminders(actionableinfo, None, None, "normal")
    elif efunct.sendDates(actionableinfo) == "weekreminder":
        efunct.emailReminders(actionableinfo, None, None, "dueinweek")
    elif efunct.sendDates(actionableinfo) == "late":
        efunct.emailReminders(actionableinfo, None, None, "late")
    else:
        pass

if __name__ == "__main__":
    main()
