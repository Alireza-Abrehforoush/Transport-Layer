import pyshark
from matplotlib import pyplot as plt
import time
import os
import json


def main():
    capturer = pyshark.LiveCapture(interface = 'lo', display_filter = 'tcp.srcport == 4040 || tcp.dstport == 4040')
    timeout = 10
    start = time.time()
    retransmition_packet_counter = 0
    received_packet_counter = 0
    dic_of_received_packets = {}
    
    time_measure = 0.01
    previous = 0
    difference = 0
    counter = 0
    x_axis = [0]



    snd_sum_of_lenghts = 0
    snd_period = 0
    snd_x_axis = [0]
    snd_y_axis = [0]

#    rcv_time_measure = 0.01
#    rcv_previous = 0
#    rcv_difference = 0

    rcv_sum_of_lenghts = 0
    rcv_period = 0
    rcv_x_axis = [0]
    rcv_y_axis = [0]
#calculating Number of recieved packets and Number of retransmited packets
    for pkt in capturer.sniff_continuously():
        current_seq_number = pkt[pkt.transport_layer].seq_raw
        current_src_port = pkt[pkt.transport_layer].srcport

        snd_bitrate = 0
        difference = float(pkt.sniff_timestamp) - start
        
        if int(current_src_port) == 4040:
            snd_sum_of_lenghts += float(pkt.length)
            snd_period += difference - previous
            if snd_period > time_measure:
                snd_bitrate = (snd_sum_of_lenghts/snd_period)
                snd_x_axis.append(snd_period + x_axis[counter])
                snd_y_axis.append(snd_bitrate/(10 ** 6))
                snd_period = 0
                snd_sum_of_lenghts = 0
                counter += 1
        else:
            rcv_sum_of_lenghts += float(pkt.length)
            rcv_period += difference - previous
            if rcv_period > time_measure:
                rcv_bitrate = (rcv_sum_of_lenghts/rcv_period)
                rcv_x_axis.append(rcv_period + x_axis[counter])
                rcv_y_axis.append(rcv_bitrate/(10 ** 6))
                rcv_period = 0
                rcv_sum_of_lenghts = 0
                counter += 1
        
        if time.time() - start > timeout:
            break
        else:
            print(pkt)
            if int(current_src_port) == 4040:
                received_packet_counter += 1
            if current_seq_number in dic_of_received_packets:
                dic_of_received_packets[current_seq_number] += 1
                retransmition_packet_counter += 1
            else:
                dic_of_received_packets[current_seq_number] = 1
    
        previous = difference
        x_axis.append(difference)

    plt.plot(snd_x_axis, snd_y_axis, color = 'red')
    plt.plot(rcv_x_axis, rcv_y_axis, color = 'blue')
    plt.show()
    



    #print()
    print("Number of recieved packets: {}".format(received_packet_counter))
    print("Number of retransmited packets: " + str(retransmition_packet_counter))
        

main()