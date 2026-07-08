#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#define PORT 8080
#define BACKLOG 3
#define BUFFER_SIZE 1024
#define HEADER "nginx/1.18.0."

// use port 65530 to send out data
// honeypot variation: listen on port 8080 - unencrypted over TLS 

// how to route to webpage based on internal html doc 

typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;

typedef uint8_t ui8;
typedef uint16_t ui16;
typedef uint32_t ui32;
typedef uint64_t ui64;
typedef float f32;
typedef double f64;


int main(int argc, char* const argv[]){
	printf("Starting up honeypot server...\n");

	int server_fd, new_socket; // server_fd is main server var
	ssize_t valread;
	struct sockaddr_in address;
	socklen_t addrlen = sizeof(address);
	// create buffer in memory 
	char buffer[BUFFER_SIZE] = {0};
	const char* message = "Server Message\n"; // set greeting message here
	const char* returnMessage = "200 OK";
	const char* nullMessage = "404 Not Found";
	const char* blockMessage = "401 Unauthorized";
	const char* bugMessage = "500 Internal Server Error";

	// create socket
	server_fd = socket(AF_INET, SOCK_STREAM, 0);
	if (server_fd < 0){
		perror("socket failed");
		return -1;
	}

	int opt = 1;
	if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0){
		perror("setsockopt failed");
		close(server_fd);
		return -1;
	}

	// configure address struct
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons(PORT);

	// bind server to socket target port
	if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0){
		perror("bind failed");
		close(server_fd);
		return -1;
	}
	printf("Bind successful\n");

	// set listening
	if (listen(server_fd, BACKLOG) < 0){
		perror("listen state failed");
		close(server_fd);
		return -1;
	}
	printf("Server listening on port %d\n", PORT);

	// accept data
	new_socket = accept(server_fd, (struct sockaddr*)&address, &addrlen);
	if (new_socket < 0){
		perror("accept failed");
		close(server_fd);
		return -1;
	}
	printf("Connection accepted\n");

	// receive data 
	valread = recv(new_socket, buffer, BUFFER_SIZE -1, 0);
	if (valread < 0){
		perror("receive failed");
	} else {
		buffer[valread] = '\0';
		printf("Received: %s\n", buffer);
	}

	// log client info -> route to another blocked port?
	
	// TODO: Config ufw on pi to block outbound traffic from port 8080

	// send respone -> send back http codes?
	if (send(new_socket, message, strlen(message), 0) < 0){
		perror("send failed");
		return -1;
	}
	
	printf("sending return message...\n"); // 200 return code 
	if (send(new_socket, returnMessage, strlen(returnMessage), 0) < 0){
		perror("return message failed to send...");
	}

	printf("Moving toward cleanup\n");

	// clean up
	close(new_socket);
	close(server_fd);

	return 0;
}

