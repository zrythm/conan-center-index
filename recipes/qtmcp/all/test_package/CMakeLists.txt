cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 6.8 REQUIRED COMPONENTS Core Network)
find_package(QtMcp REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE
    QtMcp::StreamableHttp QtMcp::Server QtMcp::Common Qt6::Core Qt6::Network)
