import tkinter as tk
from tkinter import ttk, messagebox

class SNMPGUI:
    def __init__(self, root, device):
        self.root = root
        self.device = device
        self.root.title(f"{device.device_name} - {device.ip}")

        if device.device_name == "Printer":
            self.setup_printer_ui()
        elif device.device_name == "Switch":
            self.setup_switch_ui()

    def setup_printer_ui(self):
        tree = ttk.Treeview(self.root)
        tree.pack(fill='both', expand=True)

        for oid, info in self.device.snmp_tree.items():
            parent = tree.insert("", "end", text=info["description"])
            self.populate_tree(tree, parent, info["children"])

    def populate_tree(self, tree, parent, children):
        for oid, info in children.items():
            node = tree.insert(parent, "end", text=info["description"])
            if "children" in info:
                self.populate_tree(tree, node, info["children"])

        tree.bind("<Double-1>", self.on_tree_select)

    def on_tree_select(self, event):
        item = event.widget.selection()[0]
        oid = event.widget.item(item, "text")
        result = self.device.get_snmp_data(oid)
        messagebox.showinfo("SNMP Data", f"{oid}: {result}")

    def setup_switch_ui(self):
        table = ttk.Treeview(self.root, columns=("OID", "Description", "Value"), show='headings')
        table.heading("OID", text="OID")
        table.heading("Description", text="Description")
        table.heading("Value", text="Value")
        table.pack(fill='both', expand=True)

        for entry in self.device.snmp_table:
            oid = entry["oid"]
            description = entry["description"]
            value = self.device.get_snmp_data(oid)
            table.insert("", "end", values=(oid, description, value))

        reset_button = tk.Button(self.root, text="Reset Switch", command=self.reset_switch)
        reset_button.pack()

        toggle_button = tk.Button(self.root, text="Toggle Port", command=self.toggle_port)
        toggle_button.pack()

    def reset_switch(self):
        self.device.reset_switch()
        messagebox.showinfo("Reset Switch", "Switch has been reset.")

    def toggle_port(self):
        # Port toggling logic here
        pass
