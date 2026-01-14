from app import create_server

server = create_server()

if __name__ == "__main__":
    server.run(debug=True, host=server.config["SERVER_HOST"], port=server.config["SERVER_PORT"])
