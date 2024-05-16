import tkinter as tk
from tkinter import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('720x550')
        self.resizable(True, True)

        container = tk.Frame(self)
        container.pack()

        self.frames = {}
        self.HomePage = Connection

        for F in {Connection}:
            frame = F(self, container)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Connection)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # menubar = frame.create_menubar(self)
        # self.configure(menu=menubar)
        frame.tkraise()


class Connection(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.pack()

        label = tk.Label(self, text="Connect to Cloudflare Account", font=('Times', '20'))
        label.pack(pady=10,padx=10)

        tk.Label(self, text='API Key:').pack()
        self.api_key = tk.Entry(self)
        self.api_key.pack()

        tk.Label(self, text="Email:").pack()
        self.email = tk.Entry(self)
        self.email.pack()

        test_conn_btn = tk.Button(self, text='Test Connection', command=self.test_connection)
        test_conn_btn.pack(pady=5)

        self.text = tk.Label(self, text="", font=('Times', 8))
        self.text.pack(pady=5)


    def test_connection(self):
        self.text.config(text='Connection Established', fg='green')


if __name__ == "__main__":
    app = App()
    app.mainloop()