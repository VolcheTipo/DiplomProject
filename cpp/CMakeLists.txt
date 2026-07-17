cmake_minimum_required(VERSION 3.15)
project(DiplomProject LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

add_executable(${PROJECT_NAME}
        main.cpp
        PythonBridge.cpp
        main.cpp
        PythonBridge.cpp
)

target_include_directories(${PROJECT_NAME} PRIVATE
        ${Python3_INCLUDE_DIRS}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(${PROJECT_NAME} PRIVATE
        ${Python3_LIBRARIES}
)

target_compile_definitions(${PROJECT_NAME} PRIVATE
        PROJECT_SOURCE_DIR="${CMAKE_SOURCE_DIR}"
)

set_target_properties(${PROJECT_NAME} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
)
