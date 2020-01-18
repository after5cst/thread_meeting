cmake_minimum_required(VERSION 2.8.12)
project(thread_meeting)

FIND_PACKAGE(PythonInterp 3 REQUIRED)
FIND_PACKAGE(PythonLibs REQUIRED)
message(STATUS "PYTHON_LIBRARIES = ${PYTHON_LIBRARIES}")
message(STATUS "PYTHON_EXECUTABLE = ${PYTHON_EXECUTABLE}")
message(STATUS "PYTHON_INCLUDE_DIRS = ${PYTHON_INCLUDE_DIRS}")

set (HERE ${CMAKE_CURRENT_SOURCE_DIR})
message(STATUS "HERE = ${HERE}")
set(SOURCE_DIR "${HERE}/src/thread_meeting")
set(SOURCES
    "${SOURCE_DIR}/attendee.cpp"
    "${SOURCE_DIR}/attendee.h"
    "${SOURCE_DIR}/attendee_scope.cpp"
    "${SOURCE_DIR}/attendee_scope.h"
    "${SOURCE_DIR}/baton.cpp"
    "${SOURCE_DIR}/baton.h"
    "${SOURCE_DIR}/baton_scope.cpp"
    "${SOURCE_DIR}/baton_scope.h"
    "${SOURCE_DIR}/enter_exit.cpp"
    "${SOURCE_DIR}/enter_exit.h"
    "${SOURCE_DIR}/functions.cpp"
    "${SOURCE_DIR}/functions.h"
    "${SOURCE_DIR}/globals.cpp"
    "${SOURCE_DIR}/globals.h"
    "${SOURCE_DIR}/keep.cpp"
    "${SOURCE_DIR}/keep.h"
    "${SOURCE_DIR}/peekable_queue.cpp"
    "${SOURCE_DIR}/peekable_queue.h"
    "${SOURCE_DIR}/take.cpp"
    "${SOURCE_DIR}/take.h"
    "${SOURCE_DIR}/transcription_item.cpp"
    "${SOURCE_DIR}/transcription_item.h"
    "${SOURCE_DIR}/transcription_scope.cpp"
    "${SOURCE_DIR}/transcription_scope.h"
    )


FILE(GLOB_RECURSE TESTS RELATIVE ${HERE} "tests/*_test.py")
message( "TESTS=${TESTS}" )

INCLUDE_DIRECTORIES($(SOURCE_DIR))

add_subdirectory(lib/pybind11)
pybind11_add_module(thread_meeting ${SOURCES} ${SOURCE_DIR}/bindings.cpp ${TESTS})

# Unit testing.
enable_testing()
add_test(NAME "unit_tests"
         WORKING_DIRECTORY "${HERE}"
         COMMAND ${PYTHON_EXECUTABLE} "setup.py" "test")
