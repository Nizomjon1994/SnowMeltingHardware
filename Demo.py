import time
import datetime

heating_on_time = time.time()
print()
print(heating_on_time)
time.sleep(3)
heating_off_time = time.time()
print(heating_off_time)
formatted_heating_on_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(heating_on_time))
formatted_heating_off_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(heating_off_time))
calculated_heating_time = heating_off_time - heating_on_time
d = divmod(calculated_heating_time, 86400)
print(d[0] * 86400)
h = divmod(d[1], 3600)  # hours
print(h[0] * 3600)
m = divmod(h[1], 60)  # minutes
print(m[0] * 60)
s = m[1]  # seconds
print(s)

print('%d days, %d hours, %d minutes, %d seconds' % (d[0], h[0], m[0], s))
print(formatted_heating_on_time)
print(formatted_heating_off_time)
t = ('%d' % (d[0] * 86400 + h[0] * 3600 + m[0] * 60 + s))
print(t)
# print("Calculated time " + (d[0] * 86400 + h[0] * 60 * 60 + m[0] * 60 + s))
