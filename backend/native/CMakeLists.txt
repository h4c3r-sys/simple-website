cmake_minimum_required(VERSION 3.10)
project(NativeConnector)

set(CMAKE_CXX_STANDARD 17)

add_library(connector SHARED src/connector.cpp)
add_executable(connector_test src/connector.cpp)
