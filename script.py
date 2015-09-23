import time, sys, os, logging, datetime, json
from daemon import Daemon
import collections

import telegram

class hardware:
    
    @staticmethod
    def getTemperature():
        
        filepath = '/sys/devices/w1_bus_master1/28-0000052c4b73/w1_slave'
        f = open(filepath, 'r')
        data = f.read()
        f.close()
        
        return float(data[data.find('t=')+2:])/1000

class Worker(Daemon):

    def main_loop(self, bot):
    
        updates = bot.getUpdates()
            
        if len(updates) == 0:
            return
            
        update_id = updates[len(updates) - 1].update_id
        bot.getUpdates(update_id + 1)
        
        messages = [u.message for u in updates]
        
        for m in messages:
            
            if m.text == self.start:
                
                bot.sendMessage(m.from_user.id, 'Good day!', reply_markup = telegram.ReplyKeyboardHide())
            
            elif m.text == self.temp:
                
                bot.sendMessage(m.from_user.id, str(hardware.getTemperature()), reply_markup = telegram.ReplyKeyboardHide())
        
            elif m.text == self.help:
            
                bot.sendMessage(m.from_user.id, 'You can control me by sending these commands:\n /temp - current temp in Dan\'s room', reply_markup = telegram.ReplyKeyboardHide())
    
            else:
                
                bot.sendMessage(m.from_user.id, 'Sorry, I dont understand you :(', reply_markup = telegram.ReplyKeyboardHide())

    def run(self):
    
        logging.info('ready for running')
        
        token = ''
        
        try:
            f = open('/etc/SmartHome/.auth.info')
            token = f.read()[:-1]
        except:
            logging.error('Auth.info not provided')
            sys.exit(2)

        logging.info('Got token')

        bot = telegram.Bot(token)

        self.temp = '/temp'
        self.start = '/start'
        self.help = '/help'

        while 1:
            try:
                self.main_loop(bot)
            except Exception as e:
                logging.error(e)

if __name__ == '__main__':

    worker = Worker('/tmp/neighborhoodBot.pid')

    logfile = '/home/pi/SmartHomeBot.log'
    logging.basicConfig(format = '%(asctime)s:%(levelname)s:%(message)s' ,level = logging.WARNING)
    
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            if os.path.exists(logfile):
                os.remove(logfile)
            worker.start()
        
        elif 'stop' == sys.argv[1]:
            worker.stop()
        
        elif 'restart' == sys.argv[1]:
            worker.restart()
        
        elif 'status' == sys.argv[1]:
            worker.status()
        
        else:
            print "Unknown command"
            sys.exit(2)
        
        sys.exit(0)
    
    elif len(sys.argv) == 3:

        if os.path.exists(logfile):
            os.remove(logfile)

        worker.run()

    else:
        
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)
