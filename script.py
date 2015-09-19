import time, sys, os, logging, datetime
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

        while 1:
        
            try:
        
                updates = bot.getUpdates()

                if len(updates) > 0:
                    
                    update_id = updates[len(updates) - 1].update_id
                    messages = [u.message for u in updates]

                    for m in messages:

                        if m.text == temp:
                            bot.sendMessage(m.from_user.id, str(hardware.getTemperature()))
                        elif m.text == schedule:
                        
                            schedule = json.load(open('schedule.json').read())
                        
                        elif m.text == today:
                        
                            bot.sendMessage(m.from_user.id, 'Your schedule:')
                            weekday = datetime.datetime.today().weekday()
                        
                            schedule = json.load(open('schedule.json').read())
                        
                            for lesson in schedule[str(weekday)]:
                                bot.sendMessage(m.from_user.id, "%s %s : %s" % (lesson['time'], lesson['subject'], lesson['place']))
                        
                        else:
                            bot.sendMessage(m.from_user.id, 'It\'s not supported now')

                    bot.getUpdates(update_id + 1)

            except Exception as e:
                logging.error(e)


if __name__ == '__main__':

    worker = Worker('/tmp/neighborhoodBot.pid')

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
