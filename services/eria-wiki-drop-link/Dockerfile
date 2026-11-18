# Build the ERIA API as a static Go binary.
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/eria-api .

# Minimal runtime image. The process runs as root so it can create files
# on the mounted Fly Volume; the ledger directory itself is mode 0700.
FROM gcr.io/distroless/static-debian12
COPY --from=build /out/eria-api /eria-api
EXPOSE 8787
ENTRYPOINT ["/eria-api"]
