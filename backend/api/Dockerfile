FROM golang:1.21-alpine

WORKDIR /app

COPY go.mod ./
# COPY go.sum ./
# RUN go mod download

COPY *.go ./

RUN go build -o /docker-go-api

EXPOSE 8080

CMD [ "/docker-go-api" ]
