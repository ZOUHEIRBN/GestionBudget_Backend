import subprocess
import time
from pymongo import MongoClient

subprocess.Popen("mongod")
local_data = MongoClient(port=27017)["GestionBudget"]

database_address = "mongodb+srv://bdg_admin:OMXklA8zUKGvDoEX@gestionbudgetcluster.irghg.mongodb.net/GestionBudget?retryWrites=true&w=majority"
remote_data = MongoClient(database_address)["GestionBudget"]

collections = local_data.list_collection_names()

time.sleep(10)
for collection in collections[1:]:
    l = list(local_data[collection].find({}))
    print(f"Migrating collection: \"{collection.upper()}\"...", end='')
    remote_data[collection].insert_many(l)
    time.sleep(2)
    print("Done")
