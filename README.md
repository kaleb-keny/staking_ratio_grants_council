# staking_ratio_grants_council

`conf.yaml` file should be incorporated into config folder with the following:

```
---
rpc:
    http:
        ethereum: "https://mainnet.infura.io/v3/"
        optimism: "https://optimism-mainnet.infura.io/v3/"
                
    keys:
        - "XXXXXXXXXXXXX"
        
etherscan:  
    ethereum: 'https://api.etherscan.io/api?module=contract&action=getabi&address={}&apikey=XXXXXXXXXXXXXXXXX'
    optimism: 'https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address={}&apikey=XXXXXXXXXXXXXXXXX'

multicaller:
    ethereum: '0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441'
    optimism: '0x2DC0E2aa608532Da689e89e237dF582B783E552C'

mysql:
    user:  "root"
    password:  "abc123"
    host:  "localhost"
    database:  "staking_ratio_gc"
    raise_on_warnings:  True
    port: 3315

aws:
    keyId: 'XXXXXXXXXXXXX'
    secretKey: 'XXXXXXXXXXXXX'
    region: 'us-east-2'
    logGroup: 'staking_ratio'
    stream: 'status'

proxyAddressResolver:
    ethereum: '0x4E3b31eB0E5CB73641EE1E65E7dCEFe520bA3ef2'
    optimism: '0x1Cb059b7e74fD21665968C908806143E744D5F30'
```
 
