import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import nextbus


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def launch():
    return statement('Welcome to next bus! How can I help?')


@ask.intent("GetPrediction", convert={'station':str})
def next_bus(station):
    predictions = nextbus.get_all_predictions(station)
    speech = "I've found the following trains for {} station: ".format(station)
    for routeID, preds in predictions.items():
        if len(preds) == 0: continue
        speech += "There is a {} train ".format(routeID)
        counter = 0
        for p in preds:
            speech += " in {} minutes ".format(p['time'])
            counter += 1
            if counter != len(preds): speech += "and"
            else: speech += ". "
    return statement(speech)

if __name__ == '__main__':
    app.run(debug=True)
