use std::net::TcpListener;

fn main() {
    let port = 50051;
    let listener = TcpListener::bind(format!("0.0.0.0:{}", port)).unwrap();
    println!("Rust Encryption Microservice running on port {}", port);

    // In a real implementation, this would be a gRPC server
    // handling X25519 public key distribution and validation
    for stream in listener.incoming() {
        match stream {
            Ok(_stream) => {
                println!("New connection to encryption service");
            }
            Err(e) => {
                println!("Error: {}", e);
            }
        }
    }
}
