cmake_minimum_required(VERSION 3.15)
project(lilv LANGUAGES C)

add_library(lilv-0)

target_sources(
  lilv-0
  PRIVATE src/collections.c
          src/dylib.c
          src/instance.c
          src/lib.c
          src/load_skimmer.c
          src/node.c
          src/node_hash.c
          src/node_skimmer.c
          src/plugin.c
          src/pluginclass.c
          src/port.c
          src/query.c
          src/scalepoint.c
          src/state.c
          src/string_util.c
          src/syntax_skimmer.c
          src/sys_util.c
          src/type_skimmer.c
          src/ui.c
          src/uris.c
          src/world.c
)

find_package(lv2 CONFIG REQUIRED)
find_package(serd CONFIG REQUIRED)
find_package(sord CONFIG REQUIRED)
find_package(sratom CONFIG REQUIRED)
find_package(zix CONFIG REQUIRED)

target_include_directories(
  lilv-0
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_features(lilv-0 PRIVATE c_std_99)

target_compile_definitions(lilv-0 PRIVATE LILV_INTERNAL LILV_VERSION="0.28.0")

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(lilv-0 PUBLIC LILV_STATIC)
endif()

if(CMAKE_SYSTEM_NAME MATCHES "Linux|GNU")
  target_compile_definitions(lilv-0 PRIVATE _POSIX_C_SOURCE=200809L)
endif()

target_link_libraries(
  lilv-0
  PRIVATE lv2::lv2
          serd::serd
          sord::sord
          sratom::sratom
          zix::zix
)

if(UNIX)
  target_link_libraries(lilv-0 PRIVATE m ${CMAKE_DL_LIBS})
endif()

set_target_properties(lilv-0 PROPERTIES C_VISIBILITY_PRESET hidden)

include(GNUInstallDirs)
install(TARGETS lilv-0)
install(
  FILES include/lilv/lilv.h include/lilv/lilvmm.hpp
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/lilv-0/lilv
)
