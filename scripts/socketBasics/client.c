#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#define PORT 8080


int main(int argc, char const* argv[]){
	int status, valread, client_fd;
	struct sockaddr_in serv_addr;
	char* message = "Hello from Client";
	char buffer[1024] = { 0 };
	if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0){
		printf("\n Socket creation error \n");
		return -1;
	}
	printf("Client Socket successfully created\n");

	serv_addr.sin_family = AF_INET;
	
	// destination port
	serv_addr.sin_port = htons(PORT);

	// Convert IPv4 and IPv6 addresses from text to binary
	if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0){
		printf("Invalid address/ Address not supported \n");
		return -1;
	}
	printf("Successfully converted address to binary\n");

	if ((status = connect(client_fd, (struct sockaddr*)&serv_addr, sizeof(serv_addr))) < 0){
		printf("Connection Failed \n");
		return -1;
	}
	printf("Connected to server successfully!\n");

	// subtract 1 for the null
	// Send 10 messages to server
	// terminate process at the end
	int i;
	for (i = 0; i < 10; i++){
		printf("%i\n", i);
		send(client_fd, message, strlen(message), 0);
	}

	printf("Hello messages sent\n");
	valread = read(client_fd, buffer, 1024 - 1);
	printf("%s\n", buffer);

	// close socket
	close(client_fd);
	return 0;
}

