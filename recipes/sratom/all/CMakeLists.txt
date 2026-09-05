cmake_minimum_required(VERSION 3.15)
project(sratom LANGUAGES C)

add_library(sratom-0)

target_sources(sratom-0 PRIVATE src/sratom.c)

find_package(lv2 CONFIG REQUIRED)
find_package(serd CONFIG REQUIRED)
find_package(sord CONFIG REQUIRED)

target_include_directories(
  sratom-0
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_features(sratom-0 PRIVATE c_std_99)

target_compile_definitions(sratom-0 PRIVATE SRATOM_INTERNAL)

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(sratom-0 PUBLIC SRATOM_STATIC)
endif()

target_link_libraries(sratom-0 PRIVATE lv2::lv2 serd::serd sord::sord)

if(UNIX)
  target_link_libraries(sratom-0 PRIVATE m)
endif()

set_target_properties(sratom-0 PROPERTIES C_VISIBILITY_PRESET hidden)

include(GNUInstallDirs)
install(TARGETS sratom-0)
install(FILES include/sratom/sratom.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/sratom-0/sratom)
