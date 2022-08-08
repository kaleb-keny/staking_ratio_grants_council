from utils.gather_state import GatherState
from utils.snx_contracts import SnxContracts
from utils.gather_logs import GatherLogs
import sys
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
        while True:
            try:
                self.run_update_data()
                time.sleep(60*60*6)
            except:
                sys.exit(1)
            
    def prepare_output(self):
        sql = 'select * from snx_holder'
        df = self.get_df_from_server(sql)    
        #remove unstaked (less than 1$ of debt)
        df = df[df["debt"]>1e18].copy()
        #save collateralization ratio
        contract    = self.get_snx_contract(contractName='Synthetix', chain='ethereum')
        totalSupply = contract.functions.totalSupply().call()
        cratio = df["collateral"].sum() / totalSupply
        with open("output/cratio.txt","w") as f:
            f.write(f'''{int(time.time())}/{cratio}''')
        
    def get_staking_ratio(self,df,chain):
        dfStaked  = df[df["debt"] > 1].copy()        
        if chain in ['ethereum','optimism']:
            contract                   = self.get_snx_contract(contractName='Synthetix', chain=chain)
            self.totalSnxSupply[chain] = contract.functions.totalSupply().call()
            dfStaked  = dfStaked [dfStaked["network"]==chain].copy() 
            return dfStaked["collateral"].sum() / self.totalSnxSupply[chain]
        return dfStaked["collateral"].sum()/sum(self.totalSnxSupply.values())