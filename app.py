import os
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import threading

import scripts as cf
import handlers as func

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('400x250')
        self.resizable(False, False)
        self._frame = None
        self.frame_history = []
        self.switch_frame(ConnectionPage)

        center_window(self)

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

        go_btn = tk.Button(self, text='Go', command=self.select_account)
        go_btn.pack(pady=5)

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

        with open('default_records.json', 'r') as file:
            self.default_records = json.load(file)
        
        default_server = 'd725' if 'd725' in self.default_records else (list(self.default_records.keys())[0] if self.default_records else '')
        self.selected_server = tk.StringVar(value=default_server)
        for option in self.default_records:
            tk.Radiobutton(self, text=option, variable=self.selected_server, value=option).pack()

        zone_entry_label = tk.Label(self, text='Enter Domain Name: ')
        zone_entry_label.pack(pady=(20, 10))
        
        self.zone_name_entry = tk.Entry(self, font=('Times', 12), width=30)
        self.zone_name_entry.pack(pady=(0, 20))

        add_zone_btn = tk.Button(self, text='Create Domain with Default DNS Records', command=self.add_zone)
        add_zone_btn.pack()

    def add_zone(self):
        zone_name = self.zone_name_entry.get().strip()
        if zone_name:
            default_records = self.default_records[self.selected_server.get()]
            for record in default_records:
                record['name'] = record['name'].replace('@', zone_name)

            loading_dialog = LoadingDialog(self)

            try:
                loading_dialog.update('Creating Zone...')
                zone_id = handle_zone_creation(zone_name, account_id)
                loading_dialog.update('Setting SSL...')
                handle_set_ssl(zone_id)
                loading_dialog.update('Adding DNS Records...')
                handle_add_dns_records(zone_id, default_records)
                loading_dialog.complete()
                messagebox.showinfo('Success', 'Zone Created Successfully')
            except Exception as e:
                messagebox.showerror('Error', str(e))
            finally:
                self.master.switch_frame(HomePage)
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


class RecordErrorDialog(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("Error")
        self.geometry("300x150")
        self.resizable(False, False)

        center_window(self)
        
        tk.Label(self, text=message, wraplength=280).pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.result = None

        abort_button = tk.Button(button_frame, text="Abort", command=self.abort)
        abort_button.pack(side="left", padx=5)

        retry_button = tk.Button(button_frame, text="Retry", command=self.retry)
        retry_button.pack(side="left", padx=5)

        skip_button = tk.Button(button_frame, text="Skip this Record", command=self.skip)
        skip_button.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.abort)

    def abort(self):
        self.result = "abort"
        self.destroy()

    def retry(self):
        self.result = "retry"
        self.destroy()

    def skip(self):
        self.result = "skip"
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result


class LoadingDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Working...")

        center_window(self)

        self.label = tk.Label(self, text='Starting...',)
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(self, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start()
        
        self.update_idletasks()

    def update(self, message):
        self.label.config(text=message)
        self.update_idletasks()

    def complete(self):
        self.label.config(text='Completed')
        self.update_idletasks()
        self.after(1000, self.destroy)

def center_window(window):
    window.update_idletasks()

    window_width = window.winfo_width()
    window_height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    window.geometry(f'{window_width}x{window_height}+{x}+{y}')

def handle_zone_creation(zone_name, account_id):
    response = cf.create_zone(zone_name, account_id)
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        raise Exception(f'Failed to Add Zone: {error_message}')
    zone_id = response.json()['result']['id']
    return zone_id

def handle_set_ssl(zone_id):
    response = cf.set_ssl(zone_id, 'strict')
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        raise Exception(f'Failed to Add Zone: {error_message}')

def handle_add_dns_records(zone_id, records):
    responses = {}
    for record in records:
        while True:     
            response = cf.add_dns_record(zone_id, record)
            action = handle_response(response)
            if action == 'retry':
                continue
            elif action == 'skip':
                break
            elif action == 'abort':
                return
            elif action == True:
                record_name = record['name']
                responses[record_name] = response.json()
                break

def handle_response(response):
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        result = response.json()['result']
        error_dialog = RecordErrorDialog(None, f'Failed to add DNS Record {result['type']} | {result['name']} | {result['content']}: {error_message}')
        action = error_dialog.show()
        return action
    return True

if __name__ == '__main__':
    app = App()
    app.mainloop()