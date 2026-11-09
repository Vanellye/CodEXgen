cmake_minimum_required(VERSION 3.10.2)
project(codexgen_pons LANGUAGES CXX)

set(PANTHEON_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/../../../../pantheon)

add_library(codexgen_pons SHARED
    jni/olpirt_jni.cpp
    ${PANTHEON_ROOT}/src/runtime.cpp
    ${PANTHEON_ROOT}/src/faculty_engine.cpp
)
target_include_directories(codexgen_pons PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${PANTHEON_ROOT}/include
)
set_target_properties(codexgen_pons PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
target_compile_options(codexgen_pons PRIVATE -Wall -Wextra)

find_library(log_lib log)
target_link_libraries(codexgen_pons ${log_lib})
