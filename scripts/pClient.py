import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = str(input("Enter host ip : "))
port = int(input("Enter port number : "))
addr = (host, port)

sock.connect(addr)


while True:

    print("\n1. Send message.\n2. Check for messages.")

    try:
        ch = int(input("Your choice : "))
    except ValueError:
        print("Invalid choice.\n")
        continue

    if not 0 < ch < 3:
        print("Invalid choice.\n")
        continue

    if ch is 1:
        sent = str(input("\nMessage : "))
        sent += ' '
        sock.sendto(sent.encode('utf-8'), addr)
        continue

    if ch is 2:
        sock.settimeout(5)
        try:
            data = sock.recv(8192).decode('utf-8')
            if data:
                print(
                    "\nMessage[ {} : {} ] - {}".format(host, str(port), data))
            else:
                continue
        except socket.timeout:
            print("No messages received in past 5 seconds.\nTry again later!")
            continue
