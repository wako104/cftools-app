import os
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

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


class Base(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.add_home_button(master)

    def add_home_button(self, master):
        button = tk.Button(self, text="Home Page", command=lambda: master.switch_frame(HomePage))
        button.pack(anchor='w', padx=10, pady=10)


class ConnectionPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        label = tk.Label(self, text="Connect to Cloudflare Account", font=('Times', '20'))
        label.pack(pady=10,padx=10)

        env_conn_btn = tk.Button(self, text='Connect Using Environment Variables', command=self.conn_with_env)
        env_conn_btn.pack(pady=5)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=15, pady=10)

        tk.Label(self, text='API Key:').pack()
        self.api_key = tk.Entry(self)
        self.api_key.pack()

        tk.Label(self, text="Email:").pack()
        self.email = tk.Entry(self)
        self.email.pack()

        conn_btn = tk.Button(self, text='Connect', command=self.conn)
        conn_btn.pack(pady=5)

    def conn(self):
        api_key = self.api_key.get()
        email = self.email.get()

        if cf.validate_key(api_key=api_key, email=email):
            messagebox.showinfo('Success', 'Connection Established')
            self.master.switch_frame(HomePage)
        else:
            messagebox.showerror('Error', 'Connection Failed')

    def conn_with_env(self):
        try:
            api_key = os.environ['CLOUDFLARE_API_KEY']
            email = os.environ['CLOUDFLARE_EMAIL']
        except:
            messagebox.showerror('Error', 'Could Not Find Environment Variables')

        if cf.validate_key(api_key=api_key, email=email):
            messagebox.showinfo('Success', 'Connection Established')
            self.master.switch_frame(HomePage)
        else:
            messagebox.showerror('Error', 'Connection Failed')


class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.geometry('720x550')

        heading = tk.Label(self, text="Cloudflare Manager", font=('Times', '20'))
        heading.pack(pady=10,padx=10)

        zone_btn = tk.Button(self, text='Zones', command=lambda: master.switch_frame(ZonePage))
        zone_btn.pack(pady=5)

        records_btn = tk.Button(self, text='DNS Records', command=lambda: master.switch_frame(RecordsPage))
        records_btn.pack(pady=5)


class ZonePage(Base):
    def __init__(self, master):
        super().__init__(master)
    
        heading = tk.Label(self, text="Zone Manager", width=80, font=('Times', '20'))
        heading.pack(pady=10, padx=10)


class RecordsPage(Base):
    def __init__(self, master):
        super().__init__(master)

        heading = tk.Label(self, text="DNS Records Manager", width=80, font=('Times', '20'))
        heading.pack(pady=10,padx=10)

        search_and_replace_btn = tk.Button(self, text="Search and Replace", command=lambda: master.switch_frame(SearchAndReplacePage))
        search_and_replace_btn.pack(pady=5)


class SearchAndReplacePage(Base):
    def __init__(self, master):
        super().__init__(master)


class SearchAndAddPage(Base):
    def __init__(self, master):
        super().__init__(master)


class SearchAndRemovePage(Base):
    def __init__(self, master):
        super().__init__(master)


class ReplaceAllPage(Base):
    def __init__(self, master):
        super().__init__(master)      


class AddToAllPage(Base):
    def __init__(self, master):
        super().__init__(master)


class RemoveFromAllPage(Base):
    def __init__(self, master):
        super().__init__(master)


if __name__ == "__main__":
    app = App()
    app.mainloop()