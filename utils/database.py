from sqlalchemy import create_engine
import pandas as pd

class Database():

    def __init__(self, conf):
        
        self.conf           = conf
        
    def initialize_db(self,topics):
                        
        self.create_db()
        self.generate_missing_tables(topics)

    def init_if_new(self,topics):        
        
        if not self.check_if_db_exists():
            self.initialize_db(topics)
        self.generate_missing_tables(topics)

    def check_if_db_exists(self):
        sqlConf = self.conf.get('mysql')        
        try:
            df = self.get_df_from_server(f'''show databases like '{sqlConf["database"]}' ''')
            if len(df)>0:
                return True
            return False
        except:
            return False
                                  
    def create_db(self):
        sql_conf = self.conf.get('mysql')

        user     = sql_conf["user"]
        password = sql_conf["password"]
        host     = sql_conf["host"]
        db       = sql_conf["database"]

        #Check if Database is there, deletes it
        try:
            engine_string = f'mysql+pymysql://{user}:{password}@{host}'
            engine = create_engine(engine_string)
            drop_db_sql = f'DROP DATABASE IF EXISTS {db};'
        except Exception as e:
            print(e)
            engine_string = f"mysql+pymysql://{user}:{password}@{host}/{db}"
            engine = create_engine(engine_string)

        with engine.connect() as con:
            con.execute(drop_db_sql)
            con.execute(f"CREATE DATABASE {db};")
            con.execute(f"USE {db};")


    def generate_missing_tables(self,topics):

        with self.get_mysql_connection() as con:

            availableTablesList = pd.read_sql("show tables;",con).iloc[:,0].to_list()
                
            if not "snx_holder" in availableTablesList:
                sql=\
                '''
                CREATE TABLE snx_holder
                (
                address CHAR(42),
                collateral DECIMAL (65,0),
                debt DECIMAL (65,0),
                network VARCHAR (12),
                CONSTRAINT pk_address PRIMARY KEY (address,network),
                INDEX (address,network)
                );
                '''
                con.execute(sql)
                
            if not "logs" in availableTablesList:
                sql=\
                '''
                CREATE TABLE logs
                (
                blockNumber INT(11),
                log VARCHAR(12),
                network VARCHAR(12),
                CONSTRAINT pk_time PRIMARY KEY (log,network)
                );
                '''
                con.execute(sql)
                for topic in topics:
                    for chain in self.conf["rpc"]["http"].keys():
                        sql = \
                            f'''INSERT INTO 
                                    logs 
                                VALUE 
                                    (1,"{topic}","{chain}");
                            '''
                        self.push_sql_to_server(sql)
                
    def get_df_from_server(self,sql):
        with self.get_mysql_connection() as con:
            return pd.read_sql(sql,con)
    
    def push_sql_to_server(self,sql):
        with self.get_mysql_connection() as con:
            con.execute(sql)
        
    def push_df_to_server(self,df,tbName):
        sql = f'DROP TABLE IF EXISTS temp_{tbName}'
        self.push_sql_to_server(sql)
        #Save the SQL
        with self.get_mysql_connection() as con:            
            df.to_sql(f'temp_{tbName}',con,if_exists='replace',index=False)
            con.execute(f"insert ignore into {tbName} (select * from temp_{tbName});")
            con.execute(f"DROP TABLE temp_{tbName};")

    def get_mysql_connection(self):
        sqlConf = self.conf.get('mysql')
        engine_string = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(sqlConf["user"],sqlConf["password"],sqlConf["host"],sqlConf["database"])
        engine = create_engine(engine_string)
        con = engine.connect()
        return con