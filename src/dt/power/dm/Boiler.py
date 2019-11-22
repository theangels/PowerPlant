from digital_machine import *
from digital_machine.templates import templates, simple

import pandas as pd
import pickle

# Load the pickled Linear Regression model (see in FILES)
try:
    with open(os.path.join(os.path.dirname(__file__), "lr.model"), "rb") as f:
        lr = pickle.load(f)
except:
    logging.error("Cannot load pickled model", exc_info=True)

# Customize the generic model template
class Boiler(simple.SimpleClassTemplate):

    @templates.model()
    @templates.input(features={
        "outside_temperature": {
            "metric": "Monitoring.outside_temperature",
            "aggregation": "1min",
            "aggregation-function": "avg"
        },
        "load": {
            "metric": "Monitoring.load",
            "aggregation": "1min",
            "aggregation-function": "avg",
        }
    })
    @templates.output(features={
        "load_prediction": {
            "metric": "Monitoring.load_prediction",
            "series-length": 10,
            "resolution": "1min"
        }
    })
    def load_prediction(self, input, output):
        logging.error("Applying model: %s", input.data)
        ts = input.timestamp - input.timestamp % 60
        index = input.data["index"]
        d0 = index % 24
        d1 = (index // 24) % 7
        # Invoke prediction
        result = lr.predict(
            [[
                input.data["outside_temperature"], 
                d1, 
                d0, 
                input.data["load"]
            ]])
        output.data["load_prediction"] = pd.DataFrame(data={
            "load_prediction": result[0]
        }, index = [ts + (i+1)*60. for i in range(10)])
        logging.error("Load Prediction:\n %s", output.data["load_prediction"])
        output.timestamp = ts
        
    C_CONTENT = 0.75
    
    @templates.model()
    @templates.input(features={
        "coal": {
            "metric": "Consumption.coal",
            "aggregation": "1min",
            "aggregation-function": "sum"
        }
    })
    @templates.output(features={
        "co2": {
            "metric": "Generation.co2",
            "aggregation": "1min",
            "aggregation-function": "sum"
        }
    })
    def co2_model(self, input, output):
        c = input.data["coal"] * self.C_CONTENT
        output.data["co2"] = 44./12. * c