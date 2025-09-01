import random
import json

class DungeonGenerator:
    def __init__(self, num_lanes=4, depth=6, seed=None):
        self.num_lanes = num_lanes
        self.depth = depth
        if seed is not None:
            random.seed(seed)

    def generate(self):
        dungeon = {"nodes": {}, "connections": []}
        node_id = 0

        # Start node
        dungeon["nodes"][node_id] = {"type": "start", "lane": None, "depth": 0}
        start_node = node_id
        node_id += 1

        # Generate layers
        layers = []
        for d in range(1, self.depth + 1):
            layer_nodes = []
            for l in range(self.num_lanes):
                node_type = "hard" if random.random() < 0.30 else "normal"
                dungeon["nodes"][node_id] = {"type": node_type, "lane": l, "depth": d}
                layer_nodes.append(node_id)
                node_id += 1
            layers.append(layer_nodes)

        # Shop node
        dungeon["nodes"][node_id] = {"type": "shop", "lane": None, "depth": self.depth + 1}
        shop_node = node_id
        node_id += 1

        # Boss node
        dungeon["nodes"][node_id] = {"type": "boss", "lane": None, "depth": self.depth + 2}
        boss_node = node_id

        # Connect start to first layer
        for n in layers[0]:
            dungeon["connections"].append((start_node, n))

        # Connect layers
        for i in range(len(layers) - 1):
            current = layers[i]
            next_layer = layers[i + 1]
            for idx, node in enumerate(current):
                # always connect to same-lane node
                targets = [next_layer[idx]]
                # possible adjacent connections
                if idx > 0:
                    targets.append(next_layer[idx - 1])
                if idx < len(next_layer) - 1:
                    targets.append(next_layer[idx + 1])
                # connect to at least one target (same lane guaranteed)
                dungeon["connections"].append((node, next_layer[idx]))
                for t in targets:
                    if t != next_layer[idx] and random.random() < 0.5:
                        dungeon["connections"].append((node, t))

        # Connect last layer to shop
        for n in layers[-1]:
            dungeon["connections"].append((n, shop_node))

        # Connect shop to boss
        dungeon["connections"].append((shop_node, boss_node))

        return dungeon

    def merge_char(self, existing, new):
        if existing == " ":
            return new
        if existing == new:
            return existing
        # Merge rules for junctions
        merge_map = {
            frozenset(["─", "│"]): "┼",
            frozenset(["─", "╱"]): "┼",
            frozenset(["─", "╲"]): "┼",
            frozenset(["│", "╱"]): "┼",
            frozenset(["│", "╲"]): "┼",
            frozenset(["╱", "╲"]): "┼",
        }
        return merge_map.get(frozenset([existing, new]), "┼")

    def visualize_grid_rotated(self, dungeon):
        width = self.depth + 3
        height = self.num_lanes
        cell_w = 18
        cell_h = 4

        canvas_w = width * cell_w
        canvas_h = height * cell_h
        grid = [[" " for _ in range(canvas_w)] for _ in range(canvas_h)]

        positions = {}
        bboxes = {}  # store bounding boxes of node labels

        # Place nodes
        for node_id, data in dungeon["nodes"].items():
            lane = data["lane"]
            depth = data["depth"]
            symbol = {
                "start": "START",
                "normal": "NORMAL",
                "hard": "HARD",
                "event": "EVENT",
                "shop": "SHOP",
                "boss": "BOSS"
            }.get(data["type"], "?")

            row = lane if lane is not None else height // 2
            col = depth
            x = col * cell_w + cell_w // 2
            y = row * cell_h + cell_h // 2

            label = f"[{symbol}{node_id}]"
            start_x = x - len(label) // 2
            for i, ch in enumerate(label):
                grid[y][start_x + i] = ch

            positions[node_id] = (x, y)
            bboxes[node_id] = (start_x, y, start_x + len(label) - 1, y)  # (x1, y1, x2, y2)

        # Draw connections
        for a, b in dungeon["connections"]:
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
            dy = 1 if y2 > y1 else -1 if y2 < y1 else 0
            x, y = x1, y1

            while (x, y) != (x2, y2):
                if (x != x2):
                    x += dx
                if (y != y2):
                    y += dy

                # skip drawing if inside ANY node’s bounding box
                inside_node = False
                for (x1b, y1b, x2b, y2b) in bboxes.values():
                    if x1b <= x <= x2b and y1b <= y <= y2b:
                        inside_node = True
                        break
                if inside_node:
                    continue

                if (x, y) != (x2, y2):
                    if dx != 0 and dy == 0:
                        new_char = "─"
                    elif dy != 0 and dx == 0:
                        new_char = "│"
                    else:
                        new_char = "╲" if (dx == dy) else "╱"
                    grid[y][x] = self.merge_char(grid[y][x], new_char)

        return "\n".join("".join(row) for row in grid)


if __name__ == "__main__":
    generator = DungeonGenerator(num_lanes=4, depth=4, seed=177288)
    dungeon = generator.generate()

    print(json.dumps(dungeon, indent=4))
    print("\nRotated Grid Visualization with connections:\n")
    print(generator.visualize_grid_rotated(dungeon))