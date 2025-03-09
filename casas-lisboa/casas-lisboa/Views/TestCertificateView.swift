import SwiftUI

struct TestCertificateView: View {
    @State private var status = "Not tested"
    @State private var isLoading = false
    @State private var responseDetails = ""
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Certificate Validation Test")
                    .font(.title)
                    .fontWeight(.bold)
                
                // Status indicator
                HStack(spacing: 10) {
                    Text("Status:")
                        .fontWeight(.medium)
                    
                    Text(status)
                        .foregroundColor(status == "Success" ? .green : 
                                         status == "Failed" ? .red : .orange)
                        .fontWeight(.semibold)
                    
                    if isLoading {
                        ProgressView()
                    }
                }
                
                // Test buttons
                VStack(spacing: 15) {
                    Button(action: testNetworkService) {
                        HStack {
                            Image(systemName: "network")
                            Text("Test NetworkService Certificate")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Theme.Colors.primary)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    
                    Button(action: testDirectRequest) {
                        HStack {
                            Image(systemName: "link")
                            Text("Test Direct URL Request")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Theme.Colors.secondary)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                }
                
                // Response details
                if !responseDetails.isEmpty {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Response Details:")
                            .font(.headline)
                        
                        Text(responseDetails)
                            .font(.system(.body, design: .monospaced))
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(8)
                    }
                }
                
                // Info about certificate settings
                VStack(alignment: .leading, spacing: 10) {
                    Text("Certificate Settings:")
                        .font(.headline)
                    
                    HStack {
                        Image(systemName: "checkmark.seal.fill")
                            .foregroundColor(.green)
                        Text("Custom certificate validation enabled")
                    }
                    
                    HStack {
                        Image(systemName: "checkmark.seal.fill")
                            .foregroundColor(.green)
                        Text("Target server: 100.95.208.157")
                    }
                    
                    Text("The app is configured to trust certificates from your server by implementing URLSessionDelegate with custom certificate handling.")
                        .font(.callout)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
        }
    }
    
    func testNetworkService() {
        isLoading = true
        status = "Testing..."
        responseDetails = ""
        
        Task {
            do {
                let properties = try await NetworkService.shared.fetchHouses()
                DispatchQueue.main.async {
                    self.status = "Success"
                    self.isLoading = false
                    self.responseDetails = "Successfully retrieved \(properties.count) properties"
                }
            } catch {
                DispatchQueue.main.async {
                    self.status = "Failed"
                    self.isLoading = false
                    self.responseDetails = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
    
    func testDirectRequest() {
        isLoading = true
        status = "Testing..."
        responseDetails = ""
        
        let url = URL(string: "https://100.95.208.157:8080/api/houses/")!
        
        Task {
            do {
                let (data, response) = try await NetworkService.shared.session.data(from: url)
                
                // Extract response details
                let httpResponse = response as? HTTPURLResponse
                let statusCode = httpResponse?.statusCode ?? 0
                let dataPreview = String(data: data.prefix(100), encoding: .utf8) ?? "Unable to decode data"
                
                DispatchQueue.main.async {
                    self.status = "Success"
                    self.isLoading = false
                    self.responseDetails = """
                    Status Code: \(statusCode)
                    Data Size: \(data.count) bytes
                    Preview: \(dataPreview)...
                    """
                }
            } catch {
                DispatchQueue.main.async {
                    self.status = "Failed"
                    self.isLoading = false
                    self.responseDetails = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}

#Preview {
    TestCertificateView()
} 