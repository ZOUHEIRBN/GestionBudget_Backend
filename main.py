from bindings import app, socket_io

#./env/scripts/python.exe main.py
#!mongod
#!redis-servrer
#!rq worker

if __name__ == '__main__':
    socket_io.run(app, port=3000, host='0.0.0.0')
