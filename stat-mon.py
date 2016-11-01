''' 
@author: pj4dev.mit@gmail.com
@url: https://github.com/pj4dev/stat-monitor-py
'''
import web
import json
import configparser as cparser
import subprocess
import re
import base64
from functools import wraps
import glob

port = 8000
urls = (
	'/ping', 'ping',
	'/echo/(.*)', 'echo',
	'/status/(.*)', 'status'
)

def printUrls(urls):
	print('Available URls:')
	for i in range(0, len(urls)):
		if i % 2 == 0:
			print(urls[i])

def Initialize():
	global port
	config = cparser.ConfigParser()
	config.read('monitor.conf')

	port = int(config['default']['port'])

	glob.credential = {
		'username': config['default']['username'],
		'password': config['default']['password']
	}

	if config['default']['auth'] == 'yes': glob.noauth = False
	else: glob.noauth = True

	process = config.sections()
	process.remove('default')
	for p in process:
		glob.processCmd[p] = {
			'command': config[p]['command'],
			'expect': config[p]['expect'],
			'value': config[p]['value']
		}

	printUrls(urls)
	print('Monitoring: ' + ', '.join(process))


def resConstructor(success, message, **args):
	res = {
		'success': success,
		'message': message
	}
	for arg in args:
		res[arg] = args[arg]
	return res

def executeCmd(cmd):
	cmd = cmd.split('|')
	for i in range(0, len(cmd)):
		cmd[i] = cmd[i].strip().split(' ')
		cmd[i] = list(filter(None, cmd[i]))
		if i == 0:
			p = subprocess.Popen(cmd[i], stdout=subprocess.PIPE)
		else:
			p = subprocess.Popen(cmd[i], stdin=p.stdout, stdout=subprocess.PIPE)
	out, err = p.communicate()
	status = p.wait()
	return [out, err, status]

def checkAuth(username, password):
    return glob.credential['username'] == username and glob.credential['password'] == password


def requiresAuth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = web.ctx.env['HTTP_AUTHORIZATION'] if 'HTTP_AUTHORIZATION' in  web.ctx.env else None
		if glob.noauth: return f(*args, **kwargs)
		if auth:
			auth = re.sub('^Basic ', '', auth)
			username, password = base64.b64decode(auth).decode('utf-8').split(':')
		if not auth or not checkAuth(username, password):
			web.header('WWW-Authenticate', 'Basic realm="admin"')
			web.ctx.status = '401 Unauthorized'
			return Unauthorized()
		return f(*args, **kwargs)
	return decorated

class Unauthorized():
    def GET(self,arg):
        return "401 Unauthorized"

    def POST(self,arg):
        return "401 Unauthorized"

class ping:
	def GET(self):
		return json.dumps(resConstructor(True, 'PONG'))
class echo:
	def GET(self, word):
		return json.dumps(resConstructor(True, word))

@requiresAuth
class status:
	def GET(self, proc):
		if not proc in glob.processCmd.keys():
			return json.dumps(resConstructor(False, "process not found"))
		ret = executeCmd(glob.processCmd[proc]['command'])
		is_running = False
		if glob.processCmd[proc]['expect'] == 'output':
			if str(ret[0]) == glob.processCmd[proc]['value']: is_running = True
			else: is_running = False
		elif glob.processCmd[proc]['expect'] == 'error':
			if str(ret[1]) == glob.processCmd[proc]['value']: is_running = True
			else: is_running = False
		elif glob.processCmd[proc]['expect'] == 'status':
			if str(ret[2]) == glob.processCmd[proc]['value']: is_running = True
			else: is_running = False
		else:
			return json.dumps(resConstructor(False, "invalid configuration"))
		return json.dumps(resConstructor(True, "OK", is_running=is_running))

class myRestServer(web.application):
	def run(self, port=8080, *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, ('0.0.0.0', port))

if __name__ == "__main__":

	print('Status Monitoring Server v1.0.0')
	print('by Peez Gloriousintel')
	print('see more at https://github.com/pj4dev/stat-monitor-py')
	print('===========================================')

	Initialize()

	print('Running on ', end="")
	app = myRestServer(urls, globals())
	app.run(port)
