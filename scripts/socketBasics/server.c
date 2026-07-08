#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#define PORT 8080
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

// structs are collections of data 


int main(int argc, char* const argv[]){
	printf("Starting Main\n");
	int server_fd, new_socket;
	ssize_t valread;
	struct sockaddr_in address;
	int opt = 1;
	
	// setting out length variable - sizeof() gives us size in bytes
	socklen_t addrlen = sizeof(address);

	// setting our buffer in memory 
	char buffer[1024] = { 0 };

	// setting server message
	char * hello = "Welcome to the server\n";
	
	// create socket file descriptor - create catch for errors
	if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0){
		perror("socket failed");
		exit(EXIT_FAILURE);
	}

	// Forcefully attaching socket to target port
	if (setsockopt(server_fd, SOL_SOCKET,
				SO_REUSEADDR | SO_REUSEPORT, &opt,
				sizeof(opt))){
		perror("setsockopt");
		exit(EXIT_FAILURE);
	}
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;

	// set listening port to 54321 
	address.sin_port = htons(PORT);

	// Binding socket to address and port 
	if (bind(server_fd, (struct sockaddr*)&address,sizeof(address)) < 0) {
		perror("bind failed");
		exit(EXIT_FAILURE);
	}
	printf("Socket successfully bound to port %d\n", PORT);

	if (listen(server_fd,3) < 0){
		perror("listen");
		exit(EXIT_FAILURE);
	}
	printf("Server listening on port %d\n", PORT);

	if ((new_socket = accept(server_fd, (struct sockaddr*)&address, &addrlen)) < 0){
		perror("accept");
		exit(EXIT_FAILURE);
	}
	printf("Client connected!\n");

	// subtract 1 for the null
	// terminate process at the end
	// How to set server to listen until data is done in for loop
	valread = read(new_socket, buffer, 1024 - 1);
	printf("%s\n", buffer);
	
	int i;
	for (i=0; i < 10; i++){
		send(new_socket, hello,strlen(hello), 0);
		printf("%i\n", i);
	}
	
	printf("10 hello messages sent\n");

	close(new_socket);

	close(server_fd);
	
	return 0;
}












