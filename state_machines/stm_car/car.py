from stmpy import Machine, Driver
import ipywidgets as widgets
from IPython.display import display


class Car:
    # Functions that change the displayed image
    def on_idle(self):
        self.plug.set_trait(name="value", value=self.idle)

    def on_connected(self):
        self.plug.set_trait(name="value", value=self.carConnected)

    def on_charging(self):
        self.plug.set_trait(name="value", value=self.chargeCar)

    # Functions that happens when buttons are pressed
    def on_buttonRegister_press(self, b):
        self.stm.send("register_arrival")  # <---- here we send a signal

    def on_buttonDisconnect_press(self, b):
        self.stm.send("car_disconnected")

    def on_init(self):
        print("Car created \n")
        # load images and store
        self.idle = open("../../Images/idle.jpg", "rb").read()
        self.carConnected = open("../../Images/connected.jpg", "rb").read()
        self.chargeCar = open("../../Images/charging.jpg", "rb").read()

        self.plug = widgets.Image(value=self.idle, format="jpg", width=500, height=500)

        self.title = widgets.Label(value="Car")

        self.buttonRegister = widgets.Button(description="Connect")
        self.buttonRegister.on_click(self.on_buttonRegister_press)

        self.buttonDisconnect = widgets.Button(description="Disconnect")
        self.buttonDisconnect.on_click(self.on_buttonDisconnect_press)

        box = widgets.VBox(
            [self.title, self.plug, self.buttonRegister, self.buttonDisconnect]
        )
        display(box)

    # Functions that send mqtt messages
    def send_mqtt_register(self):
        self.mqtt_client.publish("from_car", "Car is connected to the charger")

    def send_mqtt_disconnected(self):
        self.mqtt_client.publish("from_car", "Car is disconnected from the charger")

    def send_mqtt_carinfo(self):
        self.mqtt_client.publish("from_car", "Carinfo")

    def send_mqtt_batteryinfo(self):
        self.mqtt_client.publish("from_car", "Batteryinfo")


# Triggers
t0_initial = {"source": "initial", "target": "idle", "effect": "on_init"}

t1_car_connected = {
    "trigger": "register_arrival",
    "source": "idle",
    "target": "connected",
    "effect": "send_mqtt_register",
}

t2_car_disconnected = {
    "trigger": "car_disconnected",
    "source": "connected",
    "target": "idle",
    "effect": "send_mqtt_disconnected",
}

t3_provide_carinfo = {
    "trigger": "provide_carinfo",
    "source": "connected",
    "target": "connected",
    "effect": "send_mqtt_carinfo",
}

t4_provide_batteryinfo = {
    "trigger": "provide_batteryinfo",
    "source": "connected",
    "target": "connected",
    "effect": "send_mqtt_batteryinfo",
}

t5_car_charging = {
    "trigger": "start_charging",
    "source": "connected",
    "target": "charging",
}

t6_car_charging = {
    "trigger": "stop_charging",
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


class MQTT_CAR:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    # This function checks the message and sends a signal to the state machine
    def on_message(self, client, userdata, message):
        if message.payload.decode() == "Requesting data":
            self.stm_driver.send("provide_carinfo", "car")
        elif message.payload.decode() == "Please provide battery info":
            self.stm_driver.send("provide_batteryinfo", "car")
        elif message.payload.decode() == "Charging started":
            self.stm_driver.send("start_charging", "car")
        elif message.payload.decode() == "Charging finished":
            self.stm_driver.send("stop_charging", "car")
        elif message.payload.decode() == "Charging is aborted":
            self.stm_driver.send("stop_charging", "car")

    def start(self, broker, port):
        print("Connecting to broker:", broker, "port:", port)
        self.client.connect(broker, port)

        # The car only subscribes to the charger
        self.client.subscribe("from_charger")

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()


car = Car()
machine = Machine(
    name="car",
    transitions=[
        t0_initial,
        t1_car_connected,
        t2_car_disconnected,
        t3_provide_carinfo,
        t4_provide_batteryinfo,
        t5_car_charging,
        t6_car_charging,
    ],
    states=[idle, connected, charging],
    obj=car,
)

car.stm = machine

driver = Driver()
driver.add_machine(machine)

mqtt_car = MQTT_CAR()
car.mqtt_client = mqtt_car.client
mqtt_car.stm_driver = driver

driver.start()
mqtt_car.start(broker, port)
