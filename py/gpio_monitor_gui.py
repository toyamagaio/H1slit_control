# -*- coding: utf-8 -*-
import Tkinter as tk
import time
from gpio_controller import GPIOController

class MultiGPIOGuiApp(object):
    def __init__(self, master, pins):
        self.master = master
        self.pins = pins
        self.labels = {}
        self.controller = GPIOController(pins)

        self.log = tk.Text(master, height=10, width=60)
        self.log.grid(row=len(pins), column=0, columnspan=2, pady=10)

        for idx, pin in enumerate(pins):
            label = tk.Label(master, text="GPIO %d: UNKNOWN" % pin,
                             font=('Helvetica', 16), width=25, relief='ridge')
            label.grid(row=idx, column=0, padx=10, pady=5)
            self.labels[pin] = label

            # check current status
            state = self.controller.get_state(pin)
            self.update_label(pin, state)

            # register callback
            self.controller.register_callback(pin, self._make_callback(pin))

        tk.Button(master, text="stop", command=self.cleanup_and_exit,
                  bg="gray", fg="white", width=20).grid(row=len(pins)+1, column=0, pady=10)

    def _make_callback(self, pin):
        def callback(pin, state):
            self.master.after(0, self.update_label, pin, state)
        return callback

    def update_label(self, pin, state):
        text = "GPIO %d: %s" % (pin, "HIGH" if state else "LOW")
        color = "green" if state else "red"
        self.labels[pin].config(text=text, bg=color)
        self.write_log("[%s] GPIO %d: %s" % (
            time.strftime("%H:%M:%S"), pin, "HIGH" if state else "LOW"))

    def write_log(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def cleanup_and_exit(self):
        self.controller.cleanup()
        self.master.destroy()


if __name__ == "__main__":
    pins_to_monitor = [17, 18, 27]
    root = tk.Tk()
    root.title("GPIO monitor GUI")
    app = MultiGPIOGuiApp(root, pins=pins_to_monitor)
    root.mainloop()
