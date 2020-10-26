from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'hello world ! '

@app.route('/b')
def cc():
    return 'b'
    
if __name__ == '__main__':
	app.run()