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
    """
    GUI Application for managing Cloudflare zones and DNS records.

    This class initializes the app, which includes a sidebar, header and main content area.
    """
    def __init__(self):
        super().__init__()
        self.title('OSAM Websites Cloudflare Tool')
        self.geometry('900x600')

        self.logo_image = tk.PhotoImage(file=logo_path)
        self.logo = self.logo_image.subsample(5,5)

        self.icon = tk.PhotoImage(file=icon_path)
        self.wm_iconphoto(True, self.icon)

        #--------------- SIDEBAR ---------------
        self.sidebar = tk.Frame(self)
        self.sidebar.pack(side='left', fill='y')
        # dashboard
        self.dashboard_btn = ttk.Button(
            self.sidebar, image=self.logo,
            command=lambda: self.switch_frame(Dashboard, 'Dashboard'),
            state='disabled')
        self.dashboard_btn.pack(padx=10, pady=13)
        # separator
        self.separator = ttk.Separator(self.sidebar)
        self.separator.pack(fill='x', padx=10, pady=5)
        # zones
        self.zones_label = ttk.Label(self.sidebar, text='Zones')
        self.zones_label.pack(padx=10, pady=5)
        self.quick_add_zone_btn = ttk.Button(
            self.sidebar, text='Quick Add Zone',
            command=lambda: self.switch_frame(QuickAddZonePage, 'Quick Add Zone'),
            state='disabled')
        self.quick_add_zone_btn.pack(padx=10, pady=5)
        self.add_zone_btn = ttk.Button(
            self.sidebar, text='Add Zone',
            command=lambda: self.switch_frame(AddZonePage, 'Add Zone'),
            state='disabled')
        self.add_zone_btn.pack(padx=10, pady=5)
        self.rmv_zone_btn = ttk.Button(
            self.sidebar,
            text='Remove Zone',
            command=lambda: self.switch_frame(RemoveZonePage, 'Remove Zone'),
            state='disabled')
        self.rmv_zone_btn.pack(padx=10, pady=5)
        # separator
        self.separator = ttk.Separator(self.sidebar)
        self.separator.pack(fill='x', padx=10, pady=5)
        # records
        self.records_label = ttk.Label(self.sidebar, text='DNS Records')
        self.records_label.pack(padx=10, pady=5)
        self.s_and_r_btn = ttk.Button(
            self.sidebar, text='Search and Replace',
            command=lambda: self.switch_frame(SearchAndReplacePage, 'DNS Search and Replace'),
            state='disabled')
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
        self.main_placeholder = tk.Frame(
            self.right_side,
            highlightthickness=1,
            highlightbackground='black',
            bd=0)
        self.main_frame = tk.Frame(self.main_placeholder)

        self.main_placeholder.pack(expand=True, fill='both', padx=(0,5), pady=(0,5))
        self.main_frame.pack(expand=True, pady=(0,50))

        self.current_frame = None
        self.switch_frame(ConnectionPage, 'Connect to Cloudflare Account')

    def switch_frame(self, frame_class, header_text, **kwargs):
        """Switches frame of the main area."""
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        new_frame = frame_class(self.main_frame, self, **kwargs)
        new_frame.pack(fill='both', expand=True)
        self.current_frame = new_frame

        self.header_label.config(text=header_text)

    def enable_sidebar(self):
        """Enables sidebar options after user establishes connection."""
        self.dashboard_btn.config(state='normal')
        self.quick_add_zone_btn.config(state='normal')
        # self.add_zone_btn.config(state='normal')
        self.rmv_zone_btn.config(state='normal')
        self.s_and_r_btn.config(state='normal')


