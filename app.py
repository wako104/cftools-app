import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

import handlers as func
import scripts as cf

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('800x600')

        #--------------- SIDEBAR ---------------
        self.sidebar = ttk.Frame(self)
        self.sidebar.pack(side='left', fill='y')
        # dashboard
        self.dashboard_btn = ttk.Button(self.sidebar, text='Dashboard', command=lambda: self.switch_frame(Dashboard, 'Dashboard'), state='disabled')
        self.dashboard_btn.pack(padx=10, pady=10)
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
        self.rmv_zone_btn = ttk.Button(self.sidebar, text='Remove Zone', command=lambda: self.switch_frame(RemoveZonePage, 'Remove Zone'),state='disabled')
        self.rmv_zone_btn.pack(padx=10, pady=5)
        # separator
        self.separator = ttk.Separator(self.sidebar)
        self.separator.pack(fill='x', padx=10, pady=5)
        # records
        self.records_label = ttk.Label(self.sidebar, text='DNS Records')
        self.records_label.pack(padx=10, pady=5)
        self.s_and_r_btn = ttk.Button(self.sidebar, text='Search and Replace', state='disabled')
        self.s_and_r_btn.pack(padx=10, pady=5)

        #------------- RIGHT SIDE -------------
        self.right_side = ttk.Frame(self)

        self.right_side.pack(side='left', fill='both', expand=True)

        #--------------- HEADER ----------------
        self.header = ttk.Frame(self.right_side)
        self.header_label = ttk.Label(self.header, anchor='center', font=('helvetica', '20'))

        self.header.pack(fill='both')
        self.header_label.pack(fill='both', padx=10, pady=10)

        ttk.Separator(self.header, orient='horizontal').pack(side='bottom', fill='x')

        #---------------- MAIN -----------------
        self.main_frame = ttk.Frame(self.right_side)

        self.main_frame.pack(expand=True)

        self.current_frame = None
        self.switch_frame(ConnectionPage, 'Connect to Cloudflare Account')

    def switch_frame(self, frame_class, header_text):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        new_frame = frame_class(self.main_frame, self)
        new_frame.pack(fill='both', expand=True)
        self.current_frame = new_frame

        self.header_label.config(text=header_text)
    
    def enable_sidebar(self):
        self.dashboard_btn.config(state='normal')
        self.quick_add_zone_btn.config(state='normal')
        self.add_zone_btn.config(state='normal')
        self.rmv_zone_btn.config(state='normal')
        self.s_and_r_btn.config(state='normal')



class ConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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
            self.controller.switch_frame(AccountSelect, 'Select Account')
        else:
            messagebox.showerror('Error', 'Connection Failed')

    def conn_with_env(self):
        try:
            api_key = os.environ['CLOUDFLARE_API_KEY']
            email = os.environ['CLOUDFLARE_EMAIL']
            if cf.validate_key(api_key=api_key, email=email):
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
    def __init__(self, parent):
        super().__init__(parent)

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

        add_zone_btn = tk.Button(self, text='Create Domain with Default DNS Records')
        add_zone_btn.pack()

    # def add_zone(self):
    #     zone_name = self.zone_name_entry.get().strip()
    #     if zone_name:
    #         default_records = self.default_records[self.selected_server.get()]
    #         for record in default_records:
    #             record['name'] = record['name'].replace('@', zone_name)

    #         loading_dialog = LoadingDialog(self)

    #         try:
    #             loading_dialog.update('Creating Zone...')
    #             zone_id, name_servers = func.handle_zone_creation(zone_name, account_id)
    #             loading_dialog.update('Setting SSL...')
    #             func.handle_set_ssl(zone_id)
    #             loading_dialog.update('Adding DNS Records...')
    #             records = func.handle_add_dns_records(zone_id, default_records)
    #             print(records)
    #             loading_dialog.complete()
    #             messagebox.showinfo('Success', 'Zone Created Successfully')
    #         except Exception as e:
    #             messagebox.showerror('Error', str(e))
    #         finally:
    #             ZoneCompleteDialog(self, records, zone_name, name_servers)
    #     else:
    #         messagebox.showwarning('Input Error', 'Please Enter a Valid Domain Name')

class AddZonePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)


class RemoveZonePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)


if __name__ == '__main__':
    app = App()
    app.mainloop()