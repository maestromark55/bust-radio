import time
import datetime
import RPIO as RPIO
import classes.classErrorLog as errorLog
import configuration as conf


########################################################################################################################
## Setup static variables


currentTime = time.strftime("%H:%M:%S", time.localtime())
currentDate = time.strftime("%Y-%m-%d", time.localtime())
currentDay = datetime.datetime.today().weekday()
currentDateTime = datetime.datetime.now()

errorCount = 0

conf.ser.open()

if conf.ser.isOpen():
    print "Open: " + conf.ser.portstr


def readCard():
    global errorCount
    try:
        #LED("blue")
        while True:
            conf.ser.flushInput()
            #LED("blue")
            rfidData = conf.ser.readline().strip()
            #print "Line: "
            if len(rfidData) > 0:
                rfidData = rfidData[1:13]
                print "Card Scanned: ", rfidData
                #print findTag(rfidData)

    except:
        errorLog.classErrorLog(sys.exc_info())

    finally:
        conf.ser.close()
        conf.db.close()
        RPIO.cleanup()


########################################################################################################################

def LED(colorON):
        if colorON == "green":
            RPIO.output(conf.GREEN, True)
            RPIO.output(conf.RED, False)
            RPIO.output(conf.BLUE, False)
            time.sleep(1)

        elif colorON == "red":
            RPIO.output(conf.GREEN, False)
            RPIO.output(conf.RED, True)
            RPIO.output(conf.BLUE, False)
            time.sleep(1)

        elif colorON == "blue":
            RPIO.output(conf.GREEN, False)
            RPIO.output(conf.RED, False)
            RPIO.output(conf.BLUE, True)

        else:
            return "Error"


###################################################################################################################

if __name__ == '__main__':
    readCard()
