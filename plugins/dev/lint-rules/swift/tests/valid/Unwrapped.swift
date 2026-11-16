import Foundation

func first(_ values: [Int]) -> Int {
  guard let value = values.first else { return 0 }
  let odd = !value.isMultiple(of: 2)
  return odd && value != 3 ? value : 0
}

func load(_ url: URL) throws -> Data {
  return try Data(contentsOf: url)
}

final class Screen {
  var title: String?
}
