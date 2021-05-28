import pyshark
from matplotlib import pyplot as plt
import time
import os
import json
import subprocess


def main():
    snd_x_axis = [0]
    snd_y_axis = [0]
    rcv_x_axis = [0]
    rcv_y_axis = [0]
    snd_period = 0
    rcv_period = 0
    receiver_average_bitrate = ''
    ip = "127.0.0.1"
    interval = 0.1
    port = 4040
    server_process = subprocess.Popen(f'iperf3 -s -p {port} -i {interval}', encoding = 'utf-8', stdout = subprocess.PIPE, shell = True)
    client_process = subprocess.Popen(f'iperf3 -c {ip} -p {port} -i {interval}', encoding = 'utf-8', stdout = subprocess.PIPE, shell = True)
    #time.sleep(15)

    


    capturer = pyshark.LiveCapture(interface = 'lo', display_filter = 'tcp.srcport == 4040 || tcp.dstport == 4040')
    timeout = 10
    start = time.time()
    retransmition_packet_counter = 0
    received_packet_counter = 0
    dic_of_received_packets = {}
    
    # time_measure = 0.01
    # previous = 0
    # difference = 0
    # counter = 0
    # x_axis = [0]



    # snd_sum_of_lenghts = 0
    # snd_period = 0


#    rcv_time_measure = 0.01
#    rcv_previous = 0
#    rcv_difference = 0

    # rcv_sum_of_lenghts = 0
    # rcv_period = 0



#calculating Number of recieved packets and Number of retransmited packets
    for pkt in capturer.sniff_continuously():
        current_seq_number = pkt[pkt.transport_layer].seq_raw
        current_src_port = pkt[pkt.transport_layer].srcport

        # snd_bitrate = 0
        # difference = float(pkt.sniff_timestamp) - start
        # if int(current_src_port) == 4040:
        #     snd_sum_of_lenghts += float(pkt.length)
        #     snd_period += difference - previous
        #     if snd_period > time_measure:
        #         snd_bitrate = (snd_sum_of_lenghts/snd_period)
        #         snd_x_axis.append(snd_period + x_axis[counter])
        #         snd_y_axis.append(snd_bitrate/(10 ** 6))
        #         snd_period = 0
        #         snd_sum_of_lenghts = 0
        #         counter += 1
        # else:
        #     rcv_sum_of_lenghts += float(pkt.length)
        #     rcv_period += difference - previous
        #     if rcv_period > time_measure:
        #         rcv_bitrate = (rcv_sum_of_lenghts/rcv_period)
        #         rcv_x_axis.append(rcv_period + x_axis[counter])
        #         rcv_y_axis.append(rcv_bitrate/(10 ** 6))
        #         rcv_period = 0
        #         rcv_sum_of_lenghts = 0
        #         counter += 1
        
        if time.time() - start > timeout:
            break
        else:
            print(pkt)
            if int(current_src_port) == port:
                received_packet_counter += 1
            if current_seq_number in dic_of_received_packets:
                dic_of_received_packets[current_seq_number] += 1
                retransmition_packet_counter += 1
            else:
                dic_of_received_packets[current_seq_number] = 1
    
        # previous = difference
        # x_axis.append(difference)

    while True:
        client_output = client_process.stdout.readline()
        print(client_output)########################################
        c_index = 0
        client_bitrate_str = ''
        if client_output.find("bits/sec") != -1:
            c_index = client_output.find("bits/sec") + -3
            while client_output[c_index] != ' ':
                client_bitrate_str = client_output[c_index] + client_bitrate_str
                c_index -= 1
            snd_x_axis.append(snd_period + interval)
            print('$' + client_bitrate_str + '$')
            snd_y_axis.append(float(client_bitrate_str))
            snd_period += interval
        if 'sender' in client_output:
            sender_index = client_output.find('bits/sec')
            temp = sender_index - 3
            while client_output[temp] != ' ':
                temp -= 1
            receiver_average_bitrate = client_output[temp:sender_index + len('bits/sec')]
        if client_output == '':
            break
    while True:
        server_output = server_process.stdout.readline()
        print(server_output)########################################
        s_index = 0
        server_bitrate_str = ''
        if server_output.find("bits/sec") != -1:
            s_index = server_output.find("bits/sec") - 3
            while server_output[s_index] != ' ':
                server_bitrate_str = server_output[s_index] + server_bitrate_str
                s_index -= 1
            
            rcv_x_axis.append(rcv_period + interval)
            print('#' + server_bitrate_str + '#')
            rcv_y_axis.append(float(server_bitrate_str))
            rcv_period += interval
        if 'receiver' in server_output:
            break
    
    print(f'Average Sender Throughput: {receiver_average_bitrate}')
    plt.plot(snd_x_axis, snd_y_axis, color = 'red')
    plt.plot(rcv_x_axis, rcv_y_axis, color = 'blue')
    plt.show()
    

    print("Number of recieved packets: {}".format(received_packet_counter))
    print("Number of retransmited packets: " + str(retransmition_packet_counter))
        

main()