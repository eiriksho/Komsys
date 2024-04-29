from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display


class Charger:
    # Functions that change the displayed image
    def on_idle(self):
        self.plug.set_trait(name="value", value=self.idle)

    def on_connected(self):
        self.plug.set_trait(name="value", value=self.carConnected)

    def on_charging(self):
        self.plug.set_trait(name="value", value=self.chargeCar)

    # Buttons that happens when the buttons are pressed
    def on_buttonChargingAborted_press(self, b):
        self.stm.send("charging_aborted")

    def on_init(self):
        # load images and store them
        self.idle = open("../../Images/idle.jpg", "rb").read()
        self.carConnected = open("../../Images/connected.jpg", "rb").read()
        self.chargeCar = open("../../Images/charging.jpg", "rb").read()

        self.plug = widgets.Image(value=self.idle, format="jpg", width=500, height=500)

        self.title = widgets.Label(value="Charging station")

        self.buttonChargingAborted = widgets.Button(description="Abort charging")
        self.buttonChargingAborted.on_click(self.on_buttonChargingAborted_press)

        display(self.title, self.plug, self.buttonChargingAborted)

    # Functions that send mqtt messages
    def send_mqtt_connected(self):
        self.mqtt_client.publish("from_charger", "Car is connected to the charger")

    def send_mqtt_disconnected(self):
        self.mqtt_client.publish("from_charger", "Car is disconnected from the charger")

    def send_mqtt_aborted(self):
        self.mqtt_client.publish("from_charger", "Charging is aborted")

    def request_carinfo(self):
        self.mqtt_client.publish("from_charger", "Please provide car info")

    def send_carinfo(self):
        self.mqtt_client.publish("from_charger", "Car info")

    def send_mqtt_charging(self):
        self.mqtt_client.publish("from_charger", "Charging started")

    def send_mqtt_finished(self):
        self.mqtt_client.publish("from_charger", "Charging finished")


# Triggers
t0_initial = {"source": "initial", "target": "idle", "effect": "on_init"}

t1_car_connected = {
    "trigger": "car_connected",
    "source": "idle",
    "target": "connected",
    "effect": "send_mqtt_connected",
}

t2_request_charging = {
    "trigger": "request_charging",
    "source": "connected",
    "target": "charging",
    "effect": "send_mqtt_charging",
}
t3_car_disconnected = {
    "trigger": "car_disconnected",
    "source": "connected",
    "target": "idle",
    "effect": "send_mqtt_disconnected",
}
t4_charging_finished = {
    "trigger": "charging_finished",
    "source": "charging",
    "target": "connected",
    "effect": "send_mqtt_finished",
}
t5_charging_aborted = {
    "trigger": "charging_aborted",
    "source": "charging",
    "target": "connected",
    "effect": "send_mqtt_aborted",
}

t6_request_data = {
    "trigger": "request_data",
    "source": "connected",
    "target": "connected",
    "effect": "request_carinfo",
}

t7_send_carinfo = {
    "trigger": "carinfo_received",
    "source": "connected",
    "target": "connected",
    "effect": "send_carinfo",
}

# States
idle = {"name": "idle", "entry": "on_idle"}

connected = {"name": "connected", "entry": "on_connected"}

charging = {"name": "charging", "entry": "on_charging"}

from threading import Thread

import paho.mqtt.client as mqtt

broker, port = "test.mosquitto.org", 1883


class MQTT_CHARGER:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    # This function checks the message and sends a signal to the state machine
    def on_message(self, client, userdata, message):
        if message.payload.decode() == "Please start charging":
            self.stm_driver.send("request_charging", "charger")
        elif message.payload.decode() == "Please finish charging":
            self.stm_driver.send("charging_finished", "charger")
        elif message.payload.decode() == "Car is connected to the charger":
            self.stm_driver.send("car_connected", "charger")
        elif message.payload.decode() == "Car is disconnected from the charger":
            self.stm_driver.send("car_disconnected", "charger")
        elif message.payload.decode() == "Requesting data":
            self.stm_driver.send("request_data", "charger")
        elif message.payload.decode() == "Carinfo":
            self.stm_driver.send("carinfo_received", "charger")

    def start(self, broker, port):
        print("Connecting to broker:", broker, "port:", port)
        self.client.connect(broker, port)

        # The charger is connected to the car and SCU
        self.client.subscribe("from_car")
        self.client.subscribe("from_scu")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()


charger = Charger()
machine = Machine(
    name="charger",
    transitions=[
        t0_initial,
        t1_car_connected,
        t2_request_charging,
        t3_car_disconnected,
        t4_charging_finished,
        t5_charging_aborted,
        t6_request_data,
        t7_send_carinfo,
    ],
    states=[idle, connected, charging],
    obj=charger,
)

charger.stm = machine

driver = Driver()
driver.add_machine(machine)

mqtt_charger = MQTT_CHARGER()
charger.mqtt_client = mqtt_charger.client
mqtt_charger.stm_driver = driver

driver.start()
mqtt_charger.start(broker, port)
