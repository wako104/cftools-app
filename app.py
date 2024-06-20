import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

import handlers as func 
import scripts as cf

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, 'images', 'osam-logo-orange.png')
icon_path = os.path.join(script_dir, 'images', 'osam-logo.png')
default_records_path = os.path.join(script_dir, 'config', 'default_records.json')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('900x600')

        #--------------- SIDEBAR ---------------
        self.sidebar = tk.Frame(self)
        self.sidebar.pack(side='left', fill='y')
        # dashboard
        self.logo_image = tk.PhotoImage(file=logo_path)
        self.logo = self.logo_image.subsample(5,5)

        self.icon = tk.PhotoImage(file=icon_path)
        self.wm_iconphoto(True, self.icon)

        self.dashboard_btn = ttk.Button(self.sidebar, image=self.logo, command=lambda: self.switch_frame(Dashboard, 'Dashboard'), state='disabled')
        self.dashboard_btn.pack(padx=10, pady=13)
        # separator
        self.separator = ttk.Separator(self.sidebar)
        self.separator.pack(fill='x', padx=10, pady=5)
        # zones
        self.zones_label = ttk.Label(self.sidebar, text='Zones')
        self.zones_label.pack(padx=10, pady=5)
        self.quick_add_zone_btn = ttk.Button(self.sidebar, text='Quick Add Zone', command=lambda: self.switch_frame(QuickAddZonePage, 'Quick Add Zone'), state='disabled')
        self.quick_add_zone_btn.pack(padx=10, pady=5)
        self.add_zone_btn = ttk.Button(self.sidebar, text='Add Zone', command=lambda: self.switch_frame(AddZonePage, 'Add Zone'), state='disabled')
        self.add_zone_btn.pack(padx=10, pady=5)
        self.rmv_zone_btn = ttk.Button(self.sidebar, text='Remove Zone', command=lambda: self.switch_frame(RemoveZonePage, 'Remove Zone'), state='disabled')
        self.rmv_zone_btn.pack(padx=10, pady=5)
        # separator
        self.separator = ttk.Separator(self.sidebar)
        self.separator.pack(fill='x', padx=10, pady=5)
        # records
        self.records_label = ttk.Label(self.sidebar, text='DNS Records')
        self.records_label.pack(padx=10, pady=5)
        self.s_and_r_btn = ttk.Button(self.sidebar, text='Search and Replace', command=lambda: self.switch_frame(SearchAndReplace, 'DNS Search and Replace'), state='disabled')
        self.s_and_r_btn.pack(padx=10, pady=5)

        #------------- RIGHT SIDE -------------
        self.right_side = tk.Frame(self)

        self.right_side.pack(side='left', fill='both', expand=True)

        #--------------- HEADER ----------------
        self.header = tk.Frame(self.right_side)
        self.header_label = ttk.Label(self.header, anchor='center', font=('helvetica', '20'))

        self.header.pack(fill='both')
        self.header_label.pack(fill='both', padx=10, pady=10)

        #---------------- MAIN -----------------
        self.main_placeholder = tk.Frame(self.right_side, highlightthickness=1, highlightbackground='black', bd=0)
        self.main_frame = tk.Frame(self.main_placeholder)

        self.main_placeholder.pack(expand=True, fill='both', padx=(0,5), pady=(0,5))
        self.main_frame.pack(expand=True, pady=(0,50))

        self.current_frame = None
        self.switch_frame(ConnectionPage, 'Connect to Cloudflare Account')

    def switch_frame(self, frame_class, header_text, **kwargs):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        new_frame = frame_class(self.main_frame, self, **kwargs)
        new_frame.pack(fill='both', expand=True)
        self.current_frame = new_frame

        self.header_label.config(text=header_text)
    
    def enable_sidebar(self):
        self.dashboard_btn.config(state='normal')
        self.quick_add_zone_btn.config(state='normal')
        # self.add_zone_btn.config(state='normal')
        # self.rmv_zone_btn.config(state='normal')
        # self.s_and_r_btn.config(state='normal')


