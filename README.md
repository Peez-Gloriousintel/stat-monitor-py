# Status Monitoring Service
Status Monitoring service is a python web service that allows you to view a status of several processes on multiple servers simultaneously. Initially, you need to install and run this software on all of your target servers. You can freely change its configuration as you want by supplying a name of processes together with a command to check their status, expected result and value. This software will execute those commands and generate results in JSON format according to given conditions you have been configured.

## Applications
Your job is to build a web application or something similar in order to send requests to your servers and display the results returned from the web service. In addition to this, you can also create an application to log a status of processes running on your servers by sending monitoring requests periodically and storing the results for further analysis.

## Dependencies
- python 3
and
- web.py
```
sudo easy_install web.py
```

## Configuration
in monitor.conf
```
[default]
port = <port number>
auth = (yes|no)
username = <username>
password = <password>

[<process name>]
command = <any command-line>
expect = (output|error|status)
value = <expected value for matching>

#for example
[app.js]
command = ps auxww | grep app.js | grep -v grep
expect = status
value = 0

...
```
