# SSL Certificate Setup for IP Address

This guide helps you create SSL certificates for your Django API and configure your iOS app to trust them.

## Generate Certificates

1. Navigate to the certs directory:
   ```
   cd /path/to/django_api/api/certs
   ```

2. Make the script executable:
   ```
   chmod +x create_cert_for_ip.sh
   ```

3. Run the script to generate certificates:
   ```
   ./create_cert_for_ip.sh
   ```

This will create the following files:
- `ip_rootCA.crt` - Root CA certificate
- `ip_rootCA.key` - Root CA private key
- `ip_cert.crt` - Server certificate
- `ip_cert.key` - Server private key
- `ip_openssl.conf` - OpenSSL configuration file

## Configure Django Server

Update your Django settings to use the new certificates:

```python
# In your settings.py file
SECURE_SSL_CERT = os.path.join(BASE_DIR, 'api/certs/ip_cert.crt')
SECURE_SSL_KEY = os.path.join(BASE_DIR, 'api/certs/ip_cert.key')
```

When running the development server, specify the certificate and key:
```
python manage.py runserver 100.95.208.157:8080 --cert /path/to/ip_cert.crt --key /path/to/ip_cert.key
```

## Configure iOS App

There are two approaches to get your iOS app to trust your certificates:

### Option 1: Install the Root CA on your iOS device

1. Email the `ip_rootCA.crt` file to yourself or make it accessible from your iOS device
2. On your iOS device, open the file and follow the prompts to install the profile
3. Go to Settings > General > About > Certificate Trust Settings
4. Enable full trust for the root certificate

### Option 2: Bypass Certificate Validation in Development (Not recommended for production)

Your Info.plist already has the necessary settings to bypass certificate validation for 100.95.208.157. 
If you still encounter issues, you can implement custom certificate validation in your networking code:

```swift
class NetworkManager: NSObject, URLSessionDelegate {
    
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, 
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        // Accept certificates from your specific server
        if challenge.protectionSpace.host == "100.95.208.157" {
            completionHandler(.useCredential, URLCredential(trust: challenge.protectionSpace.serverTrust!))
        } else {
            completionHandler(.performDefaultHandling, nil)
        }
    }
}
```

## Trusting the Certificate in macOS (for development)

To make your Mac trust the certificate (useful for testing with tools like curl):

```
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain /path/to/ip_rootCA.crt
```

## Verifying Certificate

You can verify the certificate is correctly set up with:

```
openssl x509 -in ip_cert.crt -text -noout
```

Check that the Common Name (CN) and Subject Alternative Name (SAN) include the IP address 100.95.208.157. 