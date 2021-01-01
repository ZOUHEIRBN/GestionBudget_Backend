from datetime import datetime

from bindings import database

for i in range(21, 28):
    database['funds'].update_many({'date': f'{i}/12/2020'},
                              {'$set': {'date': datetime.strptime(f"{i}/12/2020", "%d/%m/%Y")}})