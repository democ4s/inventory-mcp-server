from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP

# Initiaize FastMCP Server
mcp = FastMCP(
  host='0.0.0.0',
  port=8000,
  name='inventory-mcp',
  description='Manages a simple product inventory'
)

# --- Memory: Inventory data ---
inventory: List[Dict[str, Any]] = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "stock": 12, "price": 999.99},
    {"id": 2, "name": "Keyboard", "category": "Accessories", "stock": 35, "price": 49.99},
    {"id": 3, "name": "Mouse", "category": "Accessories", "stock": 27, "price": 29.99},
    {"id": 4, "name": "Monitor", "category": "Electronics", "stock": 10, "price": 199.99},
    {"id": 5, "name": "Chair", "category": "Furniture", "stock": 8, "price": 89.99}
]

# Initialize tools
@mcp.tool(
    name='get_latest_id',
    description='Get the latest item ID in the inventory'
)
def get_latest_id() -> int:
    return max(item["id"] for item in inventory)

@mcp.tool(
    name='add_item',
    description='Add a new item to the inventory. Need to use get_latest_id to get the latest item ID and add 1 to it for the new item ID.'
)
def add_item(item: Dict[str, Any]):
    inventory.append(item)

@mcp.tool(
    name='update_stock',
    description='Update the stock level for an item'
)
def update_stock(item_id: int, new_stock: int):
    for item in inventory:
        if item["id"] == item_id:
            item["stock"] = new_stock
            return True
    return False

@mcp.tool(
    name='search_items',
    description='Search for items in the inventory'
)
def search_items(keyword: str) -> List[Dict[str, Any]]:
    return [item for item in inventory if keyword.lower() in item["name"].lower()]

@mcp.tool(
    name='get_all_items',
    description='Get all items in the inventory'
)
def get_all_items() -> List[Dict[str, Any]]:
    return inventory

# Define a reusable prompt for inventory management
@mcp.prompt(
    name='manage_inventory',
    description='Generate a summary of the inventory, suggest actions, or add items with automatic category assignment'
)
def manage_inventory(query: str) -> str:
    """A prompt template for inventory management tasks"""
    return f"""
You are an inventory management assistant. Use the provided tools (`get_all_items`, `search_items`, `add_item`, `update_stock`, `get_latest_id`) to process the following user query:

"{query}"

Instructions:
1. **Listing or Displaying Items**: If the query asks to "list items", "display items", or similar, use `get_all_items` or `search_items` (if a keyword is provided) to retrieve the items. Present the results in a tabular format with columns: ID, Name, Category, Stock, Price, and an additional "Stock" column. In this "Stock" column, show ✅ if stock >= 10, otherwise show ❌.
   Example table format:
   ```
   | ID | Name       | Category    | Stock | Price   | Stock |
   |----|------------|-------------|-------|---------|-------|
   | 1  | Laptop     | Electronics | 12    | 999.99  | ✅    |
   | 2  | Keyboard   | Accessories | 35    | 49.99   | ✅    |
   | 3  | Mouse      | Accessories | 27    | 29.99   | ✅    |
   | 4  | Monitor    | Electronics | 10    | 199.99  | ✅    |
   | 5  | Chair      | Furniture   | 8     | 89.99   | ❌    |
   ```
2. **Summarizing Inventory**: If the query asks for a summary, provide a concise summary of the inventory, including total items, categories, and low stock alerts (stock < 10).
3. **Searching Items**: If the query involves searching, use `search_items` with the keyword and present the results in the same tabular format as above if the intent is to list or display them.
4. **Adding Items**: If the query involves adding an item (e.g., "Add item: Headphones, 15, 79.99"), ensure the query provides:
   - Item name (string)
   - Quantity (positive integer)
   - Price (positive float)
   If any are missing or invalid, respond with: "Error: Please provide item name, quantity (positive integer), and price (positive float)."
   Automatically assign a category based on the item name:
   - "laptop", "monitor", "phone", "tablet", "headphones" → "Electronics"
   - "keyboard", "mouse", "cable" → "Accessories"
   - "chair", "desk", "table" → "Furniture"
   - Otherwise → "Miscellaneous"
   Use `get_latest_id` to generate a new ID and call `add_item`.
5. **Updating Stock**: If the query involves updating stock, use `update_stock` with the item ID and new stock level.
6. **Low Stock Alerts**: For summaries or searches, identify items with stock < 10 and suggest restocking.

Provide a clear, concise response with actionable suggestions if applicable.
"""
  
if __name__ == '__main__':
  # Initialize and run the MCP server
  mcp.run(transport='sse')
