# Builds PyNifly's NiflyDLL as a Linux shared object named NiflyDLL.dll (the name pyn/niflydll.py loads),
# from an unmodified PyNifly checkout and BadDogSkyrim's nifly fork. Commonwealth Motorbike asset tools.
cmake_minimum_required(VERSION 3.16)
project(NiflyDLLLinux LANGUAGES CXX)
set(PYNIFLY_DIR "" CACHE PATH "PyNifly checkout")
set(NIFLY_DIR "" CACHE PATH "nifly checkout (BadDogSkyrim/nifly)")
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

file(GLOB nifly_src "${NIFLY_DIR}/src/*.cpp")
set(dll_src
    "${PYNIFLY_DIR}/NiflyDLL/Anim.cpp"
    "${PYNIFLY_DIR}/NiflyDLL/Logger.cpp"
    "${PYNIFLY_DIR}/NiflyDLL/NiflyFunctions.cpp"
    "${PYNIFLY_DIR}/NiflyDLL/NiflyWrapper.cpp")
add_library(NiflyDLL SHARED ${nifly_src} ${dll_src})
# the file name the Python side asks for, with no "lib" in front
set_target_properties(NiflyDLL PROPERTIES PREFIX "" OUTPUT_NAME "NiflyDLL" SUFFIX ".dll")
target_include_directories(NiflyDLL PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/shim"      # windows.h and the headers included in another case
    "${PYNIFLY_DIR}/NiflyDLL"
    "${NIFLY_DIR}/include"
    "${NIFLY_DIR}/external")
target_compile_definitions(NiflyDLL PRIVATE NIFLYDLL_EXPORTS NOMINMAX)
# -fdeclspec: __declspec(dllexport) parses (and is ignored: ELF exports every extern symbol); no fused
# multiply-add, so the arithmetic is as the release's own build does it
target_compile_options(NiflyDLL PRIVATE -fdeclspec -ffp-contract=off -w)
target_link_libraries(NiflyDLL PRIVATE ${CMAKE_DL_LIBS})
