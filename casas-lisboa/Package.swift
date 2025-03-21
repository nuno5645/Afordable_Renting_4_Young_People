// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "casas-lisboa",
    platforms: [
        .iOS(.v15)
    ],
    products: [
        .library(
            name: "casas-lisboa",
            targets: ["casas-lisboa"]),
    ],
    dependencies: [
        .package(url: "https://github.com/evgenyneu/keychain-swift.git", from: "20.0.0")
    ],
    targets: [
        .target(
            name: "casas-lisboa",
            dependencies: [
                .product(name: "KeychainSwift", package: "keychain-swift")
            ]),
        .testTarget(
            name: "casas-lisboaTests",
            dependencies: ["casas-lisboa"]),
    ]
) 