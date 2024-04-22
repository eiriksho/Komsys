from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display

class SCU:
    
    def on_buttonConnect_press(self, b):
        self.stm.send('car_connected') # <---- here we send a signal
    
    def on_buttonCharge_press(self, b):
        self.stm.send('charge') # <---- here we send a signal
    
    def on_buttonDisconnect_press(self, b):
        self.stm.send('car_disconnected') # <---- here we send a signal

    def on_buttonChargingFinished_press(self, b):
        self.stm.send('charging_finished') # <---- here we send a signal
    
    def on_buttonChargingAborted_press(self, b):
        self.stm.send('charging_aborted') # <---- here we send a signal

    def on_buttonPlanWanted_press(self, b):
        self.stm.send('plan_wanted') # <---- here we send a signal
    
    def on_buttonPlanMade_press(self, b):
        self.stm.send('plan_made') # <---- here we send a signal
           
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
        
        self.buttonPlanWanted = widgets.Button(description="request charging plan")
        self.buttonPlanWanted.on_click(self.on_buttonPlanWanted_press)

        self.buttonPlanMade = widgets.Button(description="plan is made")
        self.buttonPlanMade.on_click(self.on_buttonPlanMade_press)

        display(self.buttonConnect, self.buttonCharge, self.buttonDisconnect, self.buttonChargingFinished, self.buttonChargingAborted, self.buttonPlanWanted, self.buttonPlanMade)


scu = SCU()

t0_initial = {'source': 'initial',
      'target': 'idle'}

t1_car_connected = {'trigger': 'car_connected',
        'source': 'idle',
        'target': 'carConnected'
}

t2_plan_wanted = {'trigger': 'plan_wanted',
        'source': 'carConnected',
        'target': 'createPlan'
}
t3_plan_made = {'trigger': 'plan_made',
        'source': 'createPlan',
        'target': 'carConnected'
}
t4_charge = {'trigger': 'charge',
        'source': 'carConnected',
        'target': 'chargeCar'
}
t5_charging_stopped = {'trigger': 'charging_stopped',
        'source': 'chargeCar',
        'target': 'carConnected'
}
t6_charging_aborted = {'trigger': 'charging_aborted',
        'source': 'chargeCar',
        'target': 'carConnected'
}
t7_car_disconnected = {'trigger': 'car_disconnected',
        'source': 'carConnected',
        'target': 'idle'
}

idle = {'name': 'idle'}

carConnected = {'name': 'carConnected'}

chargeCar = {'name': 'chargeCar'}

createPlan = {'name': 'createPlan'}

machine = Machine(name='SCU', transitions=[t0_initial, t1_car_connected, t2_plan_wanted, t3_plan_made, t4_charge, t5_charging_stopped, t6_charging_aborted, t7_car_disconnected],
                                states=[idle, carConnected, chargeCar, createPlan], obj=scu)

scu.stm = machine
driver = Driver()
driver.add_machine(machine)
driver.start()