class ConnectionPage(tk.Frame):
    """
    Allows the user to establish a connection to a Cloudflare account, either using environment
    variables or entering their email and api key. A connection must be established before the apps
    functionality is used.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        env_conn_btn = ttk.Button(
            self,
            text='Connect Using Environment Variables',
            command=self.conn_with_env)
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
        """Connect to Cloudflare account using input fields."""
        api_key = self.api_key.get()
        email = self.email.get()

        if func.handle_connection(api_key=api_key, email=email):
            messagebox.showinfo('Success', 'Connection Established')
            self.controller.switch_frame(AccountSelect, 'Select Account')
        else:
            messagebox.showerror('Error', 'Connection Failed')

    def conn_with_env(self):
        """Connect to Cloudflare account using environment variables"""
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
    """Select which Cloudflare account to make changes to."""
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
        """Sets the selected account and enables the sidebar."""
        global account_id
        account_id = next(
            (id for id, name in self.accounts if name == self.account_var.get()),
            None)
        if account_id:
            self.controller.enable_sidebar()
            self.controller.switch_frame(Dashboard, 'Dashboard')
        else:
            messagebox.showerror('Selection Error', 'No Account Selected')


class Dashboard(tk.Frame):
    """Tkinter Frame subclass representing the dashboard page."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        welcome_label = ttk.Label(self, text='Welcome', foreground='grey')
        welcome_label.pack()
        account_id_label = ttk.Label(self, text='Account ID: ' + account_id, foreground='grey')
        account_id_label.pack()


class QuickAddZonePage(tk.Frame):
    """Quick add zone page. Add a zone with one of the options for default records."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.records = []

        with open(default_records_path, 'r') as file:
            self.default_records = json.load(file)

        ttk.Label(self, text='Choose Server:').pack(pady=10)
        self.default_server = list(self.default_records.keys())[0] if self.default_records else ''
        self.selected_server = tk.StringVar(value=self.default_server)
        for option in self.default_records:
            ttk.Radiobutton(self, text=option, variable=self.selected_server, value=option).pack()

        # ttk.Label(self, text='Choose workspace:').pack(pady=10)
        # self.workspace = tk.StringVar(value='None')
        # self.workspace_options = ['None', 'Google', 'Microsoft 365']
        # self.workspace_dropdown = ttk.Combobox(
        #     self,
        #     textvariable=self.workspace,
        #     values=self.workspace_options,
        #     state='readonly')
        # self.workspace_dropdown.pack()

        ttk.Label(self, text='Enter Domain Name: ').pack(pady=(20,10))

        self.zone_name_entry = ttk.Entry(self, font=('Times', 12), width=30)
        self.zone_name_entry.pack(pady=10)

        self.add_zone_btn = ttk.Button(
            self,
            text='Create Domain with Default DNS Records',
            command=self.add_zone)
        self.add_zone_btn.pack(pady=10)

    def add_zone(self):
        """Add a zone to Cloudflare with default records."""
        self.zone_name = self.zone_name_entry.get().strip()
        if self.zone_name:
            self.selected_records = self.default_records[self.selected_server.get()]
            for record in self.selected_records:
                record['name'] = record['name'].replace('@', self.zone_name)

            loading_dialog = LoadingDialog(self)
            try:
                loading_dialog.update('Creating Zone...')
                self.zone_id, self.name_servers = func.handle_zone_creation(
                    self.zone_name,
                    account_id)
                loading_dialog.update('Setting SSL...')
                func.handle_set_ssl(self.zone_id)
                loading_dialog.update('Enabling Always Use HTTPS...')
                func.handle_always_use_https(self.zone_id)
                loading_dialog.update('Adding DNS Records...')
                self.records = func.handle_add_dns_records(self.zone_id, self.selected_records)
                loading_dialog.complete()
                self.controller.switch_frame(
                    ZoneCompletePage,
                    f'Zone Created ({self.zone_name})',
                    records=self.records,
                    zone_name=self.zone_name,
                    zone_id=self.zone_id,
                    name_servers=self.name_servers)
            except Exception as e:
                messagebox.showerror('Error', str(e))
                loading_dialog.destroy()
        else:
            messagebox.showwarning('Input Error', 'Please Enter a Valid Domain Name')


class AddZonePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller


class ZoneCompletePage(tk.Frame):
    """This page shows a summary of a Zone and it's DNS records after it has been added."""
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
            ns_copy_btn = ttk.Button(
                ns_frame, text='📋',
                width=5,
                command=lambda ns=name_server: self.copy_to_clipboard(ns))
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
    """Remove a zone from Cloudflare account."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text='Enter Domain Name: ').pack(pady=(20,10))

        self.zone_name_entry = ttk.Entry(self, font=('Times', 12), width=30)
        self.zone_name_entry.pack(pady=10)

        ttk.Button(self, text='Remove Zone from Cloudflare', command=self.remove_zone).pack(pady=10)

    def remove_zone(self):
        self.zone_name = self.zone_name_entry.get().strip()
        if self.zone_name:
            try:
                func.handle_remove_zone(self.zone_name)
                ttk.Label(self, text='Zone Successfully Removed').pack(pady=(20,10))
            except Exception as e:
                messagebox.showerror('Error', str(e))


class SearchAndReplacePage(tk.Frame):
    """Search for DNS record and replace it with another"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # tabs ->
            # search and replace dns in one domain
            # search and replace dns across all domains

        self.record = RecordEntryFrame(self)
        self.record.pack(pady=10, fill='x', expand=True)

        ttk.Button(self, text='+', command=self.get_record_data).pack()

    def get_record_data(self):
        data = self.record.get_json()
        print(json.dumps(data, indent=2))


