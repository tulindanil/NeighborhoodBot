import time, sys, os, logging, datetime, json
from daemon import Daemon

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
            for lesson in day:
                print lesson
                answer += "%s - %s: %s\n" % (day[lesson]['time'], day[lesson]['subject'], day[lesson]['place'])
        except:
            answer = "I think you got a dayoff!"

        return answer

class storage:

    @staticmethod
    def addUser(user):

        try:

            filepath = '/etc/NeighborhoodBot/users.json'
            f = open(filepath, 'r')
            data = json.load(f.read())

            try:
                index = data.index(user.to_json())
            except:
                data.append(user.to_json())
                f = open (filepath, 'w')
                f.write(data)
                    
            f.close()

        except Exception as e:

            logging.error('Failed to write in user file: %s', e)

class Worker(Daemon):

    def run(self):
    
        logging.info('ready for running')
    
        f = open('/etc/NeighborhoodBot/.auth.info')
        token = f.read()[:-1]

        logging.info('Got token')

        bot = telegram.Bot(token)

        temp = '/temp'
        today = '/today'
        start = '/start'
        
        weekdays = ['/tuesday', '/wednesday', '/thursday', '/friday', '/saturday']
        dayoffs = ['/monday', '/sunday']

        waiting_for_weekday = 0

        while 1:
            
            updates = bot.getUpdates()
            
            try:

                if len(updates) > 0:
                    
                    update_id = updates[len(updates) - 1].update_id
                    bot.getUpdates(update_id + 1)
                    
                    messages = [u.message for u in updates]
                    
                    for m in messages:
                        
                        storage.addUser(m.from_user)
                        
                        if m.text == start:
                        
                            bot.sendMessage(m.from_user.id, 'Good day!')
#                            storage.addUser(m.from_user)

                        elif m.text == temp:
                            
                            bot.sendMessage(m.from_user.id, str(hardware.getTemperature()))
                    
                        elif m.text in weekdays:
                        
                            bot.sendMessage(m.from_user.id, schedule.getDescription(weekdays.index(m.text) + 1))
                        
                        elif m.text == today:
                            
                            weekday = datetime.datetime.today().weekday()
                            bot.sendMessage(m.from_user.id, schedule.getDescription(weekday))

                        else:
                            
                            bot.sendMessage(m.from_user.id, 'Sorry, I dont understand you :(')
        
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
