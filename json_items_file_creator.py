# All available types:
# Body -> Body
# Decal -> Decal
# Wheel -> Wheels
# Boost -> Rocket Boost
# Antenna -> Antenna
# Topper -> Topper
# Trail -> Trail
# Goal Explosion -> Goal Explosion
# Paint Finish -> Paint Finish
# Engine Audio -> Engine Audio

# Unwanted:
# Crates
# Banner -> Player Banner

if __name__ == '__main__':
    import json
    items = {}
    with open('Rocket_League_Items.txt', 'r') as f:
        item_lines = []
        for line in f:
            if line.startswith("LongLabel: ") and item_lines:  # We got to a new item, now parse latest one
                item = {}
                slot = ""
                for s in item_lines:
                    split_line = [x.strip() for x in s.split(':', 1)]
                    if not split_line[0]:
                        continue
                    key = split_line[0]
                    value = split_line[1]
                    if key == "Slot":
                        slot = value
                    else:
                        item[key] = value
                if not (slot == "Crates" or slot == "Player Banner"):
                    try:
                        items[slot].append(item)
                    except KeyError:
                        items[slot] = [item]
                item_lines.clear()
            item_lines.append(line)
    with open("src/main/python/rlbot/gui/rocket_league_items.json", "w") as f:
        json.dump(items, f)



