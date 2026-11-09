cmake_minimum_required(VERSION 3.10)
project(pantheon_runtime LANGUAGES CXX)

add_library(pantheon_runtime STATIC src/runtime.cpp)
target_include_directories(pantheon_runtime PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
set_target_properties(pantheon_runtime PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
target_compile_options(pantheon_runtime PRIVATE -Wall -Wextra -pedantic)

add_executable(pantheon_runtime_smoke tests/runtime_smoke.cpp)
target_link_libraries(pantheon_runtime_smoke pantheon_runtime)
set_target_properties(pantheon_runtime_smoke PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
enable_testing()
add_test(NAME pantheon_runtime_smoke COMMAND pantheon_runtime_smoke)
