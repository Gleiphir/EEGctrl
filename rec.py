import serial
import csv
filename = input()

com = serial.Serial("COM3",baudrate=115200)

print(com.isOpen())

with open("{}-rec.csv".format(filename),"w") as fp:
    for i in range(1000):
        t = com.readline().decode('utf-8')
        fp.write(t)
        #fp.write("\n")
        print(t)



