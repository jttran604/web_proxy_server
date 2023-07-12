import socket

#Open Welcome Socket Connection
welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSocket.bind(('localhost', 5005))

#While Connection is Available, Listen
while True:
    print("WEB PROXY SERVER IS LISTENING\n")
    
    welcomeSocket.listen()
    
    #Establish Client Connection
    (clientSocket, clientAddress) = welcomeSocket.accept()
    message = clientSocket.recv(4096).decode("utf-8")
    
    print("MESSAGE RECIEVED FROM CLIENT:")
    print(message)

    print("END OF MESSAGE RECIEVED FROM CLIENT\n")

    #Split Message Into Components; Following 3 Components Relate to The Requests First Line 
    messageList = message.split(" ")

    method = messageList[0]
    destAddr = messageList[1][1: ]
    HTTPVer = messageList[2][0 : 8]

    print("[PARSE MESSAGE HEADER]:\n")
    print("METHOD =" + method + ", DESTADDRESS =" + destAddr + ", HTTPVersion =" +  HTTPVer + "\n")

    #Split URL Components
    destAddrComponents = destAddr.split("/")

    hostName = destAddrComponents[0]
    remaining = "/".join(destAddrComponents[1:])
    file = destAddrComponents[len(destAddrComponents) - 1]
    fileName = 'cache\\' + file

    #Splits Message By Line; Joins Together Lines that remain consistent between different requests for later reuse
    reusableMessage = "\n".join(message.split("\n")[3:])  

    if (method == "GET"):
        
        #Looks For File in Cache; If opened, simple lookup is performed, otherwise must build request
        objectFound = False
        try:
            open(fileName)
            objectFound = True
            print("[LOOK UP IN THE CACHE]: FOUND IN THE CACHE: FILE =" + fileName)
        except IOError:
            print("[LOOK UP IN THE CACHE]: NOT FOUND, BUILD REQUEST TO SEND TO ORIGINAL SERVER")
            print("[PARSE REQUEST HEADER] HOSTNAME IS " + hostName)
            if (remaining != "/"):
                print("[PARSE REQUEST HEADER] URL IS " + remaining)
            if (file != ''):
                print("[PARSE REQUEST HEADER] FILENAME IS " + file + "\n")


        #Case for if Request must be built
        if (objectFound != True) : 
            
            #Establish Server Connection
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.connect((hostName, 80))

            #Builds Header and Sends to Server
            print("REQUEST MESSAGE SENT TO ORIGINAL SERVER:")
            requestHeader = str(method + " /" + remaining + " HTTP/1.1\r\nHost: " + hostName + "\r\n")
            requestHeader += "Connection: close\r\n" + reusableMessage
            print(requestHeader)
            serverSocket.send(bytes(requestHeader, "utf-8"))

            print("END OF MESSAGE SENT TO ORIGINAL SERVER\n")

            #Stores Server Response and Decodes
            response = serverSocket.recv(4096)
            decodedMessage = response.decode("utf-8")

            #Stores Given Response
            decodedSplit = decodedMessage.split("\r\n\r\n")
            headerInformation = str(decodedSplit[0] + "\r\n\r\n")
            htmlCode = decodedSplit[1]
            
            #Converts Response Code to Individual String
            responseCode = headerInformation.split(' ')[1]
            
            print("RESPONSE HEADER FROM ORIGINAL SERVER")
            print(headerInformation)  
            print("END OF HEADER\n")
            
            #If Response is 200 OK, write to Cache; If Response is Bad Request, ERROR, Break; Otherwise No Action
            if (responseCode == "200"):
                print("[WRITE FILE INTO CACHE:]  " + fileName + "\n")
                file = open(fileName, 'w')
                file.write(htmlCode)
                file.close()
            if (responseCode == "400"):
                print("ERROR, GIVEN RESPONSE CODE: " + responseCode)
                print("\n" + "Unable to Print Bad Request")
                break

            #Builds Header and Sends Response back to Client
            print("RESPONSE HEADER FROM PROXY TO CLIENT:")
            print(headerInformation)
            clientHeader = headerInformation + htmlCode
            clientSocket.send(bytes(clientHeader, "utf-8"))
            clientMessage = clientSocket.recv(4096).decode("utf-8")
            print("END OF HEADER\n")
            break

        else:
            
            #Builds Header and Sends Response back to Client
            print("RESPONSE HEADER FROM PROXY TO CLIENT:")
            clientData = open(fileName).read()
            clientHeader = "HTTP/1.0 200 OK\r\n"
            clientSocket.send(bytes(clientHeader + clientData, "utf-8"))
            print(clientHeader)
            print("END OF HEADER\n")


    else:

        #Establish Server Connection
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.connect((hostName, 80))

        #Builds Header and Sends to Server
        print("REQUEST MESSAGE SENT TO ORIGINAL SERVER:")
        requestHeader = str(method + " /" + remaining + " HTTP/1.1\r\nHost: " + hostName + "\r\n")
        requestHeader += "Connection: close\r\n" + reusableMessage
        print(requestHeader)
        serverSocket.send(bytes(requestHeader, "utf-8"))

        print("END OF MESSAGE SENT TO ORIGINAL SERVER\n")

        #Stores Server Response and Decodes
        response = serverSocket.recv(4096)
        decodedMessage = response.decode("utf-8")

        #Stores Given Response
        decodedSplit = decodedMessage.split("\r\n\r\n")
        headerInformation = str(decodedSplit[0] + "\r\n\r\n")
        htmlCode = decodedSplit[1]
            
        #Converts Response Code to Individual String
        responseCode = headerInformation.split(' ')[1]
            
        print("RESPONSE HEADER FROM ORIGINAL SERVER")
        print(headerInformation)             

        #Builds Header and Sends Response back to Client
        print("RESPONSE HEADER FROM PROXY TO CLIENT:")
        print(headerInformation)
        clientHeader = headerInformation + htmlCode
        clientSocket.send(bytes(clientHeader, "utf-8"))
        clientMessage = clientSocket.recv(4096).decode("utf-8")
        print("END OF HEADER\n")
        break

    clientSocket.close()
    break

welcomeSocket.close()