import Foundation
import os

let logger = Logger(subsystem: "shop", category: "app")

func greet(_ name: String) {
  logger.info("greeting \(name, privacy: .private)")
}

func write(_ line: String) {
  FileHandle.standardOutput.write(Data((line + "\n").utf8))
}