class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        env_conn_btn = ttk.Button(self, text='Connect Using Environment Variables', command=self.conn_with_env)
        env_conn_btn.pack(pady=5)

        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', padx=15, pady=30)

        ttk.Label(self, text='API Key:').pack()
        self.api_key = ttk.Entry(self)
        self.api_key.pack(pady=5)

        ttk.Label(self, text='Email:').pack()
        self.email = ttk.Entry(self)
        self.email.pack(pady=5)

        conn_btn = ttk.Button(self, text='Connect', command=self.conn)
        conn_btn.pack(pady=5)

    def conn(self):
        api_key = self.api_key.get()
        email = self.email.get()

        if func.handle_connection(api_key=api_key, email=email):
            messagebox.showinfo('Success', 'Connection Established')
            self.controller.switch_frame(AccountSelect, 'Select Account')
        else:
            messagebox.showerror('Error', 'Connection Failed')

    def conn_with_env(self):
        try:
            api_key = os.environ['CLOUDFLARE_API_KEY']
            email = os.environ['CLOUDFLARE_EMAIL']
            if func.handle_connection(api_key=api_key, email=email):
                messagebox.showinfo('Success', 'Connection Established')
                self.controller.switch_frame(AccountSelect, 'Select Account')
            else:
                messagebox.showerror('Error', 'Connection Failed')
        except:
            messagebox.showerror('Error', 'Could Not Find Environment Variables')


