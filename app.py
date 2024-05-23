import os
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json

import scripts as cf

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('400x250')
        self.resizable(False, False)
        self._frame = None
        self.frame_history = []
        self.switch_frame(ConnectionPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self.frame_history.append(self._frame.__class__)
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def previous_frame(self):
        if self.frame_history:
            frame = self.frame_history.pop()
            self.switch_frame(frame)
        else:
            messagebox.showinfo('Info', 'No previous page available')


class Base(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.geometry('720x400')
        master.resizable(False, False)
        self.add_home_button(master)
        self.add_back_button(master)

    def add_home_button(self, master):
        button = tk.Button(self, text='Home Page', command=lambda: master.switch_frame(HomePage))
        button.pack(anchor='w', padx=10, pady=10)

    def add_back_button(self, master):
        button = tk.Button(self, text='Back', command=lambda: master.previous_frame())
        button.pack(anchor='w', padx=10, pady=5)


class ConnectionPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        heading = tk.Label(self, text='Connect to Cloudflare Account', font=('Times', '20'))
        heading.pack(pady=10,padx=10)

        env_conn_btn = tk.Button(self, text='Connect Using Environment Variables', command=self.conn_with_env)
        env_conn_btn.pack(pady=5)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=15, pady=10)

        tk.Label(self, text='API Key:').pack()
        self.api_key = tk.Entry(self)
        self.api_key.pack()

        tk.Label(self, text='Email:').pack()
        self.email = tk.Entry(self)
        self.email.pack()

        conn_btn = tk.Button(self, text='Connect', command=self.conn)
        conn_btn.pack(pady=5)

    def conn(self):
        api_key = self.api_key.get()
        email = self.email.get()

        if cf.validate_key(api_key=api_key, email=email):
            messagebox.showinfo('Success', 'Connection Established')
            self.master.switch_frame(AccountSelect)
        else:
            messagebox.showerror('Error', 'Connection Failed')

    def conn_with_env(self):
        try:
            api_key = os.environ['CLOUDFLARE_API_KEY']
            email = os.environ['CLOUDFLARE_EMAIL']
            if cf.validate_key(api_key=api_key, email=email):
                messagebox.showinfo('Success', 'Connection Established')
                self.master.switch_frame(AccountSelect)
            else:
                messagebox.showerror('Error', 'Connection Failed')
        except:
            messagebox.showerror('Error', 'Could Not Find Environment Variables')


class AccountSelect(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        heading = tk.Label(self, text='Select Account', font=('Times', '20'))
        heading.pack(pady=10,padx=10)

        self.accounts = cf.get_cloudflare_accounts()
        self.account_var = tk.StringVar()

        account_select = ttk.Combobox(self, textvariable=self.account_var, state='readonly')
        account_select['values'] = [name for _, name in self.accounts]
        if self.accounts:
            self.account_var.set(self.accounts[0][1])
        account_select.pack(pady=10, padx=10)

        tk.Button(self, text='Go', command=self.select_account).pack(pady=5)

    def select_account(self):
        global account_id
        account_id = next((id for id, name in self.accounts if name == self.account_var.get()), None)
        if account_id:
            self.master.switch_frame(HomePage)
        else:
            messagebox.showerror('Selection Error', 'No Account Selected')


class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.geometry('400x250')

        heading = tk.Label(self, text='Cloudflare Manager', font=('Times', '20'))
        heading.pack(pady=10,padx=10)

        zone_btn = tk.Button(self, text='Zones', width=10, height=3, command=lambda: master.switch_frame(ZonePage))
        zone_btn.pack(pady=5)

        records_btn = tk.Button(self, text='DNS Records', width=10, height=3, command=lambda: master.switch_frame(RecordsPage))
        records_btn.pack(pady=5)


class ZonePage(Base):
    def __init__(self, master):
        super().__init__(master)
    
        heading = tk.Label(self, text='Zone Manager', width=80, font=('Times', '20'))
        heading.pack(pady=10, padx=10)

        add_btn = tk.Button(self, text='Quick Add', width=15, command=lambda: master.switch_frame(QuickAddZone))
        add_btn.pack(pady=5)

        add_btn = tk.Button(self, text='Add', width=15)
        add_btn.pack(pady=5)

        add_btn = tk.Button(self, text='Remove', width=15)
        add_btn.pack(pady=5)


class QuickAddZone(Base):
    def __init__(self, master):
        super().__init__(master)

        heading = tk.Label(self, text='Quick Add', width=80, font=('Times', '20'))
        heading.pack(pady=10, padx=10)

        with open('defaults.json', 'r') as file:
            self.default_records = json.load(file)
        
        self.selected_server = tk.StringVar(value='d725')
        for option in self.default_records:
            tk.Radiobutton(self, text=option, variable=self.selected_server, value=option).pack()

        tk.Label(self, text='Enter Domain Name: ').pack(pady=(20, 10))
        
        self.zone_name_entry = tk.Entry(self, font=('Times', 12), width=30)
        self.zone_name_entry.pack(pady=(0, 20))

        add_zone_btn = tk.Button(self, text='Create Domain with Default DNS Records', command=self.add_zone)
        add_zone_btn.pack()

    def add_zone(self):
        zone_name = self.zone_name_entry.get().strip()
        if zone_name:
            selected_records = self.default_records[self.selected_server.get()]
            if cf.create_zone(zone_name, account_id, selected_records):
                messagebox.showinfo('Success', 'Zone Created Successfully')
                self.master.switch_frame(HomePage)
            else:
                messagebox.showerror('Error', 'Failed to Add Zone')
        else:
            messagebox.showwarning('Input Error', 'Please Enter a Valid Domain Name')


class AddZone(Base):
    def __init__(self, master):
        super().__init__(master)


class RemoveZone(Base):
    def __init__(self, master):
        super().__init__(master)


class RecordsPage(Base):
    def __init__(self, master):
        super().__init__(master)

        heading = tk.Label(self, text='DNS Records Manager', width=80, font=('Times', '20'))
        heading.pack(pady=10,padx=10)

        tk.Button(self, text='Search and Replace', width=15, command=lambda: master.switch_frame(SearchAndReplacePage)).pack(pady=5)

        tk.Button(self, text='Search and Add', width=15, command=lambda: master.switch_frame(SearchAndAddPage)).pack(pady=5)

        tk.Button(self, text='Search and Remove', width=15, command=lambda: master.switch_frame(SearchAndRemovePage)).pack(pady=5)

        tk.Button(self, text='Replace All', width=15, command=lambda: master.switch_frame(ReplaceAllPage)).pack(pady=5)

        tk.Button(self, text='Add to All', width=15, command=lambda: master.switch_frame(AddToAllPage)).pack(pady=5)

        tk.Button(self, text='Remove from All', width=15, command=lambda: master.switch_frame(RemoveFromAllPage)).pack(pady=5)


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


if __name__ == '__main__':
    app = App()
    app.mainloop()