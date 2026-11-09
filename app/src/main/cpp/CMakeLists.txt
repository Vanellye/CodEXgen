cmake_minimum_required(VERSION 3.10.2)
project(codexgen_pons LANGUAGES CXX)

add_library(codexgen_pons SHARED jni/olpirt_jni.cpp)
target_include_directories(codexgen_pons PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
set_target_properties(codexgen_pons PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
target_compile_options(codexgen_pons PRIVATE -Wall -Wextra)

find_library(log_lib log)
target_link_libraries(codexgen_pons ${log_lib})
