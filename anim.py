import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_excel('tobe.xlsx')

pressure = df['Pressure (KPA)']
satliq = df['Saturated Liquid (m^3/kg)']
satvap = df['Saturated Vapor (m^3/kg)']
tempa = df['Temp (Celcius)']
entliq = df['Sat. Liquid (kJ/(kg*K)']
entvap = df['Sat. Vap ((kJ/(kg*K)']

yaxis = pd.concat([pressure, pressure.iloc[::-1]], ignore_index = True)
xaxis = pd.concat([satliq, satvap.iloc[::-1]], ignore_index = True)

def pres_extrap(temp):
    for dex, i in enumerate(tempa):
        if temp == i:
            return pressure[dex]
        if temp >= tempa[dex] and temp <= tempa[dex + 1]:
            x = (((pressure[dex+1]-pressure[dex])/(tempa[dex+1]-tempa[dex]))*(temp-tempa[dex]))+pressure[dex]
            return x
        
def satliq_extrap(temp):
    for dex, i in enumerate(tempa):
        if temp == i:
            return satliq[dex]
        if temp >= tempa[dex] and temp <= tempa[dex + 1]:
            x = (((satliq[dex+1]-satliq[dex])/(tempa[dex+1]-tempa[dex]))*(temp-tempa[dex]))+satliq[dex]
            return x
    
def satvap_extrap(temp):
    for dex, i in enumerate(tempa):
        if temp == i:
            return satvap[dex]
        if temp >= tempa[dex] and temp <= tempa[dex + 1]:
            x = (((satvap[dex+1]-satvap[dex])/(tempa[dex+1]-tempa[dex]))*(temp-tempa[dex]))+satvap[dex]
            return x

def entvap_extrap(temp):
    for dex, i in enumerate(tempa):
        if temp == i:
            return entvap[dex]
        if temp >= tempa[dex] and temp <= tempa[dex + 1]:
            x = (((entvap[dex+1]-entvap[dex])/(tempa[dex+1]-tempa[dex]))*(temp-tempa[dex]))+entvap[dex]
            return x

def entliq_extrap(temp):
    for dex, i in enumerate(tempa):
        if temp == i:
            return entliq[dex]
        if temp >= tempa[dex] and temp <= tempa[dex + 1]:
            x = (((entliq[dex+1]-entliq[dex])/(tempa[dex+1]-tempa[dex]))*(temp-tempa[dex]))+entliq[dex]
            return x



temp = 100
ltemp = 60

def caref(coltemp, hotemp):
    return 1 - (coltemp/hotemp)

def isothermal_addition(temp):
    press = pres_extrap(temp)
    initv = satliq_extrap(temp)
    finv = satvap_extrap(temp)
    inits = entliq_extrap(temp)
    fins = entvap_extrap(temp)
    return press, initv, finv, inits, fins

def adiabatic_expansion(temp, ltemp):
    initP, initv, _, inits, fins = isothermal_addition(temp)
    liquid_entropy = entliq_extrap(ltemp)
    vapour_entropy = entvap_extrap(ltemp)
    x = (fins - liquid_entropy)/(vapour_entropy-liquid_entropy)
    new_spvolume = (x*(satvap_extrap(ltemp)-satliq_extrap(ltemp)))+satliq_extrap(ltemp)
    final_press = pres_extrap(ltemp)
    return liquid_entropy, vapour_entropy, x, new_spvolume, final_press, inits

def isothermal_rejection(temp,ltemp):
    liquid_entropy, vapour_entropy, _, _, press, inits = adiabatic_expansion(temp, ltemp)
    new_x = (inits - liquid_entropy)/(vapour_entropy-liquid_entropy)
    final_spvolume = (new_x*(satvap_extrap(ltemp)-satliq_extrap(ltemp)))+satliq_extrap(ltemp)
    return new_x, final_spvolume, inits, press

carof = caref(ltemp, temp)
initpres, initvol, finvol, initent, finent = isothermal_addition(temp)
_, _, qual, qual_phase, fin_press, _ = adiabatic_expansion(temp, ltemp)
new_qual, new_phase, _, _ = isothermal_rejection(temp, ltemp)

print(f'Your input temperatures {temp} and {ltemp} \n \t During Stage 1, \n \t initial Pressure:{initpres}, \n \t initial specific volume:{initvol},\n\t initial specific entropy {initent}')
print(f'At stage 2,\n \t the pressure is same, \n \t the specific volume = {finvol}, \n \t the specific entropy = {finent}')
print(f'At Stage 3, \n \t the pressure is {fin_press}, \n \t liquid quality is {qual}, \n \t the specific volume is {qual_phase}, \n \t the specific entropy is the same')
print(f'At stage 4, pressure is same, \n \t the entropy is same as initial, \n \t the final specifc volume is {new_phase}, \n \t the new quality is {new_qual}')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

print(f'Initial value {initvol} and final value {finvol}')

volrang1 = np.linspace(initvol, finvol, 10)
volrang2 = np.linspace(finvol, qual_phase, 10)
volrang3 = np.linspace(qual_phase, new_phase, 10)
volrang4 = np.linspace(new_phase, initvol, 10)

pressrang1 = [initpres] * 10
pressrang2 = np.linspace(initpres,fin_press,10)
pressrang3 = [fin_press] * 10
pressrang4 = np.linspace(fin_press, initpres, 10)

x = [item for sublist in [volrang1,volrang2,volrang3,volrang4] for item in sublist]
y = [item for sublist in [pressrang1, pressrang2,pressrang3, pressrang4] for item in sublist]

x_show = []
y_show = []

# Initial setup for your plot
plt.plot(xaxis, yaxis, label='Initial Plot')  # Replace with your initial plot data
line, = plt.plot([], [], label='Animated Plot', color='orange')  # Line to be animated
plt.xscale('log')
plt.yscale('log')
# Update function for FuncAnimation
def update(frame):
    plt.xscale('log')
    plt.yscale('log')
    x_show.append(x[frame])
    y_show.append(y[frame])
    line.set_data(x_show, y_show)
    return line,

# Create animation
ani = FuncAnimation(plt.gcf(), update, frames=range(len(x)), blit=True, interval = 300)

plt.legend()
plt.show()
