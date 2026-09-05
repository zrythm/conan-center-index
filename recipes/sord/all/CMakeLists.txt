cmake_minimum_required(VERSION 3.15)
project(sord LANGUAGES C)

add_library(sord-0)

target_sources(sord-0 PRIVATE src/sord.c src/syntax.c)

find_package(serd CONFIG REQUIRED)
find_package(zix CONFIG REQUIRED)

target_include_directories(
  sord-0
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_features(sord-0 PRIVATE c_std_99)

target_compile_definitions(sord-0 PRIVATE SORD_INTERNAL SORD_VERSION="0.16.22")

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(sord-0 PUBLIC SORD_STATIC)
endif()

target_link_libraries(sord-0 PRIVATE serd::serd zix::zix)

if(UNIX)
  target_link_libraries(sord-0 PRIVATE m)
endif()

set_target_properties(sord-0 PROPERTIES C_VISIBILITY_PRESET hidden)

include(GNUInstallDirs)
install(TARGETS sord-0)
install(
  FILES include/sord/sord.h include/sord/sordmm.hpp
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/sord-0/sord
)