class RecordEntryFrame(tk.Frame):
    """
    Frame for creating a record. Allows a user to choose the record type, then enter the
    required data
    """
    def __init__(self, parent, record_type='A'):
        super().__init__(parent)
        self.input_fields = {}
        self.record_type_var = tk.StringVar(value=record_type)
        self.record_types = ['A', 'CNAME', 'MX', 'TXT']

        ttk.Label(self, text='Select Record Type:').pack(pady=5)
        self.record_type_menu = ttk.Combobox(
            self,
            textvariable=self.record_type_var,
            values=self.record_types,
            state='readonly')
        self.record_type_menu.pack(pady=5)
        self.record_type_menu.bind('<<ComboboxSelected>>', self.display_input_fields)

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=30, fill='x', expand=True)
        self.display_input_fields()

    def display_input_fields(self, event=None):
        # destroy previous input fields
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        record_type = self.record_type_var.get()

        fields = {
            'A': ['Name', 'IP Address', 'Proxy Status'],
            'CNAME': ['Name', 'Target', 'Proxy Status'],
            'MX': ['Name', 'Mail Server', 'Priority'],
            'TXT': ['Name', 'Content']
        }

        for i, field in enumerate(fields.get(record_type, [])):
            if i > 0:
                ttk.Separator(self.input_frame, orient='vertical').pack(
                    side='left',
                    fill='y',
                    padx=8)
            if field == 'Proxy Status':
                self.create_proxy_switch()
            else:
                label = ttk.Label(self.input_frame, text=field + ':')
                label.pack(side='left')
                entry = ttk.Entry(self.input_frame)
                entry.pack(side='left', fill='x')
                self.input_fields[field] = entry

    def create_proxy_switch(self):

        proxy_label = ttk.Label(self.input_frame, text='Proxy Status:')
        proxy_label.pack(side='left')

        self.proxy_var = tk.BooleanVar(value=True)
        proxy_switch = ttk.Checkbutton(
            self.input_frame,
            variable=self.proxy_var,
            command=self.update_proxy_text)
        proxy_switch.pack(side='left')

        self.proxy_status_text = tk.StringVar(value='On')
        proxy_status_label = ttk.Label(self.input_frame, textvariable=self.proxy_status_text)
        proxy_status_label.pack(side='left')

    def update_proxy_text(self):
        if self.proxy_var.get():
            self.proxy_status_text.set('On')
        else:
            self.proxy_status_text.set('Off')

    def get_json(self):
        record_type = self.record_type_var.get()
        data = {'type': record_type}

        field_map = {
            'Name': 'name',
            'IP Address': 'content',
            'Target': 'content',
            'Mail Server': 'content',
            'Content': 'content',
            'Proxy Status': 'proxied',
            'Priority': 'priority'
        }

        for field, entry in self.input_fields.items():
            if field == 'Proxy Status':
                data[field_map[field]] = entry.variable.get()
            else:
                data[field_map[field]] = entry.get()
        return data


class LoadingDialog(tk.Toplevel):
    """
    Dialog for when a script is running, giving the user a message of what's currently
    happening
    """
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
