!python3 -m pip install --upgrade stmpy
import stmpy
from stmpy import Machine, Driver
from IPython.display import clear_output


class scu_class:

    def on_init(self):
        clear_output(wait=True)
        self.stm.driver.print_status()

    def on_idle(self):
        clear_output(wait=True)
        self.stm.send('scu_idle') # <---- here we send a signal
        self.stm.driver.print_status()

    # car connected:
    def on_getCarData(self):
        clear_output(wait=True)
        self.stm.send('scu_getCarData')
        print(self.stm.driver.print_status())

        self.stm.send('charger_requestData')
        #if recievedDataFromCar == true:
        #    chargerFromCar_recievedData

    def on_updateCloud(self):
        clear_output(wait=True)
        self.stm.send('scu_updateCloud')
        print(self.stm.driver.print_status())
        
        self.stm.send('cloud_sendCarData')
        #if recievedNewDataFromCloud == true:
        #    cloud_recievedData
    
    def on_updateMobileApp(self):
        clear_output(wait=True)
        self.stm.send('scu_updateMobileApp')
        print(self.stm.driver.print_status())
        
        self.stm.send('mobileApp_nofityChargePlan')
    
    def on_noCloudCommunication(self):
        clear_output(wait=True)
        self.stm.send('scu_noCloudCommunication')
        print(self.stm.driver.print_status())
        
        self.stm.send('mobileApp_nofityNoCloud')
    
    # car connected 2:
    def on_chargeCar(self):
        clear_output(wait=True)
        self.stm.send('scu_chargeCar')
        print(self.stm.driver.print_status())
        
        self.stm.send('deliverChargeAccordingToPlan')
    
    def on_abortCharging(self):
        clear_output(wait=True)
        self.stm.send('scu_abortCharging')
        print(self.stm.driver.print_status())

        self.stm.send('cancelCharging')
        #if charging_cancelled == true:
        #    chargingAborted
    
    # mobile app request:
    def on_getCloudData(self):
        clear_output(wait=True)
        self.stm.send('scu_getCloudData')
        print(self.stm.driver.print_status())
    
    def on_getCarData(self):
        clear_output(wait=True)
        self.stm.send('scu_getCarData')
        print(self.stm.driver.print_status())
    
    def on_suggestChargingPlan(self):
        clear_output(wait=True)
        self.stm.send('scu_suggestChargingPlan')
        print(self.stm.driver.print_status())
    
    def on_updateChargingPlan(self):
        clear_output(wait=True)
        self.stm.send('scu_updateChargingPlan')
        print(self.stm.driver.print_status())

scu = scu_class()

# initial transition
t0 = {
    "source": "initial",
    "target": "s_idle",
    "effect": "on_init",
}

# transition s_init ----> s_idle
t1 = {
    "source": "s_init",
    "target": "s_idle",
    "effect": "on_idle",
}

# car connected:
# transition s_idle ----> s_getCarData
t2 = {
    "trigger": "car_connected",
    "source": "s_idle",
    "target": "s_getCarData",
    "effect": "on_getCarData",
}

# transition s_getCarData ----> s_updateCloud
t3 = {
    "trigger": "chargerFromCar_recievedData",
    "source": "s_getCarData",
    "target": "s_updateCloud",
    "effect": "on_updateCloud; start_timer('t', 50000)",
}

# transition s_updateCloud ----> s_noCloudCommunication
t4 = {
    "trigger": "t",
    "source": "s_updateCloud",
    "target": "s_noCloudCommunication",
    "effect": "on_noCloudCommunication",
}

# transition s_noCloudCommunication ----> s_idle
t5 = {
    "source": "s_noCloudCommunication",
    "target": "s_idle",
    "effect": "on_idle",
}

# transition s_updateCloud ----> s_updateMobileApp
t6 = {
    "trigger": "cloud_recievedData",
    "source": "s_updateCloud",
    "target": "s_updateMobileApp",
    "effect": "on_updateMobileApp",
}

# transition s_updateMobileApp ----> s_idle
t7 = {
    "source": "s_updateMobileApp",
    "target": "s_idle",
    "effect": "on_idle",
}

# car connected 2:
t8 = {
    "trigger": "car_connected",
    "source": "s_idle",
    "target": "s_chargeCar",
    "effect": "on_chargeCar",
}

t9 = {
    "trigger": "chargingComplete",
    "source": "s_chargeCar",
    "target": "s_idle",
    "effect": "on_idle",
}

t10 = {
    "trigger": "rescheduleCharging",
    "source": "s_chargeCar",
    "target": "s_abortCharging",
    "effect": "on_abortCharging",
}

t11 = {
    "trigger": "chargingAborted",
    "source": "s_abortCharging",
    "target": "s_idle",
    "effect": "on_idle",
}

# mobile app request:
t12 = {
    "trigger": "mobileApp_requestFrom",
    "source": "s_idle",
    "target": "s_getCloudData",
    "effect": "on_getCloudData",
}


scu_machine = Machine( name="SCU", transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12], obj=scu)



import paho.mqtt.client as mqtt


