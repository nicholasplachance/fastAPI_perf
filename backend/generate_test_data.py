import json
import random
from uuid import uuid4
from datetime import date, timedelta

# ---------------------------
# Characters and Lore
# ---------------------------
character_data = [
    ("Mario Mario", "Mushroom Kingdom", "Toad Town"),
    ("Luigi Mario", "Mushroom Kingdom", "Toad Town"),
    ("Samus Aran", "Metroid Galaxy", "Zebes"),
    ("Master Chief", "Halo Universe", "Reach"),
    ("Solid Snake", "Metal Gear", "Shadow Moses Island"),
    ("Lara Croft", "Tomb Raider", "Surrey"),
    ("Ezio Auditore", "Assassin's Creed", "Florence"),
    ("Link", "Legend of Zelda", "Hyrule"),
    ("Zelda", "Legend of Zelda", "Castle Town"),
    ("Kirby", "Dream Land", "Popstar"),
    ("Rick Sanchez", "Rick and Morty", "Dimension C-137"),
    ("Morty Smith", "Rick and Morty", "Dimension C-137"),
    ("Finn the Human", "Adventure Time", "Land of Ooo"),
    ("Jake the Dog", "Adventure Time", "Land of Ooo"),
    ("Steven Universe", "Steven Universe", "Beach City"),
    ("Peter Quill", "Marvel", "Spartax"),
    ("Gamora", "Marvel", "Zen-Whoberi"),
    ("Groot", "Marvel", "Planet X"),
    ("Rocket Raccoon", "Marvel", "Halfworld"),
    ("Thanos", "Marvel", "Titan"),
    ("Saitama", "One Punch Man", "Z-City"),
    ("Goku", "Dragon Ball", "Mount Paozu"),
    ("Vegeta", "Dragon Ball", "Planet Vegeta"),
    ("Ichigo Kurosaki", "Bleach", "Karakura Town"),
    ("Naruto Uzumaki", "Naruto", "Hidden Leaf Village"),
    ("Ash Ketchum", "Pokemon", "Pallet Town"),
    ("Misty", "Pokemon", "Cerulean City"),
    ("Bugs Bunny", "Looney Tunes", "Toon Town"),
    ("Shrek", "DreamWorks", "Far Far Away"),
    ("SpongeBob SquarePants", "Nickelodeon", "Bikini Bottom")
]

menu_items = [
    "Infinity Sausage Slice", "Time-Turner Truffle Pie", "Triforce Supreme",
    "Planetary Pepperoni", "Hero's Feast Flatbread", "Morph Ball Margherita",
    "Moon Prism Mushroom", "Ultra Instinct Udon Pizza", "Saiyan BBQ Bomb", "Cosmic Cheddar Crush"
]

# ---------------------------
# Utilities
# ---------------------------
def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

today = date.today()
one_year_ago = today - timedelta(days=365)

customers = []
orders = []

for name, multiverse, town in character_data:
    customer_id = str(uuid4())
    first_order = random_date(one_year_ago, today - timedelta(days=30))
    last_order = random_date(first_order, today)

    address = f"{random.randint(1, 999)} {town} Road, {town}, {multiverse}"
    email = f"{name.lower().replace(' ', '')}@{multiverse.lower().replace(' ', '')}.com"

    customer = {
        "id": customer_id,
        "name": name,
        "address": address,
        "email": email,
        "most_ordered_item": "",
        "first_order_date": str(first_order),
        "last_order_date": str(last_order),
        "multiverse": multiverse,
        "town": town
    }

    # 1–5 orders
    order_count = random.randint(1, 5)
    item_counts = {}

    for _ in range(order_count):
        item = random.choice(menu_items)
        quantity = random.randint(1, 3)
        order_date = random_date(first_order, today)

        orders.append({
            "id": str(uuid4()),
            "customer_id": customer_id,
            "item": item,
            "quantity": quantity,
            "order_date": str(order_date)
        })

        item_counts[item] = item_counts.get(item, 0) + quantity

    # Assign most ordered item
    if item_counts:
        customer["most_ordered_item"] = max(item_counts.items(), key=lambda x: x[1])[0]

    customers.append(customer)

# ---------------------------
# Save to JSON Files
# ---------------------------
with open("customers.json", "w") as f:
    json.dump(customers, f, indent=2)

with open("orders.json", "w") as f:
    json.dump(orders, f, indent=2)

print(f"✅ Generated {len(customers)} customers and {len(orders)} orders")
