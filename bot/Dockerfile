FROM golang:1.22
WORKDIR /app
COPY bot.go .
RUN go mod init bot && go get github.com/pebbe/zmq4 && go build -o bot .
CMD ["./bot"]
