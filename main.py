import tkinter as tk
from tkinter import ttk, messagebox
from device_scanner import DeviceScanner
from printer_snmp import PrinterSNMP
from switch_snmp import SwitchSNMP
from pysnmp.hlapi import *
import threading

def snmp_walk(ip, community='public'):
    oid = '1.3.6.1.2.1'
    result = []

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    ):
        if errorIndication:
            result.append(str(errorIndication))
            break
        elif errorStatus:
            result.append('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                result.append(f'{varBind[0].prettyPrint()} = {varBind[1].prettyPrint()}')

    return result

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner")
        self.root.geometry("400x600")

        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True)

        self.device_listbox = tk.Listbox(frame)
        self.device_listbox.pack(fill='both', expand=True)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='both', expand=True)

        self.scan_button = ttk.Button(button_frame, text="Scan Devices", command=self.scan_devices)
        self.scan_button.pack(side='left')

        self.view_info_button = ttk.Button(button_frame, text="View Device Info", command=self.view_device_info)
        self.view_info_button.pack(side='left')

    def scan_devices(self):
        scanner = DeviceScanner('192.168.0')
        devices = scanner.scan()
        self.device_listbox.delete(0, tk.END)
        for device in devices:
            self.device_listbox.insert(tk.END, f"{device['ip']} - {device['sys_descr']}")

    def view_device_info(self):
        selected_index = self.device_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a device")
            return
        selected_device = self.device_listbox.get(selected_index)
        ip = selected_device.split(' - ')[0]

        self.view_info_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.detect_and_show_device_info, args=(ip,))
        thread.start()

    def detect_and_show_device_info(self, ip):
        device_type = self.detect_device_type(ip)
        self.root.after(0, self.show_device_info, ip, device_type)

    def detect_device_type(self, ip):
        snmpwalk_output = snmp_walk(ip)
        for line in snmpwalk_output:
            if "TL-SG2428P" in line or "switch" in line.lower():
                return "Switch"
            if "Printer" in line or "HP" in line:
                return "Printer"

        return "Unknown"

    def show_device_info(self, ip, device_type):
        self.view_info_button.config(state=tk.NORMAL)
        if device_type == "Printer":
            device = PrinterSNMP(ip)
        elif device_type == "Switch":
            device = SwitchSNMP(ip)
        else:
            messagebox.showerror("Error", "Unknown device type")
            return

        new_window = tk.Toplevel(self.root)
        new_window.title(f"{device_type} - {ip}")

        if device_type == "Switch":
            self.build_table(new_window, device)
        else:
            tree = ttk.Treeview(new_window)
            tree.pack(fill='both', expand=True)
            self.build_tree(tree, device.snmp_tree)
            tree.bind("<Double-1>", lambda event: self.on_tree_select(event, device))

    def build_tree(self, tree, data, parent=''):
        for key, value in data.items():
            oid = key
            text = value.get("description", "Unknown")
            explanation = value.get("explanation", "")
            node = tree.insert(parent, 'end', text=oid, values=(text, explanation))
            if "children" in value:
                self.build_tree(tree, value["children"], node)

    def build_table(self, window, device):
        table = ttk.Treeview(window, columns=('OID', 'Description', 'Value'), show='headings')
        table.heading('OID', text='OID')
        table.heading('Description', text='Description')
        table.heading('Value', text='Value')
        table.pack(fill='both', expand=True)

        for item in device.snmp_table:
            oid = item["oid"]
            print(item["oid"], item["description"])
            description = item["description"]
            value = device.get_snmp_data(oid)
            table.insert('', 'end', values=(oid, description, value))

        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', expand=True)

        reset_btn = ttk.Button(btn_frame, text="Reset Switch", command=device.reset_switch)
        reset_btn.pack(side='left', padx=5, pady=5)

        toggle_btn = ttk.Button(btn_frame, text="Toggle Port", command=lambda: device.toggle_port(1, "up"))
        toggle_btn.pack(side='left', padx=5, pady=5)

    def on_tree_select(self, event, device):
        item = event.widget.selection()[0]
        oid = event.widget.item(item, "text")
        value = device.get_snmp_data(oid)
        messagebox.showinfo("SNMP Data", f"{oid} = {value}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