class AccountSelect(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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
            self.controller.enable_sidebar()
            self.controller.switch_frame(Dashboard, 'Dashboard')
        else:
            messagebox.showerror('Selection Error', 'No Account Selected')


class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        welcome_label = ttk.Label(self, text='Welcome', foreground='grey')
        welcome_label.pack()
        account_id_label = ttk.Label(self, text='Account ID: ' + account_id, foreground='grey')
        account_id_label.pack()


class QuickAddZonePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.records = []

        with open(default_records_path, 'r') as file:
            self.default_records = json.load(file)

        server_label = ttk.Label(self, text='Choose Server:')
        server_label.pack(pady=10)

        default_server = list(self.default_records.keys())[0] if self.default_records else ''
        self.selected_server = tk.StringVar(value=default_server)
        for option in self.default_records:
            ttk.Radiobutton(self, text=option, variable=self.selected_server, value=option).pack()

        zone_entry_label = ttk.Label(self, text='Enter Domain Name: ')
        zone_entry_label.pack(pady=(20,10))
        
        self.zone_name_entry = ttk.Entry(self, font=('Times', 12), width=30)
        self.zone_name_entry.pack(pady=10)

        add_zone_btn = ttk.Button(self, text='Create Domain with Default DNS Records', command=self.add_zone)
        add_zone_btn.pack(pady=10)

    def add_zone(self):
        self.zone_name = self.zone_name_entry.get().strip()
        if self.zone_name:
            self.selected_records = self.default_records[self.selected_server.get()]
            for record in self.selected_records:
                record['name'] = record['name'].replace('@', self.zone_name)

            loading_dialog = LoadingDialog(self)
            try:
                loading_dialog.update('Creating Zone...')
                self.zone_id, self.name_servers = func.handle_zone_creation(self.zone_name, account_id)
                loading_dialog.update('Setting SSL...')
                func.handle_set_ssl(self.zone_id)
                loading_dialog.update('Enabling Always Use HTTPS...')
                func.handle_always_use_https(self.zone_id)
                loading_dialog.update('Adding DNS Records...')
                self.records = func.handle_add_dns_records(self.zone_id, self.selected_records)
                loading_dialog.complete()
            except Exception as e:
                messagebox.showerror('Error', str(e))
                loading_dialog.destroy()
            self.controller.switch_frame(ZoneCompletePage, f'Zone Created ({self.zone_name})', records=self.records, zone_name=self.zone_name, zone_id=self.zone_id, name_servers=self.name_servers)
        else:
            messagebox.showwarning('Input Error', 'Please Enter a Valid Domain Name')


class AddZonePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller


class ZoneCompletePage(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.records = kwargs.get('records')
        self.zone_name = kwargs.get('zone_name')
        self.zone_id = kwargs.get('zone_id')
        self.name_servers = kwargs.get('name_servers')

        self.link = f'dash.cloudflare.com/{self.zone_id}/{self.zone_name}'

        zone_name_label = ttk.Label(self, text='Domain: ' + self.zone_name)
        zone_name_label.pack(pady=10)

        for i, name_server in enumerate(self.name_servers):
            ns_frame = tk.Frame(self)
            ns_frame.pack(pady=5)
            ns_label = ttk.Label(ns_frame, text=f'Nameserver {i+1}: {name_server}')
            ns_label.pack(side='left')
            ns_copy_btn = ttk.Button(ns_frame, text='📋', width=5, command=lambda ns=name_server: self.copy_to_clipboard(ns))
            ns_copy_btn.pack(side='right')

        records_label = ttk.Label(self, text=f'{len(self.records)} Records Added:')
        records_label.pack(pady=10)

        table_frame = ttk.Frame(self)
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        columns=('Type', 'Name', 'Content', 'Proxy Status', 'TTL')
        table = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=150)

        for record in self.records:
            result = record.get('result', {})
            type = result.get('type', 'N/A')
            name = result.get('name', 'N/A')
            content = result.get('content', 'N/A')
            proxied = result.get('proxied', 'N/A')
            ttl = result.get('ttl', 'N/A')
            table.insert('', tk.END, values=(type, name, content, proxied, ttl))

        table.pack(fill=tk.BOTH, expand=True)

    def copy_to_clipboard(self, text):
        self.controller.clipboard_clear()
        self.controller.clipboard_append(text)


class RemoveZonePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        zone_entry_label = ttk.Label(self, text='Enter Domain Name: ')
        zone_entry_label.pack(pady=(20,10))

        self.zone_name_entry = ttk.Entry(self, font=('Times', 12), width=30)
        self.zone_name_entry.pack(pady=10)

        add_zone_btn = ttk.Button(self, text='Remove Zone from Cloudflare', command=self.remove_zone)
        add_zone_btn.pack(pady=10)

    # def remove_zone(self):
    #     self.zone_name = self.zone_name_entry.get().strip()
    #     if self.zone_name:
    #         func.handle_remove_zone(zone_name):

        

class SearchAndReplace(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller


class RecordErrorDialog(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title('Error')
        self.geometry('300x150')
        self.resizable(False, False)
        
        tk.Label(self, text=message, wraplength=280).pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.result = None

        abort_button = tk.Button(button_frame, text='Abort', command=self.abort)
        abort_button.pack(side='left', padx=5)

        retry_button = tk.Button(button_frame, text='Retry', command=self.retry)
        retry_button.pack(side='left', padx=5)

        skip_button = tk.Button(button_frame, text='Skip this Record', command=self.skip)
        skip_button.pack(side='left', padx=5)

        self.protocol('WM_DELETE_WINDOW', self.abort)

    def abort(self):
        self.result = 'abort'
        self.destroy()

    def retry(self):
        self.result = 'retry'
        self.destroy()

    def skip(self):
        self.result = 'skip'
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result


class LoadingDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('300x100')
        self.title('Working...')

        self.label = tk.Label(self, text='Starting...')
        self.label.pack(pady=10)

        self.update_idletasks()

    def update(self, message):
        self.label.config(text=message)
        self.update_idletasks()

    def complete(self):
        self.label.config(text='Completed')
        self.update_idletasks()
        self.after(1000, self.destroy)


if __name__ == '__main__':
    app = App()
    app.mainloop()