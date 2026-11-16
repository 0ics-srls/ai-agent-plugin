#include <stdlib.h>

const char* read_key(void) { return getenv("API_KEY"); }

const char* customer_query(void) {
  // TODO(#123): revisit connection pooling
  return "SELECT * FROM customer WHERE id = $1";
}
