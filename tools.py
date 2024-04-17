from langchain.agents import tool
import json
market_drivers = []

@tool
def set_market_drivers(market_drivers_data):
    """
    save the market drivers data to the global variable market_drivers to be used later
    Args:
        market_drivers_data (dict): market drivers data
    """
    global market_drivers
    market_drivers = market_drivers_data

tools = [set_market_drivers]
