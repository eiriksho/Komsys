from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display


class SCU:
    # Functions that change the displayed image
    def on_idle(self):
        self.plug.set_trait(name="value", value=self.idle)
        self.label.set_trait(name="value", value="No car connected")

    def on_connected(self):
        self.plug.set_trait(name="value", value=self.carConnected)

    def on_charging(self):
        self.plug.set_trait(name="value", value=self.chargeCar)

    # Functions that send signal to the state machine when the buttons are pressed
    def on_buttonCharge_press(self, b):
        self.stm.send("request_charging")

    def on_buttonChargingFinished_press(self, b):
        self.stm.send("charging_finished")

    def on_init(self):
        self.idle = open("../../Images/idle.jpg", "rb").read()
        self.carConnected = open("../../Images/connected.jpg", "rb").read()
        self.chargeCar = open("../../Images/charging.jpg", "rb").read()

        self.plug = widgets.Image(value=self.idle, format="jpg", width=500, height=500)

        self.title = widgets.Label(value="Smart Charging Unit")

        self.label = widgets.Label(value="No car connected")

        self.buttonCharge = widgets.Button(description="Charge")
        self.buttonCharge.on_click(self.on_buttonCharge_press)

        self.buttonChargingFinished = widgets.Button(description="Finish charging")
        self.buttonChargingFinished.on_click(self.on_buttonChargingFinished_press)

        box = widgets.VBox(
            [
                self.title,
                self.plug,
                self.buttonCharge,
                self.buttonChargingFinished,
                self.label,
            ]
        )
        display(box)

    # Functions that send mqtt messages
    def send_mqtt_charging(self):
        self.mqtt_client.publish("from_scu", "Please start charging")

    def send_mqtt_finished(self):
        self.mqtt_client.publish("from_scu", "Please finish charging")

    def request_data(self):
        self.mqtt_client.publish("from_scu", "Requesting data")


# Triggers
t0_initial = {"source": "initial", "target": "idle", "effect": "on_init"}

t1_car_connected = {
    "trigger": "car_connected",
    "source": "idle",
    "target": "connected",
    "effect": "request_data",
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
}

# States
idle = {"name": "idle", "entry": "on_idle"}

connected = {"name": "connected", "entry": "on_connected"}

charging = {"name": "charging", "entry": "on_charging"}

from threading import Thread

import paho.mqtt.client as mqtt

broker, port = "test.mosquitto.org", 1883


class MQTT_SCU:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    # This function checks incoming messages and sends asignal to the state machine
    def on_message(self, client, userdata, message):
        if message.payload.decode() == "Car is connected to the charger":
            self.stm_driver.send("car_connected", "scu")
        elif message.payload.decode() == "Car is disconnected from the charger":
            self.stm_driver.send("car_disconnected", "scu")
        elif message.payload.decode() == "Charging is aborted":
            self.stm_driver.send("charging_aborted", "scu")
        elif message.payload.decode() == "Car info":
            self.scu.label.value = "Tesla Model S\nBattery: 50%\nRange: 200km\n"
        # elif more stuff

    def start(self, broker, port):
        self.client.connect(broker, port)

        # The SCU subscribes to the messages from the charger
        self.client.subscribe("from_charger")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()


scu = SCU()
machine = Machine(
    name="scu",
    transitions=[
        t0_initial,
        t1_car_connected,
        t2_request_charging,
        t3_car_disconnected,
        t4_charging_finished,
        t5_charging_aborted,
    ],
    states=[idle, connected, charging],
    obj=scu,
)

scu.stm = machine

driver = Driver()
driver.add_machine(machine)

mqtt_scu = MQTT_SCU()
scu.mqtt_client = mqtt_scu.client
mqtt_scu.stm_driver = driver
mqtt_scu.scu = scu

driver.start()
mqtt_scu.start(broker, port)
