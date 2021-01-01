from bindings import app, socket

#./env/scripts/python.exe main.py
#!mongod
#!redis-servrer
#!rq worker

if __name__ == '__main__':
    socket.run(app, port=3000)
