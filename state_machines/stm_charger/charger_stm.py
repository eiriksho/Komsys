from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display

class Charger:
    
    def on_buttonConnect_press(self, b):
        self.stm.send('car_connected') # <---- here we send a signal
    
    def on_buttonCharge_press(self, b):
        self.stm.send('request_charging') # <---- here we send a signal
    
    def on_buttonDisconnect_press(self, b):
        self.stm.send('car_disconnected') # <---- here we send a signal

    def on_buttonChargingFinished_press(self, b):
        self.stm.send('charging_finished') # <---- here we send a signal
    
    def on_buttonChargingAborted_press(self, b):
        self.stm.send('charging_aborted') # <---- here we send a signal
            
    def __init__(self):
        # load images and store them
        self.buttonConnect = widgets.Button(description="Connect car")
        self.buttonConnect.on_click(self.on_buttonConnect_press)
        
        self.buttonCharge = widgets.Button(description="Charge")
        self.buttonCharge.on_click(self.on_buttonCharge_press)

        self.buttonDisconnect = widgets.Button(description="Disconnect car")
        self.buttonDisconnect.on_click(self.on_buttonDisconnect_press)

        self.buttonChargingFinished = widgets.Button(description="Finish charging")
        self.buttonChargingFinished.on_click(self.on_buttonChargingFinished_press)

        self.buttonChargingAborted = widgets.Button(description="Abort charging")
        self.buttonChargingAborted.on_click(self.on_buttonChargingAborted_press)

        display(self.buttonConnect, self.buttonCharge, self.buttonDisconnect, self.buttonChargingFinished, self.buttonChargingAborted)


charger = Charger()

t0_initial = {'source': 'initial',
      'target': 'idle'}

t1_car_connected = {'trigger': 'car_connected',
        'source': 'idle',
        'target': 'connected'
}

t2_request_charging = {'trigger': 'request_charging',
        'source': 'connected',
        'target': 'charging'
}
t3_car_disconnected = {'trigger': 'car_disconnected',
        'source': 'connected',
        'target': 'idle'
}
t4_charging_finished = {'trigger': 'charging_finished',
        'source': 'charging',
        'target': 'connected'
}
t5_charging_aborted = {'trigger': 'charging_aborted',
        'source': 'charging',
        'target': 'connected'
}

idle = {'name': 'idle'}

connected = {'name': 'connected'}

charging = {'name': 'charging'}

machine = Machine(name='charger', transitions=[t0_initial, t1_car_connected, t2_request_charging, t3_car_disconnected, t4_charging_finished, t5_charging_aborted],
                                states=[idle, connected, charging], obj=charger)

charger.stm = machine
driver = Driver()
driver.add_machine(machine)
driver.start()