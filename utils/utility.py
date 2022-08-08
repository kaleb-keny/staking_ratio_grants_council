import yaml
from itertools import cycle
import web3 as w3

def parse_config(path):
    with open(path, 'r') as stream:
        return  yaml.load(stream, Loader=yaml.FullLoader)

def get_w3(conf,chain):
    url = conf["rpc"]["http"][chain]+conf["rpc"]["keys"][0]
    return w3.Web3(w3.HTTPProvider(url))

async def run_post_request(session,url,payload):
    async with session.post(url=url,data=payload) as response:
        return await response.json(content_type=None)

async def run_get_request(session,url):
    async with session.get(url) as response:
        return await response.json(content_type=None)
    
def setup_node_cycle(conf):
    nodeDict = dict()
    for chain, url in conf["rpc"]["http"].items():
        nodeList      = list()
        for key in conf["rpc"]["keys"]:
            nodeList.append(url+key)
        nodeDict[chain] = cycle(nodeList)
    return nodeDict            