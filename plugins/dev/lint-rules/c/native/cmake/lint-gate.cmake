# The lint gate of the build: every target of the project passes through lint_gate(<target>), so a
# compiler warning or a clang-tidy finding fails `cmake --build`. The warnings on are the ones that
# find a defect: a conversion that loses the value, a name that covers another, a null dereferenced. The dependencies are SYSTEM
# (cmake/dependencies.cmake): their headers are neither warned about nor analysed.
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
find_program(LINT_GATE_CLANG_TIDY NAMES clang-tidy REQUIRED)

function(lint_gate target)
    target_compile_options(${target} PRIVATE
        -Wall -Wextra -Werror -Wshadow -Wconversion -Wsign-conversion
        -Wnull-dereference -Wformat=2 -Wimplicit-fallthrough -Wstrict-prototypes -Wcast-qual -Wvla
        # A name never used is cleaning, not a defect.
        -Wno-unused-parameter -Wno-unused-variable -Wno-unused-function -Wno-unused-but-set-variable)
    set_target_properties(${target} PROPERTIES C_CLANG_TIDY "${LINT_GATE_CLANG_TIDY}")
endfunction()
