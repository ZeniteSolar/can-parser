from parse import parse
import numpy as np

filename = "../datalog/filtered/candump-2020-01-29_114446.log.filtered"

voltage_battery_1_value = []
voltage_battery_1_time = []
voltage_battery_2_value = []
voltage_battery_2_time = []
voltage_battery_3_value = []
voltage_battery_3_time = []
current_battery_1_value = []
current_battery_1_time = []
current_battery_2_value = []
current_battery_2_time = []

with open(filename) as fp:
    for linenumber, line in enumerate(fp):
        parsed = parse('({}) can0 {}#{}', line)
        if parsed:
            
            time = float(parsed[0])
            tid = int(parsed[1], 16)
            payload = parsed[2][2:]
            signature = int(parsed[2][0:2], 16)
            length = 2
            if len(payload) == 12:
                value_avg = (int(payload[2:4], 16) << 8) | int(payload[0:2], 16)
                value_min = (int(payload[6:8], 16) << 8) | int(payload[4:6], 16)
                value_max = (int(payload[10:12], 16) << 8) | int(payload[8:10], 16)

            if tid == 0x21:
                if signature == 0xFA:
                    scale = 1/100
                    voltage_battery_1_value.append(value_avg * scale)
                    voltage_battery_1_time.append(time)
                elif signature == 0xFB:
                    scale = 1/100
                    voltage_battery_2_value.append(value_avg * scale)
                    voltage_battery_2_time.append(time)
                elif signature == 0xFC:
                    scale = 1/100
                    voltage_battery_3_value.append(value_avg * scale)
                    voltage_battery_3_time.append(time)
                elif signature == 0xFD:
                    scale = 1/1000
                    current_battery_1_value.append(value_avg * scale)
                    current_battery_1_time.append(time)
                elif signature == 0xFE:
                    scale = 1/1000
                    current_battery_2_value.append(value_avg * scale)
                    current_battery_2_time.append(time)
                else:
                    pass

lengths = np.array([
    len(voltage_battery_1_value),
    len(voltage_battery_2_value),
    len(voltage_battery_3_value),
    len(current_battery_1_value),
    len(current_battery_2_value)
])
print(lengths)

import matplotlib.pyplot as plt
voltage_battery_1_value_ = np.array(voltage_battery_1_value)
voltage_battery_2_value_ = np.array(voltage_battery_2_value)
voltage_battery_3_value_ = np.array(voltage_battery_3_value)
voltage_battery_1_time_ = np.array(voltage_battery_1_time)
voltage_battery_2_time_ = np.array(voltage_battery_2_time)
voltage_battery_3_time_ = np.array(voltage_battery_3_time)
current_battery_1_value_ = np.array(current_battery_1_value)
current_battery_2_value_ = np.array(current_battery_2_value)
current_battery_1_time_ = np.array(current_battery_1_time)
current_battery_2_time_ = np.array(current_battery_2_time)

import pandas as pd

df = pd.DataFrame({
    'Timestamp': voltage_battery_1_time_[:min(lengths)], 
    'Battery 1 Voltage': voltage_battery_1_value_[:min(lengths)], 
    'Battery 2 Voltage': voltage_battery_2_value_[:min(lengths)],
    'Battery 3 Voltage': voltage_battery_3_value_[:min(lengths)],
    'Battery Input Current': current_battery_1_time_[:min(lengths)],
    'Battery Output Current': current_battery_2_time_[:min(lengths)]
})

df.to_csv(filename + '.csv', index=False)

plt.figure(figsize=(20,10))
plt.title("Battery Voltage")
plt.plot(voltage_battery_1_time_, voltage_battery_1_value_, label='Battery 1')
plt.plot(voltage_battery_2_time_, voltage_battery_2_value_, label='Battery 2')
plt.plot(voltage_battery_3_time_, voltage_battery_3_value_, label='Battery 3')
plt.legend()
plt.show()

plt.figure(figsize=(20,10))
plt.title("Battery Current")
plt.plot(current_battery_1_time_, current_battery_1_value_, label='Input')
plt.plot(current_battery_2_time_, current_battery_2_value_, label='Output')
plt.legend()
plt.show()