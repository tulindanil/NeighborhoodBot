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

class schedule:

    @staticmethod
    def getDescription(weekday):

        raw = open('/home/pi/NeighborhoodBot/schedule.json')
        data = json.load(raw)
        raw.close()
            
        answer = ""
                
        try:
            day = data[str(weekday)]
            answer = "Your schedule :\n"
            
            day_sorted = collections.OrderedDict(sorted(data.items()))
            
            for lesson in day_sorted:
                answer += "%s - %s: %s\n" % (day_sorted[lesson]['time'], day_sorted[lesson]['subject'], day_sorted[lesson]['place'])
        except Exception as e:
            print e.strerror
            answer = "I think you got a dayoff!"

        return answer

class storage:

    @staticmethod
    def addUser(user):

        try:

            filepath = '/etc/NeighborhoodBot/users.json'
            f = open(filepath, 'r')
            
            data = {}
            
            try:
                data = json.load(f)
            except:
                data = {}

            try:
                index = data.index(user.to_json())
            except:
                data[str(user.id)] = user.to_json()
                f.close()
                f = open(filepath, 'w')
                f.write(json.dumps(data))

            f.close()

        except Exception as e:

            logging.error('Failed to write in user file: %s', e)

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
                
                bot.sendMessage(m.from_user.id, 'Good day!')
                storage.addUser(m.from_user)
            
            elif m.text == self.temp:
                
                bot.sendMessage(m.from_user.id, str(hardware.getTemperature()))
        
            elif m.text in self.weekdays:
                
                bot.sendMessage(m.from_user.id, schedule.getDescription(self.weekdays.index(m.text) + 1))
            
            elif m.text == self.today:
                
                weekday = datetime.datetime.today().weekday()
                bot.sendMessage(m.from_user.id, schedule.getDescription(weekday))
    
            else:
                
                bot.sendMessage(m.from_user.id, 'Sorry, I dont understand you :(')

    def run(self):
    
        logging.info('ready for running')
        
        token = ''
        
        try:
            f = open('/etc/NeighborhoodBot/.auth.info')
            token = f.read()[:-1]
        except:
            logging.error('Auth.info not provided')
            sys.exit(2)

        logging.info('Got token')

        bot = telegram.Bot(token)

        self.temp = '/temp'
        self.today = '/today'
        self.start = '/start'
        
        self.weekdays = ['/tuesday', '/wednesday', '/thursday', '/friday', '/saturday']
        self.dayoffs = ['/monday', '/sunday']

        while 1:
            
            try:
                self.main_loop(bot)
            except Exception as e:
                logging.error(e)

if __name__ == '__main__':

    worker = Worker('/tmp/neighborhoodBot.pid')

    logfile = 'neighbourhoodBot.log'
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
