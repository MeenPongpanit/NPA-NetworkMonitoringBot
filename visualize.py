import matplotlib.pyplot as plt

def utilize_graph(inocts, speed, delta_time, desc):
    """plot utilization graph corresponding to data given"""
    utization_list = [utilize_cal(x, y, speed, delta_time) for x, y in zip(inocts, inocts[1:])]
    data_size = len(utization_list)
    plt.title(desc)
    plt.xlabel('time from now (seconds)')
    plt.ylabel('ultilization ratio (%)')
    # plt.ylim([0, 100])
    plt.plot([-delta_time*i for i in range(data_size-1, -1, -1)], utization_list)
    plt.savefig('utl.jpg')
    plt.clf()

def utilize_cal(inoct1, inoct2, speed, delta_time):
    """calculate ultilization ratio of interface"""
    return (inoct2-inoct1)*8/speed*100