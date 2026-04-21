#!/bin/bash

# Generate certificates for MQTT TLS testing
# Creates a self-signed CA, broker certificate, and client certificate

set -e

mkdir -p certs
cd certs

# Generate CA private key
openssl genrsa -out ca.key 2048

# Generate CA certificate
openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
    -subj "/C=US/ST=CA/L=Local/O=MQTT-Test/CN=mqtt-ca"

# Generate broker private key
openssl genrsa -out broker.key 2048

# Generate broker certificate signing request
openssl req -new -key broker.key -out broker.csr \
    -subj "/C=US/ST=CA/L=Local/O=MQTT-Test/CN=localhost"

# Sign broker certificate with CA
openssl x509 -req -in broker.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out broker.crt -days 365 -sha256

# Generate client_a private key
openssl genrsa -out client_a.key 2048

# Generate client_a certificate signing request
openssl req -new -key client_a.key -out client_a.csr \
    -subj "/C=US/ST=CA/L=Local/O=MQTT-Test/CN=mqtt-client-a"

# Sign client_a certificate with CA
openssl x509 -req -in client_a.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out client_a.crt -days 365 -sha256

# Generate client_b private key
openssl genrsa -out client_b.key 2048

# Generate client_b certificate signing request
openssl req -new -key client_b.key -out client_b.csr \
    -subj "/C=US/ST=CA/L=Local/O=MQTT-Test/CN=mqtt-client-b"

# Sign client_b certificate with CA
openssl x509 -req -in client_b.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out client_b.crt -days 365 -sha256

# Clean up temporary files
rm -f broker.csr client_a.csr client_b.csr

echo "Certificates generated in certs/ directory:"
ls -lh *.crt *.key *.srl 2>/dev/null | awk '{print "  " $9}'
