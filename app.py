import urllib2
import sys
import json
from flask import Flask
from flask import Response

app = Flask(__name__)

try:
    repository = sys.argv[1].split("/", 3)[3]
except IndexError:
    print "Invalid or No config repository URL provided!"
    sys.exit()

@app.route("/")
def hello():
    return "Hello from Dockerized Flask App!!"

@app.route("/v1/<environment>-config.yml")
def configYml(environment):
    return getEnvContent(environment)

@app.route("/v1/<environment>-config.json")
def configJson(environment):
    try:
        response = getEnvContent(environment)
        return generateJSON(response.split(":")[0], response.split(":")[1])
    except IndexError:
        return "Config Repository or File not found!"

def getEnvContent(environment):
    try:
        request = urllib2.Request("https://api.github.com/repos/" + repository + "/contents/" + environment + "-config.yml")
        request.add_header('Accept' , 'application/vnd.github.VERSION.raw')
        return urllib2.urlopen(request).read().strip()
    except:
        return "Config Repository or File not found!"

def generateJSON(key, value):
    return Response(json.loads(json.dumps('{"' + key + '":' + value + '}')), mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')