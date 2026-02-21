import pandas as pd
import random
import numpy as np

def generate_test_data():
    assets = ["Boiler-1", "Boiler-2", "Turbine-A", "Cooling-Tower"]
    
    # Rows 1-5: Normal realistic float values
    data = []
    for _ in range(5):
        data.append({
            "asset": random.choice(assets),
            "coal": round(random.uniform(100.0, 500.0), 2),
            "power_1": round(random.uniform(50.0, 250.0), 2),
            "power_2": round(random.uniform(50.0, 250.0), 2), 
            "temp": round(random.uniform(300.0, 600.0), 2),
            "water": round(random.uniform(1000.0, 5000.0), 2),
            "co2": round(random.uniform(10.0, 50.0), 2)
        })
        
    # Row 6: Formatted strings (String parsing test)
    data.append({
        "asset": "Turbine-A",
        "coal": "1,234.50",
        "power_1": "150 MT",
        "power_2": "150 MT",
        "temp": "450,0",
        "water": "2,500.99",
        "co2": "35.50"
    })
    
    # Row 7: Missing data test
    data.append({
        "asset": "Boiler-2",
        "coal": "N/A",
        "power_1": "Missing",
        "power_2": "",
        "temp": None,
        "water": "",
        "co2": np.nan
    })
    
    # Row 8: Validation warning test (Impossible negative value)
    data.append({
        "asset": "Boiler-1",
        "coal": 200.5,
        "power_1": -50.5,
        "power_2": -50.5,
        "temp": 400.0,
        "water": 2000.0,
        "co2": 25.0
    })
    
    # Row 9: Duplicate mapping test
    # (By including both 'Power Output' and 'MW Generated' in messy_df, 
    # we inherently test this across all rows, but we ensure we add a 9th row here as requested)
    data.append({
        "asset": "Cooling-Tower",
        "coal": 105.0,
        "power_1": 60.0,
        "power_2": 65.0, 
        "temp": 320.0,
        "water": 4500.0,
        "co2": 15.0
    })
    
    return data

def main():
    raw_data = generate_test_data()
    
    # 1. Clean Data (Uses Canonical Names)
    clean_df = pd.DataFrame({
        "asset_name": [row["asset"] for row in raw_data],
        "coal_consumption": [row["coal"] for row in raw_data],
        "power_generation": [row["power_1"] for row in raw_data],
        "operating_temperature": [row["temp"] for row in raw_data],
        "water_flow_rate": [row["water"] for row in raw_data],
        "emissions_co2": [row["co2"] for row in raw_data],
    })
    clean_df.to_excel("clean_data.xlsx", index=False)
    
    # 2. Messy Data (Uses Chaotic Variation Names & Duplicate Mapping columns)
    messy_df = pd.DataFrame({
        "Equipment ID": [row["asset"] for row in raw_data],
        "Total Coal Used (Metric Tons)": [row["coal"] for row in raw_data],
        "Gen. Output [MW]": [row["power_1"] for row in raw_data],
        "Temp (Celsius)": [row["temp"] for row in raw_data],
        "Water In (LPH)": [row["water"] for row in raw_data],
        "Carbon Output": [row["co2"] for row in raw_data],
        "Power Output": [row["power_1"] for row in raw_data],
        "MW Generated": [row["power_2"] for row in raw_data]
    })
    messy_df.to_excel("messy_data.xlsx", index=False)
    
    # 3. Multi-Asset Data (Tests multi-sheet parsing where sheet names map to assets)
    with pd.ExcelWriter("multi_asset.xlsx") as writer:
        for asset in ["Boiler-1", "Boiler-2", "Turbine-A", "Cooling-Tower"]:
            asset_data = [row for row in raw_data if row["asset"] == asset]
            if not asset_data:
                # Add dummy row if empty so the sheet isn't completely blank
                asset_data = [raw_data[0]]

            df = pd.DataFrame({
                "Total Coal Used (Metric Tons)": [row["coal"] for row in asset_data],
                "Gen. Output [MW]": [row["power_1"] for row in asset_data],
                "Temp (Celsius)": [row["temp"] for row in asset_data],
                "Water In (LPH)": [row["water"] for row in asset_data],
                "Carbon Output": [row["co2"] for row in asset_data],
                "Power Output": [row["power_1"] for row in asset_data],
                "MW Generated": [row["power_2"] for row in asset_data]
            })
            
            # Using Sheet Name as Asset Identifier rather than a column
            df.to_excel(writer, sheet_name=asset, index=False)
            
    print("Successfully generated clean_data.xlsx, messy_data.xlsx, and multi_asset.xlsx!")

if __name__ == "__main__":
    main()