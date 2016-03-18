#!/usr/bin/env python

#Written by Roger Fachini
#Startup script located at /etc/init/githttpstartup.conf

import logging
import socket
import SimpleHTTPServer
import SocketServer
import json
import time
import os
import commands
import cgi

IP = ''
PORT = 80
BASE_DIR =  '/robotics/services/pvcs/'
LOG_DIR = '/robotics/logs/pvcs/'
HTML_DIR = 'html/'
GIT_DIR = '/robotics/git/'
LATEST_LOG = '/robotics/logs/latest-pvcs.log'

REDIRECTS = {'/':'index.htm'}
fileData = {'__data': {'ip':'Null'}}

NEW_REPO_CMD = 'bash /robotics/scripts/makeHub.sh'
NEW_LOCAL_CMD = 'bash /robotics/scripts/makeHubLocal.sh'
RESYNC_CMD = 'bash /robotics/scripts/syncGit.sh'

MACHINE_IP = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    global main
    def do_GET(self):
        self.log_message('Getting path: %s',self.path)
        if self.path == '/customData.json':
            self.send_response(200)
            self.send_header("Content-type", 'application/json')
            self.end_headers()
            reloadFileList()
            fileData.update({'__data': {'ip':MACHINE_IP}})
            self.wfile.write(json.dumps(fileData))
            return

        elif self.path in REDIRECTS.iterkeys():
            self.path = REDIRECTS[self.path]

        self.path = HTML_DIR+self.path
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        print(self.path)
        if self.path =='/newRepo':
            self.send_response(301)
            self.send_header('Location','versionControl.htm')
            self.end_headers()
            print postvars
            if postvars['name'] == ['']:return
            private = postvars['public'] == ['false']
            name=postvars['name'][0]
            name = name.replace(' ','_')
            dir = '%s/%s.git'%(GIT_DIR, name)
            makeNewGitRepo(dir, private)

        elif self.path =='/resync':
            self.send_response(301)
            self.send_header('Location','versionControl.htm')
            self.end_headers()
            resyncGit()

    def log_message(self, format, *args):
        log = logging.getLogger('handler')
        log.info("%s %s" %
                     (self.client_address[0],
                      format%args))


def reloadFileList():
    global fileData 
    fileData = {'__data': {'ip':'Null'}}
    for f in os.listdir(GIT_DIR):
        if not f.endswith('.git'): continue
        if os.path.isfile(GIT_DIR+f+'/no-github-sync'): state = 'Local'
        else: state = 'Public'
        date = time.ctime(os.path.getmtime(GIT_DIR+f+'/git-daemon-export-ok'))
        ip = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
        link = 'git@server:/opt/git/%s'%f
        fileData.update({f:{'path':GIT_DIR+f, 
                            'date':date,
                            'link':link,
                            'state':state}})

def makeNewGitRepo(dir, localR=False):
    if localR:
        cmd = NEW_LOCAL_CMD
    else:
        cmd = NEW_REPO_CMD
    log = logging.getLogger('server')
    log.info('Running git init script: %s'%cmd)
    name = dir.split('/')
    name = name[-1]
    
    status = os.system(cmd+' %s'%name) 
    if status == 0:
        log.info('Success!')
    else:
        log.error('Failure: command returned status code of %s', status)

def resyncGit():
    log = logging.getLogger('server')
    log.info('Running git resync ')
    status = os.system(RESYNC_CMD)
    log.info('done')


class Main:
    def __init__(self, ip, port):
        reloadFileList()
        logger = logging.getLogger('server')
        logger.info('Starting server on %s:%s',ip,port)
        server = SocketServer.TCPServer((ip, port), Handler)
        logger.info('Serving forever...')
        server.serve_forever()


if __name__ == '__main__':
    os.chdir(BASE_DIR)
    logfile = LOG_DIR+time.strftime("%m-%d-%y %H:%M:%S.log")
    logfmt = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    datefmt = '%H:%M:%S %m/%d/%y'
    formatter = logging.Formatter(fmt=logfmt, 
                                  datefmt=datefmt)
    logging.basicConfig(level=logging.DEBUG, 
                        format=logfmt,
                        datefmt=datefmt)

    logger = logging.getLogger()
    fh = logging.FileHandler(logfile)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    fh = logging.FileHandler(LATEST_LOG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logging.info('Logging to file: %s',logfile)
    while True:
        try:
             Main(IP,PORT)
        except KeyboardInterrupt:
             logging.critical('Terminated By User')
             break
        except BaseException as er:
            logging.critical('Server Daemon crashed:')
            logging.exception(er)
            logging.info('Restarting in 2...')
            time.sleep(2)
            logging.info('Restarting...')



