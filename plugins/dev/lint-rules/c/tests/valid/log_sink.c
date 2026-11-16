#include <stdarg.h>
#include <stdio.h>

// The logger's sink writes to the stream it is handed: the console is one of them.
static void write_line(FILE* sink, const char* format, va_list arguments) {
  (void)vfprintf(sink, format, arguments);
  (void)fputc('\n', sink);
}

void log_line(FILE* sink, const char* format, ...) {
  va_list arguments;
  va_start(arguments, format);
  write_line(sink, format, arguments);
  va_end(arguments);
}

void save(FILE* file, int value) { (void)fprintf(file, "%d\n", value); }
