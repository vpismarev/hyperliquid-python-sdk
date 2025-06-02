import requests


header = {'accept': 'application/json'}
data = requests.get('https://dlmm-api.meteora.ag/info/protocol_metrics', headers=header)


print(data.content.decode())
