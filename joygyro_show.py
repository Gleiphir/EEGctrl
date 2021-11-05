from pyjoycon import GyroTrackingJoyCon, get_L_id
import time
from matplotlib import pyplot as plt

joycon_id = get_L_id()
joycon = GyroTrackingJoyCon(*joycon_id)
plt.ion()

datapack = {
    'ptxs' : [],
    'ptys' : [],
    'rotxs' : [],
    'rotys' : [],
    'rotzs' : [],
    'drcxs' : [],
    'drcys' : [],
    'drczs' : [],
}
for i in range(1000):
    #print("joycon pointer:  ", joycon.pointer)
    #print("joycon rotation: ", joycon.rotation)
    #print("joycon direction:", joycon.direction)
    plt.cla()
    #ptx,pty = joycon.pointer.to_tuple()
    rotx,roty,rotz = joycon.rotation.to_tuple()
    drcx,drcy,drcz = joycon.direction.to_tuple()
    #ptxs.append(ptx)
    #ptys.append(pty)
    datapack['rotxs'].append(rotx)
    datapack['rotys'].append(roty)
    datapack['rotzs'].append(rotz)
    datapack['drcxs'].append(drcx)
    datapack['drcys'].append(drcy)
    datapack['drczs'].append(drcz)
    plt.ylim([-1.0, 4.0])
    for key in datapack:
        plt.plot(datapack[key][-20:],label=key)
    #plt.plot(fake.cpu().detach().numpy()[0, :, 0],color='orange')
    plt.legend()
    plt.draw()
    plt.pause(0.1)
    #time.sleep(0.05)