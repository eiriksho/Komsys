from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display

class KitchenTimer:
    
    def on_button_press(self, b):
        self.stm.send('switch') # <---- here we send a signal
            
    def __init__(self):
        # load images and store them
        self.on_60 = open("images/timer/on_60.jpg", "rb").read()
        self.off_60 = open("images/timer/off_60.jpg", "rb").read()
        self.on_45 = open("images/timer/on_45.jpg", "rb").read()
        self.off_45 = open("images/timer/off_45.jpg", "rb").read()
        self.on_30 = open("images/timer/on_30.jpg", "rb").read()
        self.off_30 = open("images/timer/off_30.jpg", "rb").read()
        self.on_15 = open("images/timer/on_15.jpg", "rb").read()
        self.off_15 = open("images/timer/off_15.jpg", "rb").read()
        self.plug_on = open("images/timer/plug_on.jpg", "rb").read()
        self.plug_off = open("images/timer/plug_off.jpg", "rb").read()
        
        self.led_15 = widgets.Image(value=self.off_15, format='jpg', width=50, height=50)
        self.led_30 = widgets.Image(value=self.off_30, format='jpg', width=50, height=50)
        self.led_45 = widgets.Image(value=self.off_45, format='jpg', width=50, height=50)
        self.led_60 = widgets.Image(value=self.off_60, format='jpg', width=50, height=50)
        
        left_box = widgets.VBox([self.led_60, self.led_45])
        right_box = widgets.VBox([self.led_15, self.led_30])
        box = widgets.HBox([left_box, right_box])
        self.plug = widgets.Image(value=self.plug_off, format='jpg', width=100, height=100)
        
        # display the user interface
        # a button
        self.button = widgets.Button(description="Button")
        self.button.on_click(self.on_button_press)
        
        display(box, self.button, self.plug)
        
    
    def switch_led(self, led, on):
        if led == '15' and on: self.led_15.set_trait(name='value', value=self.on_15)
        if led == '15' and not on: self.led_15.set_trait(name='value', value=self.off_15) 
        if led == '30' and on: self.led_30.set_trait(name='value', value=self.on_30)
        if led == '30' and not on: self.led_30.set_trait(name='value', value=self.off_30) 
        if led == '45' and on: self.led_45.set_trait(name='value', value=self.on_45)
        if led == '45' and not on: self.led_45.set_trait(name='value', value=self.off_45) 
        if led == '60' and on: self.led_60.set_trait(name='value', value=self.on_60)
        if led == '60' and not on: self.led_60.set_trait(name='value', value=self.off_60) 
            
    def switch_plug(self, on):
        if on: self.plug.set_trait(name='value', value=self.plug_on)
        else: self.plug.set_trait(name='value', value=self.plug_off) 



kitchentimer = KitchenTimer()

t0 = {'source': 'initial',
      'target': 'off'}

t1 = {'trigger': 'switch',
        'source': 'off',
        'target': 'led_15min'
}

t2 = {'trigger': 'switch',
        'source': 'led_15min',
        'target': 'led_30min'
}
t3 = {'trigger': 'switch',
        'source': 'led_30min',
        'target': 'led_45min'
}
t4 = {'trigger': 'switch',
        'source': 'led_45min',
        'target': 'led_60min'
}
t5 = {'trigger': 'switch',
        'source': 'led_60min',
        'target': 'off'
}

t6 = {'trigger' : 'time',
      'source' : 'led_60min',
      'target' : 'led_45min'
}

t7 = {'trigger' : 'time',
      'source' : 'led_45min',
      'target' : 'led_30min'
}

t8 = {'trigger' : 'time',
      'source' : 'led_30min',
      'target' : 'led_15min'
}

t9 = {'trigger' : 'time',
      'source' : 'led_15min',
      'target' : 'off'
}

off = {'name': 'off',
       'entry' : 'switch_plug(False); switch_led("15", False); switch_led("30", False); switch_led("45", False); switch_led("60", False)'}

led_15min = {'name': 'led_15min',
        'entry': 'switch_led("15", True);switch_led("30", False); start_timer("time", 1000); switch_plug(True)'
}

led_30min = {'name': 'led_30min',
        'entry': 'switch_led("30", True);switch_led("45", False); start_timer("time", 1000)'
}

led_45min = {'name': 'led_45min',
        'entry': 'switch_led("45", True);switch_led("60", False); start_timer("time", 1000)',
}
led_60min = {'name': 'led_60min',
        'entry': 'switch_led("60", True); start_timer("time", 1000)',
}

machine = Machine(name='kitchentimer', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9], 
                           states=[off, led_15min, led_30min, led_45min, led_60min], obj=kitchentimer)
kitchentimer.stm = machine
driver = Driver()
driver.add_machine(machine)
driver.start()