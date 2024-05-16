import tkinter as tk
from tkinter import *
from tkinter import messagebox

import scripts as cf

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('400x250')
        self._frame = None
        self.switch_frame(ConnectionPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()



class ConnectionPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        label = tk.Label(self, text="Connect to Cloudflare Account", font=('Times', '20'))
        label.pack(pady=10,padx=10)

        tk.Label(self, text='API Key:').pack()
        self.api_key = tk.Entry(self)
        self.api_key.pack()

        tk.Label(self, text="Email:").pack()
        self.email = tk.Entry(self)
        self.email.pack()

        test_conn_btn = tk.Button(self, text='Test Connection', command=self.check_connection)
        test_conn_btn.pack(pady=5)

    def check_connection(self):
        api_key = self.api_key.get()
        email = self.email.get()

        if cf.validate_key(api_key=api_key, email=email):
            messagebox.showinfo('Success', 'Connection Established')
            self.master.switch_frame(HomePage)
        else:
            messagebox.showerror('Error', 'Connection Failed')


class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.geometry('720x550')

        label = tk.Label(self, text="Cloudflare Manager", font=('Times', '20'))
        label.pack(pady=10,padx=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()