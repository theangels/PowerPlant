
import digital_machine
import digital_machine.templates as tmpl

from .BoilerWorkshop import BoilerWorkshop
from .Boiler import Boiler
from .PowerPlant import PowerPlant


try:
    from ._legacy import models as legacy_models
except ModuleNotFoundError:
    legacy_models = {}

py_model_collection = tmpl.PyModelCollection()

BoilerWorkshop().generate_model(digital_machine.digital_twin_model("power", "BoilerWorkshop"), py_model_collection)
Boiler().generate_model(digital_machine.digital_twin_model("power", "Boiler"), py_model_collection)
PowerPlant().generate_model(digital_machine.digital_twin_model("power", "PowerPlant"), py_model_collection)


models = py_model_collection.models
models.update(legacy_models)
