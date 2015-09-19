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

class Worker(Daemon):

    def run(self):
    
        logging.info('ready for running')
    
        f = open('/tmp/.auth.info')
        token = f.read()[:-1]

        logging.info('Got token')

        bot = telegram.Bot(token)

        temp = '/temp'
        schedule = '/schedule'
        today = '/today'
        
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
                        
                        if m.text == temp:
                            
                            waiting_for_weekday = 0
                            bot.sendMessage(m.from_user.id, str(hardware.getTemperature()))
                        
                        elif m.text == schedule:
                        
                            waiting_for_weekday = 1
                            
                            answer = 'In what day are you interested in?\n'
                            for day in weekdays:
                                answer += '%s ' % day
                                    
                            bot.sendMessage(m.from_user.id, answer)
                        
                        
                        elif m.text == today or waiting_for_weekday:
                            
                            weekday = 0
                            
                            if m.text == today:
                                weekday = datetime.datetime.today().weekday()
                            else:
                                try:
                                    weekday = weekdays.index(m.text) + 1
                                except:
                                    try:
                                        weekday = weekdays.index(m.text) + 1
                                    except:
                                        bot.sendMessage(m.from_user.id, 'Hey, there is no such day!')
                        
                            waiting_for_weekday = 0
                            
                            raw = open('schedule.json')
                            data = json.load(raw)
                            raw.close()
                            
                            answer = ""
                            
                            try:
                                day = data[str(weekday)]
                                
                                answer = "Your schedule :\n"
                                
                                for lesson in day:
                                    answer += "%s - %s: %s\n" % (day[lesson]['time'], day[lesson]['subject'], day[lesson]['place'])
                            except:
                                answer = "I think you got a dayoff!"
                        
                            bot.sendMessage(m.from_user.id, answer)

                        else:
                            
                            bot.sendMessage(m.from_user.id, 'Try again, just do it!')
        
            except Exception as e:
                
                logging.error(e)

if __name__ == '__main__':

    worker = Worker('/tmp/neighborhoodBot.pid')

    worker.run()

    logfile = 'neighbourhoodBot.log'
    
    if os.path.exists(logfile):
        os.remove(logfile)

    logging.basicConfig(format = '%(asctime)s:%(levelname)s:%(message)s' ,level = logging.INFO, filename = logfile)
    
    if len(sys.argv) == 2:
        
        if 'start' == sys.argv[1]:
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
    
    else:
        
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)
