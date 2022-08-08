#!/usr/bin/env python3
from utils.utility import parse_config
import argparse
import os
from utils.database import Database
from utils.update_data import UpdateData
conf       = parse_config(r"config/conf.yaml")
topics     = parse_config(r"config/topics.yaml")

if not 'mysql' in conf.keys():
    conf["mysql"] = dict()

conf["mysql"]["user"]     = os.environ.get("DB_USER",conf["mysql"]["user"])
conf["mysql"]["password"] = os.environ.get("DB_PASSWORD",conf["mysql"]["password"])
conf["mysql"]["host"]     = os.environ.get("DB_HOST",conf["mysql"]["host"])
conf["mysql"]["port"]     = os.environ.get("DB_PORT",conf["mysql"]["port"])
conf["mysql"]["database"] = os.environ.get("DB_NAME",conf["mysql"]["database"])

#%%Arg Parse
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='launches the process to gather minters data')
    parser.add_argument("-t",
                        type=str,
                        required=True,
                        choices=["init","docker_run","run"],
                        help="Please choose between init, run and docker_run")
    args = parser.parse_args()
    if args.t == 'init':
        db = Database(conf)
        db.initialize_db(topics)
        print("db initialized")
    elif args.t == 'run':
        data = UpdateData(conf,topics)
        data.run_update_data()
    elif args.t == 'docker_run':
        db = Database(conf)
        db.init_if_new(topics)
        data = UpdateData(conf,topics)
        data.run_update_data_docker()
    else:
        print("doing nothing")