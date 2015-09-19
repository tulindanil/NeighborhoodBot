import sys, os, time, atexit, logging
from signal import SIGTERM

class Daemon:
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
    
    def daemonize(self):
        
        try:
            
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
    
        except OSError, e:
            
            logging.error("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        logging.info("Ready for second fork")
        
        try:
            
            pid = os.fork()
            if pid > 0:
                sys.exit(0)

        except OSError, e:
        
            logging.error("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        
        logging.info("forked")
        
        sys.stdout.flush()
        sys.stderr.flush()
        
        logging.info("flushed")
        
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        logging.info("dupped")
        
        atexit.register(self.delpid)
        
        try:
        
            pid = str(os.getpid())
        
        except OSError, e:
            
            logging.error("pid getting failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        
        try:
            file(self.pidfile, 'w+').write("%s\n" % pid)
        except Exception as e:
            logging.errno("Failed to write to pid file %s" % e.strerror)
                
        logging.info("created pid file")

    def delpid(self):
        
        os.remove(self.pidfile)
    
    def start(self):
        
        try:
            
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        
        except IOError:
            
            pid = None
        
        if pid:
            
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        logging.info("Staring daemonazing")
        self.daemonize()
        logging.info("Daemonazied")
        
        self.run()
    
    def stop(self):
        
        try:
            
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        
        except IOError:
            
            pid = None
        
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return
        
        try:
            
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
    
        except OSError, err:
            
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        
        self.stop()
        self.start()

    def status(self):
        
        try:
            
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        
        except IOError:
            
            pid = None
        
        if not pid:
            print 'Daemon is not running'
            return
        
        print 'Daemon is running'

