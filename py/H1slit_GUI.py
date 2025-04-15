# -*- coding: utf-8 -*-
import Tkinter as tk
import tkMessageBox
from H1slit_controller import H1SlitController

class MotorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("H1Slit Motor Controller")

        self.controller = H1SlitController()
        self.controller.open_ser()

        self.entries = {}
        self.log = tk.Text(master, height=10, width=80)
        self.log.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        for i in range(4):
            seg = i + 1
            frame = tk.LabelFrame(master, text="Motor SEG %d" % seg, padx=10, pady=10)
            frame.grid(row=i // 2, column=i % 2, padx=10, pady=10)

            tk.Label(frame, text="Value:").grid(row=0, column=0)
            entry = tk.Entry(frame)
            entry.grid(row=0, column=1)
            self.entries[seg] = entry

            tk.Button(frame, text="Home", command=lambda s=seg: self.home_motor(s)).grid(row=1, column=0)
            tk.Button(frame, text="Abs Move", command=lambda s=seg: self.abs_move(s)).grid(row=1, column=1)
            tk.Button(frame, text="Rel Move", command=lambda s=seg: self.rel_move(s)).grid(row=2, column=0)
            tk.Button(frame, text="Read Pos", command=lambda s=seg: self.read_position(s)).grid(row=2, column=1)
            tk.Button(frame, text="Reset Home", command=lambda s=seg: self.reset_home(s)).grid(row=3, column=0)
            #tk.Button(frame, text="Read Home Param", command=lambda s=seg: self.read_home_params(s)).grid(row=3, column=1)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_message(self, msg):
        self.log.insert(tk.END, msg + '\n')
        self.log.see(tk.END)

    def home_motor(self, seg):
        try:
            self.log_message("SEG %d: Homing..." % seg)
            self.controller.home(seg)
            self.log_message("SEG %d: Homing complete" % seg)
        except Exception as e:
            tkMessageBox.showerror("Error", str(e))

    def abs_move(self, seg):
        try:
            pos = int(self.entries[seg].get())
            self.log_message("SEG %d: Moving to absolute %d" % (seg, pos))
            self.controller.absolute(seg, pos)
            self.log_message("SEG %d: Move complete" % seg)
        except Exception as e:
            tkMessageBox.showerror("Error", str(e))

    def rel_move(self, seg):
        try:
            step = int(self.entries[seg].get())
            self.log_message("SEG %d: Moving relatively by %d" % (seg, step))
            self.controller.step(seg, step)
            self.log_message("SEG %d: Move complete" % seg)
        except Exception as e:
            tkMessageBox.showerror("Error", str(e))

    def read_position(self, seg):
        try:
            pos = self.controller.get_position(seg)
            self.log_message("SEG %d: Current Position = %d" % (seg, pos))
        except Exception as e:
            tkMessageBox.showerror("Error", str(e))

    def reset_home(self, seg):
        try:
            self.controller.reset_home(seg)
            self.log_message("SEG %d: Home parameters reset" % seg)
        except Exception as e:
            tkMessageBox.showerror("Error", str(e))

    def read_home_params(self, seg):
        try:
            self.controller.read_home_params(seg)
            self.log_message("SEG %d: Read home parameters (see console)" % seg)
        except Exception as e:
            tkMessageBox.showerror("Error", str(e))

    def on_closing(self):
        self.controller.close_ser()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MotorGUI(root)
    root.mainloop()
