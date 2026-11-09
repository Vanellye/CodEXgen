cmake_minimum_required(VERSION 3.22.1)
project(codexgen_pons LANGUAGES CXX)

add_library(codexgen_pons SHARED jni/olpirt_jni.cpp)
target_include_directories(codexgen_pons PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(codexgen_pons PRIVATE cxx_std_17)
target_compile_options(codexgen_pons PRIVATE -Wall -Wextra -Wpedantic)

find_library(log_lib log)
target_link_libraries(codexgen_pons PRIVATE ${log_lib})
