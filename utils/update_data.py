from utils.gather_state import GatherState
from utils.snx_contracts import SnxContracts
from utils.gather_logs import GatherLogs
import logging, watchtower
import json
from logging.handlers import TimedRotatingFileHandler
import sys
import boto3
import time 

class UpdateData(GatherState,GatherLogs,SnxContracts):
    
    def __init__(self,conf,topics):
        GatherState.__init__(self,conf)
        GatherLogs.__init__(self,conf, topics)
        SnxContracts.__init__(self,conf)
        self.totalSnxSupply = dict()
    
    def run_update_data(self):        
        self.run_gather_logs()
        self.run_gather_state()                
        sql = 'delete from snx_holder where collateral < 1e18;'
        self.push_sql_to_server(sql)
        self.prepare_output()
        
    def run_update_data_docker(self):
        self.log_init(self.conf)
        while True:
            try:
                self.log("preparing cratio",False)
                self.run_update_data()
                self.log("cratio computed successfully",False)
                time.sleep(60*60*6)
            except:
                time.sleep(60*60)
                self.logger.exception('issue seen with staking ratio, trying again')
                sys.exit(1)
            
    def prepare_output(self):
        sql = 'select * from snx_holder'
        df = self.get_df_from_server(sql)    
        #remove unstaked (less than 1$ of debt)
        df = df[df["debt"]>1e18].copy()
        #save collateralization ratio
        contract    = self.get_snx_contract(contractName='Synthetix', chain='ethereum')
        totalSupply = contract.functions.totalSupply().call()
        systemStakingPercent = df["collateral"].sum() / totalSupply
        stakedSnx = df.groupby(by='network')["collateral"].sum()/1e18
        output = {"systemStakingPercent":systemStakingPercent,
                  "timestamp":int(time.time()),
                  "stakedSnx":{"ethereum":stakedSnx["ethereum"],
                               "optimism":stakedSnx["optimism"]}}
        with open("output/output.json","w") as f:
            json.dump(output,f,indent=6)
                
    def get_staking_ratio(self,df,chain):
        dfStaked  = df[df["debt"] > 1].copy()        
        if chain in ['ethereum','optimism']:
            contract                   = self.get_snx_contract(contractName='Synthetix', chain=chain)
            self.totalSnxSupply[chain] = contract.functions.totalSupply().call()
            dfStaked  = dfStaked [dfStaked["network"]==chain].copy() 
            return dfStaked["collateral"].sum() / self.totalSnxSupply[chain]
        return dfStaked["collateral"].sum()/sum(self.totalSnxSupply.values())

    def log_init(self,conf):
        logging.basicConfig(handlers=[logging.FileHandler(filename="log.log", 
                                                         encoding='utf-8', mode='a+')],
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
                            datefmt="%F %A %T", 
                            level=logging.INFO)                                
        self.logger = logging.getLogger(__name__)
        handler = TimedRotatingFileHandler(filename='log.log', when='D', interval=1, backupCount=5, encoding='utf-8', delay=True)
        self.logger.addHandler(handler)
        try:            
            boto3Client = boto3.client("logs",
                                       aws_access_key_id=conf["aws"]["keyId"],
                                       aws_secret_access_key=conf["aws"]["secretKey"],
                                       region_name=conf["aws"]['region'])
            self.logger.addHandler(watchtower.CloudWatchLogHandler(boto3_client=boto3Client, 
                                                                   log_group=conf["aws"]['logGroup'],
                                                                   log_stream_name=conf["aws"]['stream'],
                                                                   create_log_stream=True))
            self.logger.debug(msg='this error was seen')
        except:
            self.logger.exception('issue streaming logs')
            
    def log(self,message,isWarning):
        if isWarning:
            self.logger.warning(message) 
        else:
            self.logger.info(message)                                        
    
