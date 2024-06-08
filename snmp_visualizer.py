import networkx as nx
import matplotlib.pyplot as plt
from tkinter import messagebox


class SNMPVisualizer:
    def __init__(self, snmp_device):
        self.snmp_device = snmp_device
        self.G = nx.DiGraph()
        self.pos = None
        self.labels = None
        self.shapes = {}

    def vertical_layout(self, G, root=None, width=1., height=1.):
        pos = nx.spring_layout(G)
        levels = self._get_levels(G, root)
        vgap = height / len(levels)
        hgap = width / (max(len(level) for level in levels.values()) + 1)
        for level, nodes in levels.items():
            for i, node in enumerate(nodes):
                pos[node] = ((i + 1) * hgap, (len(levels) - level) * vgap)
        return pos

    def _get_levels(self, G, root):
        if root is None:
            root = list(G.nodes)[0]
        levels = {}
        queue = [(root, 0)]
        while queue:
            node, level = queue.pop(0)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
            for neighbor in G.neighbors(node):
                queue.append((neighbor, level + 1))
        return levels

    def visualize_tree(self):
        def add_nodes_edges(G, tree, parent=None):
            for oid, info in tree.items():
                shape = 's' if 'children' in info else 'o'
                G.add_node(oid, label=info["description"], shape=shape)
                self.shapes[oid] = shape
                if parent:
                    G.add_edge(parent, oid)
                if "children" in info:
                    add_nodes_edges(G, info["children"], oid)

        add_nodes_edges(self.G, self.snmp_device.snmp_tree)

        self.pos = self.vertical_layout(self.G, root="1.3.6.1.2.1.1")
        self.labels = nx.get_node_attributes(self.G, 'label')
        nx.draw(self.G, self.pos, labels=self.labels, with_labels=True, node_size=3000, node_color="skyblue",
                font_size=10, font_color="black", font_weight="bold", arrows=False)

        node_shapes = set((self.shapes[node] for node in self.G))
        for shape in node_shapes:
            nx.draw_networkx_nodes(self.G, self.pos,
                                   nodelist=[sNode[0] for sNode in self.shapes.items() if sNode[1] == shape],
                                   node_shape=shape, node_color="skyblue", node_size=3000)

        plt.gcf().canvas.mpl_connect('button_press_event', self.on_click)
        plt.show()

    def on_click(self, event):
        if event.inaxes is not None:
            for node, (x, y) in self.pos.items():
                if (event.xdata - x) ** 2 + (event.ydata - y) ** 2 < 0.01 and self.shapes[node] == 'o':
                    description = self.labels[node]
                    result = self.snmp_device.get_snmp_data(node)
                    result_text = f" {result}"
                    print(result_text)
                    messagebox.showinfo("SNMP Data", result_text)
                    break
