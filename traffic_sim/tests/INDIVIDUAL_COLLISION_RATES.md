# Individual Vehicle Collision Rate System

## Overview
Each vehicle type now has its own unique collision behavior and spacing settings, allowing for more realistic traffic simulation where different vehicles maintain appropriate distances based on their characteristics.

## 🚗 **Vehicle-Specific Settings**

### **Cars**
```python
"CAR": {
    "FOLLOWING_DISTANCE_MULTIPLIER": 1.5,  # Moderate following distance
    "MIN_FOLLOWING_DISTANCE": 50.0,        # 50 pixels minimum
    "SEARCH_DISTANCE": 150.0,              # Look ahead 150 pixels
    "EMERGENCY_STOP_DISTANCE": 30.0,       # Emergency braking at 30 pixels
}
```
- **Behavior**: Balanced spacing, typical car-like following behavior
- **Use Case**: Standard passenger vehicles

### **Trucks**
```python
"TRUCK": {
    "FOLLOWING_DISTANCE_MULTIPLIER": 2.0,  # Larger following distance
    "MIN_FOLLOWING_DISTANCE": 80.0,        # 80 pixels minimum (largest)
    "SEARCH_DISTANCE": 200.0,              # Look ahead 200 pixels (furthest)
    "EMERGENCY_STOP_DISTANCE": 50.0,       # Emergency braking at 50 pixels (longest)
}
```
- **Behavior**: Conservative spacing due to size and braking distance
- **Use Case**: Large commercial vehicles requiring more space

### **Cyclists**
```python
"CYCLIST": {
    "FOLLOWING_DISTANCE_MULTIPLIER": 1.0,  # Closer following
    "MIN_FOLLOWING_DISTANCE": 30.0,        # 30 pixels minimum
    "SEARCH_DISTANCE": 100.0,              # Look ahead 100 pixels
    "EMERGENCY_STOP_DISTANCE": 20.0,       # Emergency braking at 20 pixels
}
```
- **Behavior**: More agile, can follow closer and stop quickly
- **Use Case**: Bicycle traffic with better maneuverability

### **Pedestrians**
```python
"PEDESTRIAN": {
    "FOLLOWING_DISTANCE_MULTIPLIER": 0.8,  # Very close following
    "MIN_FOLLOWING_DISTANCE": 20.0,        # 20 pixels minimum (smallest)
    "SEARCH_DISTANCE": 80.0,               # Look ahead 80 pixels (shortest)
    "EMERGENCY_STOP_DISTANCE": 15.0,       # Emergency braking at 15 pixels (shortest)
}
```
- **Behavior**: Can get very close, immediate stopping capability
- **Use Case**: Foot traffic with maximum flexibility

## 🔧 **How It Works**

### **1. Vehicle Type Detection**
Each vehicle automatically detects its type using:
```python
def get_vehicle_type(self) -> str:
    return type(self).__name__.upper()  # Returns "CAR", "TRUCK", etc.
```

### **2. Settings Retrieval**
Vehicles fetch their specific settings:
```python
def get_collision_settings(self) -> dict:
    config = Config()
    vehicle_type = self.get_vehicle_type()
    return config.VEHICLE_SPACING[vehicle_type]
```

### **3. Dynamic Behavior**
- **Following Distance**: Calculated as `vehicle_size × multiplier`
- **Search Range**: How far ahead the vehicle looks for other vehicles
- **Emergency Stopping**: Distance at which emergency braking activates
- **Minimum Distance**: Absolute minimum spacing regardless of size

### **4. Physics Integration**
The physics system automatically uses vehicle-specific settings:
- `find_vehicle_ahead()` uses each vehicle's search distance
- `calculate_safe_following_speed()` uses each vehicle's following preferences
- Collision detection respects individual emergency stop distances

## 📊 **Expected Behaviors**

### **Traffic Density**
- **Pedestrians**: Highest density, can form tight groups
- **Cyclists**: Medium-high density, pack behavior
- **Cars**: Standard density, normal traffic flow
- **Trucks**: Lowest density, conservative spacing

### **Reaction Times**
- **Pedestrians**: Immediate stops, quick reactions
- **Cyclists**: Quick stops, agile maneuvering
- **Cars**: Standard reaction time and braking
- **Trucks**: Longer reaction time, gradual braking

### **Lane Usage**
Each vehicle type optimally uses road space according to its characteristics:
- More pedestrians can fit in the same space
- Trucks naturally create larger gaps
- Mixed traffic creates realistic density variations

## 🎛️ **Customization**

### **Adjusting Individual Vehicle Behavior**
Edit `configuration.py` to change any vehicle type's settings:

```python
# Make cars more aggressive (closer following)
"CAR": {
    "FOLLOWING_DISTANCE_MULTIPLIER": 1.0,  # Reduced from 1.5
    "MIN_FOLLOWING_DISTANCE": 30.0,        # Reduced from 50.0
    # ... other settings
}

# Make trucks even more conservative
"TRUCK": {
    "FOLLOWING_DISTANCE_MULTIPLIER": 2.5,  # Increased from 2.0
    "MIN_FOLLOWING_DISTANCE": 100.0,       # Increased from 80.0
    # ... other settings
}
```

### **Adding New Vehicle Types**
1. Add new vehicle class (e.g., `Bus`, `Motorcycle`)
2. Add settings to `VEHICLE_SPACING` configuration
3. The system automatically uses the new settings

### **Global Fallback**
Unknown vehicle types use the `"DEFAULT"` settings for safety.

## 🧪 **Testing**

Run the test script to verify individual collision rates:
```bash
python test_individual_collision_rates.py
```

This test will:
- Display each vehicle type's settings
- Spawn mixed traffic with different vehicle types  
- Monitor minimum distances achieved by each type
- Verify that vehicles behave according to their settings

## ✅ **Benefits**

1. **Realistic Traffic**: Different vehicle types behave appropriately
2. **Flexible Configuration**: Easy to adjust individual vehicle behavior
3. **Scalable System**: New vehicle types automatically supported
4. **Performance Optimized**: Vehicles only search/calculate what they need
5. **Safety Maintained**: Each vehicle type has appropriate collision prevention

The individual collision rate system creates much more realistic and diverse traffic patterns while maintaining the safety guarantees of the collision prevention system.