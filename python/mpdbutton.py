
import time
import datetime
import RPIO
import classes.classErrorLog as errorLog
import configuration as conf
import sys
import subprocess
import re
import time
import RPi.GPIO as GPIO

currentTime = time.strftime("%H:%M:%S", time.localtime())
currentDate = time.strftime("%Y-%m-%d", time.localtime())
currentDay = datetime.datetime.today().weekday()
currentDateTime = datetime.datetime.now()


## Internet radio stations
wwoz=subprocess.check_output('/home/pi/get_m3u_stream.sh http://wwoz-sc.streamguys.com/wwoz-hi.mp3.m3u',shell=True)

fip=subprocess.check_output('/home/pi/get_m3u_stream.sh http://www.tv-radio.com/station/fip_mp3/fip_mp3-128k.m3u',shell=True)



busts={'02005CC4D44E':'strauss','020059093B69':'brahms','020058053D62':'chopin','10005E2C0062':'handel','8500ABEF14D5':'debussy','15007B58C9FF':'lizst','020019707F14':'tchaikovsky','020031B044C7':'bach','0E0023743F66':'beethoven','8500AA681F58':'mozart','020059F4A20D':'jazz','FILLIN':wwoz,'FILLIN2':fip}

errorCount = 0
button_pin=18
sleep_time=0.05

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin,GPIO.IN)
input = GPIO.input(button_pin)

def getMpdStatus():
    shell_status=subprocess.check_output('mpc status -f %file%',shell=True)
    shell_status=re.split('\n',shell_status)
    play_status=re.sub('^\[|\].*','',shell_status[1])
    if(len(shell_status)==2):
        return('stopped')
    elif(play_status=='playing'):
        return('playing'+'~'+re.sub('/.*','',shell_status[0]))
    elif(play_status=='paused'):
        return('paused'+'~'+re.sub('/.*','',shell_status[0]))

mpdstatus=getMpdStatus()


#initialise a previous input variable to 0 (assume button not pressed last)
def buttonLogic():
    prev_input=0
    button_wait_time=1
    elapsed_time=0
    button_press_count=0
    mpdstatus=getMpdStatus()
    while True:
        #take a reading
        input = GPIO.input(button_pin)
        #if the last reading was low and this one high, print
        if ((not prev_input) and input):
            print("Button pressed")
            button_press_count+=1
            elapsed_time=0.001
        if (elapsed_time>button_wait_time and button_press_count >= 3):
            print('button pressed thrice')
            subprocess.call('mpc stop',shell=True)
            subprocess.call('mpc clear',shell=True)
            mpdstatus='stopped'
            elapsed_time=0
            button_press_count=0
            #try:
            #    print(readCard())
            #except:
            #    print('failed')
        if (elapsed_time>button_wait_time and button_press_count == 2):
            print('button pressed twice')
            subprocess.call('mpc next',shell=True)
            mpdstatus=getMpdStatus()
            elapsed_time=0
            button_press_count=0
        if (button_press_count>0 and elapsed_time>button_wait_time and mpdstatus=='stopped' or (elapsed_time>button_wait_time and button_press_count == 1)):
            print('button pressed once')
            if(re.sub('~.*','',mpdstatus)=='playing'):
                subprocess.call('mpc pause',shell=True)
                mpdstatus=getMpdStatus()
            elif(re.sub('~.*','',mpdstatus)=='paused'):
                subprocess.call('mpc play',shell=True)
                mpdstatus=getMpdStatus()
            else:
                card_read=False
                while card_read==False:
                    print('read from rfid until one is found')
                    try:
                        ret=readCard()
                        if ret !='failed':
                            print('playing')
                            subprocess.call('mpc add '+ret,shell=True)
                            subprocess.call('mpc play',shell=True)
                            mpdstatus=getMpdStatus()
                            card_read=True
                    except:
                        print('failed')
            elapsed_time=0
            button_press_count=0
        #update previous input
        prev_input = input
        #add time to elapsed_time count
        if (button_press_count>0):
            elapsed_time+=sleep_time
        #slight pause to debounce
        time.sleep(sleep_time)


def readCard():
    conf.ser.open()
    if conf.ser.isOpen():
        print "Open: " + conf.ser.portstr
    global errorCount
    elapsed_time=0
    try:
        while elapsed_time<0.2:
            elapsed_time+=sleep_time
            conf.ser.flushInput()
            rfidData = conf.ser.readline().strip()
            if len(rfidData) > 0:
                rfidData = rfidData[1:13]
                print "Card Scanned: ", rfidData, ' ', busts[rfidData], len(busts[rfidData])
                if(len(busts[rfidData])>0):
                    return(busts[rfidData])
    except:
        errorLog.classErrorLog(sys.exc_info())
    finally:
        conf.ser.close()
        conf.db.close()
        RPIO.cleanup()


if __name__ == '__main__':
    #readCard()
    subprocess.call('mpc clear',shell=True)
    subprocess.call('mpc stop',shell=True)
    buttonLogic()



