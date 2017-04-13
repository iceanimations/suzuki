'''

 Author: Alex Baker
 Date: 7th July 2008
 Description : Simple python program to generate wrap as a service based on example on the web, see link below.

 http://essiene.blogspot.com/2005/04/python-windows-services.html

 Modified by: Talha Ahmed for ICE Animations
 Date:

 Usage : python vboxservice.py install
 Usage : python vboxservice.py start
 Usage : python vboxservice.py stop
 Usage : python vboxservice.py remove

 C:\>python vboxservice.py  --username <username> --password <PASSWORD> --startup auto install

'''

import win32service
import win32serviceutil
import win32api
import win32event
import logging
import os
import threading
import json
import suzuki

current_dir = os.path.dirname(__file__)
log_file = os.path.join(current_dir, 'SuzukiService.log')
logging.basicConfig(filename=os.path.join(current_dir, 'SuzukiService.log'),
        level=logging.INFO)

config = {}
json_file = os.path.join(current_dir, 'SuzukiService.json')
if os.path.exists(json_file):
    with open(json_file) as jfile:
        config = json.load(jfile)
        logging.info('config read from file: %s as %r'%(json_file, config))
else:
    logging.warning('config file not found at: %s!' % json_file)


class SuzukiService(win32serviceutil.ServiceFramework):
    "VBoxService - A mechanism for running VBox VMs at the startup of machine"

    _svc_name_ = "SuzukiService"
    _svc_display_name_ = "SuzukiService"
    _svc_description_ = "SuzukiService"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def start(self):
        logging.info('Starting Suzuki Server ...')
        self.server = suzuki.SuzukiServer(**config)
        self.thread = threading.Thread(target=self.server.run)
        self.thread.daemon = True
        self.thread.start()
        logging.info('Suzuki Server Running')

    def stop(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        if self.thread.isAlive():
            logging.error('Suzuki Server not shutting down')
        else:
            logging.info('Suzuki Server has shutdown')

    def SvcDoRun(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            logging.info('Starting Suzuki Server in a thread ...')
            self.start()
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            logging.info('Suzuki Server running in a thread!')
            win32event.WaitForSingleObject(self.stop_event,
                    win32event.INFINITE)
        except Exception as e:
            logging.error('Error Encountered: %s' % str(e))

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop()
        win32event.SetEvent(self.stop_event)

def ctrlHandler(ctrlType):
    return True

if __name__ == '__main__':
    win32api.SetConsoleCtrlHandler(ctrlHandler, True)
    win32serviceutil.HandleCommandLine(SuzukiService)
