import time, sys, os, logging
from daemon import Daemon

import telegram

class Worker(Daemon):

    def run(self):

        f = open('auth.info')
        token = f.read()[:-1]

        bot = telegram.Bot(token)

        temp = '/temp'

#        bot.sendMessage(55978, 'hello')

        while 1:
        
            updates = bot.getUpdates()

            if len(updates) > 0:
                
                update_id = updates[len(updates) - 1].update_id
                messages = [u.message for u in updates]

                for m in messages:

                    if m.text == temp:
                        bot.sendMessage(m.from_user.id, '23.0')

                bot.getUpdates(update_id + 1)



if __name__ == '__main__':

    worker = Worker('./neighborhoodBot.pid')

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
