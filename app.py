from flask import Flask, render_template, jsonify
from flask import request
from flightController import FlightController

flightCon = FlightController()


app = Flask(__name__)

def getDirectionValue(value):
    if value is None:
        return 1500
    try:
        value = int(value)
        if value > 2000:
            value = 2000
        if value < 1000:
            value = 1100
        return value
    except ValueError:
        return 1500

@app.route('/')
def index():
    pitch = getDirectionValue(request.args.get('pitch'))
    yaw = getDirectionValue(request.args.get('yaw'))
    roll = getDirectionValue(request.args.get('roll'))
    throttle = getDirectionValue(request.args.get('throttle'))

    directions = {'pitch':pitch, 'roll':roll, 'yaw':yaw, 'throttle':throttle}
    flightCon.write_to_arduino(directions)
    maxThrottle = '<h1><a href="?throttle=2000">throttle=2000</a></h1>'
    minThrottle = '<h1><a href="?throttle=1000&yaw=1000">throttle&yaw=1000</a></h1>'
    Throttle1000 = '<h1><a href="?throttle=1000">throttle=1000</a></h1>'
    Throttle1100 = '<h1><a href="?throttle=1100">throttle=1100</a></h1>'
    Throttle1200 = '<h1><a href="?throttle=1200">throttle=1200</a></h1>'
    Throttle1300 = '<h1><a href="?throttle=1300">throttle=1300</a></h1>' 
    Throttle1400 = '<h1><a href="?throttle=1400">throttle=1400</a></h1>'
    Throttle1500 = '<h1><a href="?throttle=1500">throttle=1500</a></h1>'


    htmlPage = maxThrottle + minThrottle + Throttle1000 + Throttle1100 + Throttle1200 + Throttle1300 + Throttle1400 + Throttle1500
    return htmlPage

@app.route('/joy')
def joy():
    return render_template('index.html')        

@app.route('/_get')
def post():
    s_key = request.args.get('streamKey')
    if s_key is not None:
        if s_key == "":
            chhu='stop'
        else:
            return ""
        
    else:
        yaw = getDirectionValue(request.args.get('yaw'))
        throttle = getDirectionValue(request.args.get('throttle'))
        pitch = getDirectionValue(request.args.get('pitch'))
        roll = getDirectionValue(request.args.get('roll'))
        directions = {'pitch':pitch, 'roll':roll, 'yaw':yaw, 'throttle':throttle}
        flightCon.write_to_arduino(directions)
    return str({'yaw':yaw, 'throttle':throttle})

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')
        

