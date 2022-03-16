cmake_minimum_required(VERSION 3.9)
project(NikonPowerBoard)

set(CMAKE_CXX_STANDARD 11)

add_executable(NikonPowerBoard
        avr_compiler.h
        debug.c
        debug.h
        iox32a4.h
        main.c
        main.h)
