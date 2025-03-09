#!/bin/bash

# Certificate setup variables
IP_ADDRESS="100.95.208.157"
CERT_DIR=$(pwd)
OPENSSL_CONFIG_FILE="${CERT_DIR}/ip_openssl.conf"

# Create OpenSSL configuration file for IP address
cat > ${OPENSSL_CONFIG_FILE} << EOL
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = dn

[dn]
C = US
ST = State
L = City
O = Development
OU = Development Team
CN = ${IP_ADDRESS}

[v3_req]
subjectAltName = @alt_names
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = ${IP_ADDRESS}
IP.2 = 127.0.0.1
EOL

echo "Creating new Root CA..."
# Create Root CA
openssl genrsa -out ip_rootCA.key 4096
openssl req -x509 -new -nodes -key ip_rootCA.key -sha256 -days 1024 -out ip_rootCA.crt \
  -subj "/C=US/ST=State/L=City/O=Development CA/OU=Development CA Team/CN=${IP_ADDRESS}"

echo "Creating server certificate..."
# Create server certificate
openssl genrsa -out ip_cert.key 2048
openssl req -new -key ip_cert.key -out ip_cert.csr -config ${OPENSSL_CONFIG_FILE}
openssl x509 -req -in ip_cert.csr -CA ip_rootCA.crt -CAkey ip_rootCA.key -CAcreateserial \
  -out ip_cert.crt -days 825 -sha256 -extfile ${OPENSSL_CONFIG_FILE} -extensions v3_req

echo "Certificate created successfully."
echo "Root CA: ip_rootCA.crt"
echo "Server Certificate: ip_cert.crt"
echo "Server Key: ip_cert.key"

# Verify the certificate
echo -e "\nVerifying certificate..."
openssl x509 -in ip_cert.crt -text -noout | grep -A1 "Subject:" | cat
openssl x509 -in ip_cert.crt -text -noout | grep -A2 "Subject Alternative Name" | cat

echo -e "\nTo use these certificates in your Django project, update your settings with these new certificate files."
echo "To trust these certificates on your iOS device, you need to install ip_rootCA.crt on your device." 