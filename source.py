import pyshark
from matplotlib import pyplot as plt
import time
import subprocess
import os
import signal
import colorama

class MyTextFormat:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def main():
    snd_x_axis = []
    snd_y_axis = []
    rcv_x_axis = []
    rcv_y_axis = []
    snd_period = 0
    rcv_period = 0
    receiver_average_bitrate = ''
    ip = '127.0.0.1'
    interval = 0.1
    port = 4040
    server_process = subprocess.Popen(f'iperf3 -s -p {port} -i {interval}', encoding = 'utf-8', stdout = subprocess.PIPE, shell = True)
    client_process = subprocess.Popen(f'iperf3 -c {ip} -p {port} -i {interval}', encoding = 'utf-8', stdout = subprocess.PIPE, shell = True)

    capturer = pyshark.LiveCapture(interface = 'lo', display_filter = 'tcp.srcport == 4040 || tcp.dstport == 4040')
    timeout = 10
    start = time.time()
    retransmition_packet_counter = 0
    received_packet_counter = 0
    dic_of_received_packets = {}

#Calculating number of recieved packets and Number of retransmited packets
    print('Capturing...')
    capturer.sniff(timeout = timeout)
    print('Capturing done\n')

    for i in range(len(capturer)):
        received_packet_counter += 1
        data = f'{capturer[i]}'
        if 'retransmission' in data or 'Retransmission' in data:
            retransmition_packet_counter += 1
    # for pkt in capturer.sniff_continuously():
    #     current_seq_number = pkt[pkt.transport_layer].seq_raw
    #     current_src_port = pkt[pkt.transport_layer].srcport
    #     if time.time() - start > timeout:
    #         break
    #     else:
    #         # print(pkt)
    #         if int(current_src_port) == port:
    #             received_packet_counter += 1
    #         if current_seq_number in dic_of_received_packets:
    #             dic_of_received_packets[current_seq_number] += 1
    #             retransmition_packet_counter += 1
    #         else:
    #             dic_of_received_packets[current_seq_number] = 1

#Plotting
    while True:
        client_output = client_process.stdout.readline()
        # print(client_output)########################################
        c_index = 0
        client_bitrate_str = ''
        if client_output.find('bits/sec') != -1:
            c_index = client_output.find('bits/sec') + -3
            while client_output[c_index] != ' ':
                client_bitrate_str = client_output[c_index] + client_bitrate_str
                c_index -= 1
            snd_x_axis.append(snd_period + interval)
            # print('$' + client_bitrate_str + '$')
            snd_y_axis.append(float(client_bitrate_str))
            snd_period += interval
        if 'sender' in client_output:
            sender_index = client_output.find('bits/sec')
            temp = sender_index - 3
            while client_output[temp] != ' ':
                temp -= 1
            receiver_average_bitrate = client_output[temp + 1:sender_index + len('bits/sec')]
        if client_output == '':
            break
    while True:
        server_output = server_process.stdout.readline()
        # print(server_output)########################################
        s_index = 0
        server_bitrate_str = ''
        if server_output.find('bits/sec') != -1:
            s_index = server_output.find('bits/sec') - 3
            while server_output[s_index] != ' ':
                server_bitrate_str = server_output[s_index] + server_bitrate_str
                s_index -= 1
            
            rcv_x_axis.append(rcv_period + interval)
            # print('#' + server_bitrate_str + '#')
            rcv_y_axis.append(float(server_bitrate_str))
            rcv_period += interval
        if 'receiver' in server_output:
            break
    
    print('Average Sender Throughput: ' + colorama.Fore.GREEN + MyTextFormat.BOLD + receiver_average_bitrate + MyTextFormat.END + colorama.Fore.RESET)
    print('Number of recieved packets: ' + colorama.Fore.GREEN + MyTextFormat.BOLD + str(received_packet_counter) + MyTextFormat.END + colorama.Fore.RESET)
    print('Number of retransmitted packets: ' + colorama.Fore.GREEN + MyTextFormat.BOLD + str(retransmition_packet_counter) + MyTextFormat.END + colorama.Fore.RESET)
    print('')
    plt.plot(snd_x_axis, snd_y_axis, label = 'Sender', color = 'red')
    plt.plot(rcv_x_axis, rcv_y_axis, label = 'Receiver', color = 'blue')
    plt.legend(loc = 'best')
    plt.grid()
    plt.xlabel('Time(sec)')
    plt.ylabel('Bitrate(Gbits/sec)')
    print('Close \'Figure 1\' to continue...' + '(' + colorama.Fore.YELLOW + MyTextFormat.BOLD + 'Attention:' + MyTextFormat.END + colorama.Fore.RESET + ' Do not kill the process!' + ')')
    plt.show()

    os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
    

main()