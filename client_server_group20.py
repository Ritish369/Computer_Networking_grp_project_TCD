from socket import * # importing socket library
from p2p_message import * # importing the protocol code shared with group 4
import random # importing the random library
from urllib import request # we import the request module from the urllib library
from hardimessage import * # we import the code from group 3 to be able to read their type of messages

# we initialise some variables
personal_id = "" # we initialise our own ID, which is generated in the main
running = True # while this is true the application will run

# Function for the server
def server(personal_id, server_port = 12000):
    # We initialise the socket
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print("Initialising server")
    print(f"ID of server: {personal_id}")
    print("Server prepared to receive messages")
    
    # We initialise some local variables needed to reply to other groups
    rolled_number = 0
    weather = "sunny"

    # This code is to reply to other groups depending on the received message
    while True:
        # we get information on ip address and port number of node sending the message
        info, addr = server_socket.recvfrom(2048)
        # here we reply to messages that have our same protocol
        try:
            # we turn the received message into a string
            protocol_message = P2PMessage.decode(info.decode("utf-8"))
            if protocol_message.message_type == "request":
                if protocol_message.message == "initiate connection":
                    # this way we prepare the reply to a connection request
                    protocol_response = P2PMessage("response", personal_id, protocol_message.sender_id)
                elif protocol_message.message == "what is your favorite team":
                    # this way we prepare a reply to our own game
                    myteam = "Madrid"
                    protocol_response = P2PMessage("response", personal_id, protocol_message.sender_id, myteam)
                elif protocol_message.message == "give me a random number":
                    # this way we prepare a reply to the other group using our protocol
                    mynumber = str(random.randint(1, 100))
                    protocol_response = P2PMessage("response", personal_id, protocol_message.sender_id, mynumber)
                    # we check we have prepared the response and what our response is
                    print(protocol_response.encode())
                
                # we turn the reply into a string
                protocol_answer = protocol_response.encode()
                # we send the reply to the server that has asked us for it
                server_socket.sendto(protocol_answer.encode("utf-8"), addr)

        except ValueError: 
            # If the received message is not of the type of our protocol, we try to see if it is of the other group
            try:
                # This is from the other group
                hardimsg_recv = HardiMessage(0, 0, False, False, "?")
                hardimsg_recv.read_message(message.decode("UTF-8"))
                # If hardimsg_recv is a request
                if hardimsg_recv.req:
                    hardimsg_resp = HardiMessage(unique_id, hardimsg_recv.sourceID, False, True, "Accepted")
                    if hardimsg_recv.msg == "connect":
                        hardimsg_resp = HardiMessage(unique_id, hardimsg_recv.sourceID, False, True, "Accepted")
                    # If message is weather?, set the response message accordingly
                    elif hardimsg_recv.msg == "weather?" and int(hardimsg_recv.sourceID) != unique_id:
                        hardimsg_resp = HardiMessage(unique_id, hardimsg_recv.sourceID, False, True, weather)
                    # If message is a weather type, change own weather to message
                    elif hardimsg_recv.msg == "sunny" or hardimsg_recv.msg == "raining" or hardimsg_recv.msg == "windy" or hardimsg_recv.msg == "cloudy" and int(hardimsg_recv.sourceID) != unique_id:
                        weather = hardimsg_recv.msg
                    print(weather)
                    serverSocket.sendto(hardimsg_resp.create_message().encode("utf-8"), (clientAdress[0],12000))
            except ValueError:
                pass



# We will now work on the client

port_of_server = 12000 # We set our server port number
nodes_met = [] # here we will store the list of nodes we connect with through the broadcast

def node_search():
    # we initialise the client socket
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    
    # we broadcast a message into the network to find the nodes we want to interact with
    string_message = P2PMessage("request", personal_id, "unknown", "initiate connection").encode()
    # the encode function turns the protocol message into a string
    client_socket.sendto(string_message.encode("utf-8"), ('255.255.255.255', port_of_server))
    
    try:
        client_socket.settimeout(5.0) # We set a 5 second limit for blocking operations
        while True:
            try:
                info, addr = client_socket.recvfrom(2048) # in addr we are storing the ip address and the port number
                try:
                    print("Getting nodes...")
                    # we turn the response frpm byte string into our protocol structure
                    retrieved_info = info.decode("utf-8")
                    # we turn the response from the protocol structure into a normal string
                    received_message = P2PMessage.decode(retrieved_info)
                    # We check if the received message is an answer to the broadcast
                    if received_message.message_type == "response":
                        # if it is, we add it (both the ip address and the id) to our nodes list
                        nodes_met.append((addr[0], received_message.sender_id))
                except ValueError:
                        pass
            except timeout:
                break
                     
    finally:
        if nodes_met:
            print("We found nodes!!")
        else:
            print("We didn't find nodes:(")
                  
        client_socket.close()
     
    
def football_teams():
    # We create a function to gather the football teams from all nodes
    client_socket = socket(AF_INET, SOCK_DGRAM)
    # we initialise a list in which we will place all the teams
    teams = []
    # We now proceed to send a request to the nodes we have gathered asking them to send us their favourite team
    for node in nodes_met:
        # we convert the protocol-structured message into a string
        favourite_team = P2PMessage("request", personal_id, node[1], "what is your favorite team").encode()
        # we convert that string into a byte string before sending it to the nodes
        client_socket.sendto(favourite_team.encode("utf-8"), (node[0], port_of_server))
        
    try:
        client_socket.settimeout(3.0) # We wait for 3 seconds to receive all responses
        # And we repeat the process we undertook when gathering the info of the nodes before, but now we gather their football team
        while True:
            try:
                info, addr = client_socket.recvfrom(2048)
                try:
                    retrieved_info = info.decode("utf-8")
                    received_message = P2PMessage.decode(retrieved_info)
                    # We check if the received message is an answer to our broadcast
                    if received_message.message_type == "response":
                        # we add the reply, i.e. the team of the node, to our list of teams
                        teams.append(received_message.message)
                except ValueError:
                    pass
            except timeout:
                print("Here's every node's favourite team:")
                break
    except :
        pass
    
    if teams:
        # now we send our own team
        for node in nodes_met:
            own_team = P2PMessage("response", personal_id, node[1], "Madrid").encode()
            client_socket.sendto(own_team.encode("utf-8"), (node[0], port_of_server))          
        # and we now print all the teams
        print(*teams, sep = ", ")
    else:
        print("We received no teams:(")
    client_socket.close()
                    
                        
# We include now a function for the user to interact and input commands
def client_input(personal_id2, port_of_server2 = 12000):
    global port_of_server, personal_id
    port_of_server = port_of_server2
    personal_id = personal_id2
    while running:
        command = input("Please input a command: ")
        action = actions.get(command, wrong_command)
        action()
            
            
# We now create the functions for all the rest of possible actions

    
# Function to let the user know the requested action does not exist
def wrong_command():
    print("This command does not exist. Please try again.")

# Function to show the nodes connected to the server
def print_nodes():
    node_num = 1
    for node in nodes_met:
        print(f"Node number {node_num} to connect: ")
        print(f"{node[0]}, {node[1]} \n")      
        node_num = node_num + 1

# We associate a specific input command to each possible action
actions = {
        "Find nodes": node_search,
    "Print nodes": print_nodes,
    "Fantasy football": football_teams
}
    