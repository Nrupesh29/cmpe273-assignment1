import sys
import json
import yaml
import collections
from github import Github
from flask import Flask
from flask import Response
from github import UnknownObjectException
from github import RateLimitExceededException

app = Flask(__name__)

try:
    url = sys.argv[1].split("/", 4)
    username = url[3]
    repository = url[4]
    git = Github().get_user(username).get_repo(repository)
except (UnknownObjectException, IndexError):
    print "Provide a valid Github repository URL!"
    sys.exit()
except RateLimitExceededException:
    print "Sorry! Only 60 requests per hour."
    sys.exit()
except Exception as e:
    print "Oops! " + str(e)
    sys.exit()


'''
Function to preserve the order of YML content
'''
def preserveYamlOrder():

    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_mapping(_mapping_tag, data.iteritems())

    def dict_constructor(loader, node):
        return collections.OrderedDict(loader.construct_pairs(node))

    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)


'''
Function to execute on an API request with url <base_address>/v1/<file_name>
'''
@app.route("/v1/<environment>")
def config(environment):

    preserveYamlOrder()
    filename = environment.rsplit(".")[0]
    extention = environment.rsplit(".")[1]

    try:
        content = git.get_file_contents(filename+".yml").content.decode(git.get_contents(filename+".yml").encoding)
    except UnknownObjectException:
        return "File not found in the repository!"
    except RateLimitExceededException:
        return "Sorry! Only 60 requests per hour."
    except Exception as e:
        return "Oops! " + str(e)

    if (extention == 'yml'):
        return Response(yaml.safe_load(yaml.dump(content)))
    elif (extention == 'json'):
        return Response(json.dumps(yaml.load(content), indent=2), mimetype='application/json')
    else:
        return "Not a valid file extention!"



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')