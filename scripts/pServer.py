import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', int(input("Enter port number : "))))
sock.listen(1)

conn, addr = sock.accept()


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
        conn.sendto(sent.encode('utf-8'), addr)
        continue

    if ch is 2:
        conn.settimeout(5)
        try:
            data = conn.recv(8192).decode('utf-8')
            if data:
                print('\nMessage[' + addr[0] + ':' +
                      str(addr[1]) + '] - ' + data)
            else:
                continue
        except socket.timeout:
            print("No messages received in past 5 seconds.\nTry again later!")
            continue
