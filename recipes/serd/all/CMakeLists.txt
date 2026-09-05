cmake_minimum_required(VERSION 3.15)
project(serd LANGUAGES C)

add_library(serd-0)

target_sources(
  serd-0
  PRIVATE src/base64.c
          src/byte_source.c
          src/env.c
          src/n3.c
          src/node.c
          src/read_utf8.c
          src/reader.c
          src/string.c
          src/system.c
          src/uri.c
          src/writer.c
)

target_include_directories(
  serd-0
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_features(serd-0 PRIVATE c_std_99)

target_compile_definitions(serd-0 PRIVATE SERD_INTERNAL SERD_VERSION="0.32.10")

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(serd-0 PUBLIC SERD_STATIC)
endif()

if(CMAKE_SYSTEM_NAME MATCHES "Linux|GNU")
  target_compile_definitions(serd-0 PRIVATE _POSIX_C_SOURCE=200809L)
endif()

if(UNIX)
  target_link_libraries(serd-0 PRIVATE m)
endif()

set_target_properties(serd-0 PROPERTIES C_VISIBILITY_PRESET hidden)

include(GNUInstallDirs)
install(TARGETS serd-0)
install(FILES include/serd/serd.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/serd-0/serd)
