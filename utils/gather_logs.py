import pandas as pd
import itertools
from utils.logs import Logs
from utils.utility import get_w3
from collections import namedtuple

class GatherLogs(Logs):
    
    def __init__(self,conf,topics):
        self.topics     = topics
        self.tupple = namedtuple('topic', ['topic',
                                           'address',
                                           'initialBlock',
                                           'endingBlock'])
        
        Logs.__init__(self,conf)

    def run_gather_logs(self):
        
        for chain in self.nodeDict.keys():
            w3 = get_w3(self.conf,chain)
            latestBlock = w3.eth.blockNumber

            for topicName, topicDict in self.topics.items():
                
                sql = \
                f'''
                SELECT
                    blockNumber
                FROM
                    logs
                WHERE
                    network = '{chain}'
                AND
                    log = '{topicName}'
                ;
                '''
                initialBlock      = self.get_df_from_server(sql).iloc[0,0]    
                contractAddress   = self.get_address(topicDict["contract"],chain=chain)                                
                input = self.tupple(topic=w3.keccak(text=self.topics[topicName]["topic"]).hex(),
                                    address=contractAddress ,
                                    initialBlock=initialBlock,
                                    endingBlock=latestBlock)
                inputList, outputList = self.gather_logs(chain=chain,
                                                         inputList=[input],
                                                         runCounter=1)
                df = pd.DataFrame(list(itertools.chain(*outputList)))                    
                exec(f'self.{topicName}_dump_to_server(df,chain)')

                self.update_logs_max_block(topicName,chain,latestBlock)     
                    
    def mint_dump_to_server(self,data,chain):
                
        if len(data)>0:
            userSet     = set()
            userList    = '0x'+ data["topics"].str[1].str[-40:]
            userSet.update(userList.to_list())                        
            self.update_snx_addresses_to_server(userSet,chain)

    def update_logs_max_block(self,topicName,chain,blockNumber):

        sql=\
        f'''
        UPDATE
            logs
        SET
            blockNumber = {blockNumber}
        WHERE
            network = '{chain}'
        AND
            log = '{topicName}'
        ;
        '''
        self.push_sql_to_server(sql)
        
    def update_snx_addresses_to_server(self,userSet,chain):
        df = self.get_df_from_server('select * from snx_holder limit 0')
        w3 = get_w3(self.conf,'ethereum')
        df["address"]  = pd.DataFrame(userSet)
        df["address"]  = df["address"].apply(w3.toChecksumAddress)
        df["network"]  = chain
        df.fillna(0,inplace=True)
        self.push_df_to_server(df,'snx_holder')