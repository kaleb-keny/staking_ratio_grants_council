import asyncio
import pandas as pd
from utils.multicall import Multicall
from utils.database import Database

class GatherState(Multicall,Database):

    def __init__(self,conf):

        Database.__init__(self,conf)
        Multicall.__init__(self,conf=conf)
                        
    def run_gather_state(self):
        
        for chain in self.conf["rpc"]["http"].keys():

            sql = f"SELECT address FROM snx_holder where network = '{chain}';"
            addressList = self.get_df_from_server(sql)["address"].to_list()
    
            #get debt / collateral of all addys
            self.update_collateral(addressList,chain)
            self.update_debt(addressList,chain)
        
    def update_collateral(self,addressList,chain):
        task   = self.run_multicall(addressList, 
                                    chain, 
                                    functionName='collateral', 
                                    contractName='Synthetix')
        output        = self.run_async_task([task])
        df            = pd.DataFrame(output).T
        df["address"] = df.index
        df.columns    = ['collateral','address']
        df["collateral"] = df["collateral"].astype(str)        
        self.push_state_to_server(df,'collateral',chain)

    def update_debt(self,addressList,chain):
        task= self.run_multicall(addressList, 
                                 chain, 
                                 functionName='debtBalanceOf', 
                                 contractName='Synthetix',
                                 arg='0x73555344')
        output        = self.run_async_task([task])
        df            = pd.DataFrame(output).T
        df["address"] = df.index
        df.columns    = ['debt','address']
        df["debt"] = df["debt"].astype(str)        
        self.push_state_to_server(df,'debt',chain)
        
    def run_async_task(self,task):
        loop  = asyncio.get_event_loop()        
        task  = asyncio.gather(*task,return_exceptions=True)
        try:
            return loop.run_until_complete(task)
        except:
            tasks = asyncio.all_tasks(loop=loop)
            for t in tasks:
                t.cancel()
            group = asyncio.gather(*tasks,return_exceptions=True)
            loop.run_until_complete(group)
                
    def push_state_to_server(self,df,field,chain):                

        with self.get_mysql_connection() as con:
            df.to_sql("temp",con,index=False,if_exists='replace')

        sql = \
            f'''
            UPDATE
                snx_holder s
            INNER JOIN
                temp t ON
            s.address = t.address
            SET
                s.{field} = IFNULL(t.{field},0)
            WHERE
                network = '{chain}';
            '''
        self.push_sql_to_server(sql)
        
#%%
if __name__ == '__main__':
    self=gather_state(conf)
    # self.run_gather_state()
