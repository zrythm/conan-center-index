cmake_minimum_required(VERSION 3.15)
project(zix LANGUAGES C)

add_library(zix-0)

target_sources(
  zix-0
  PRIVATE src/allocator.c
          src/btree.c
          src/bump_allocator.c
          src/digest.c
          src/errno_status.c
          src/filesystem.c
          src/hash.c
          src/path.c
          src/ring.c
          src/status.c
          src/string_view.c
          src/system.c
          src/tree.c
)

if(WIN32)
  target_sources(
    zix-0
    PRIVATE src/win32/environment_win32.c
          src/win32/filesystem_win32.c
          src/win32/sem_win32.c
          src/win32/system_win32.c
          src/win32/thread_win32.c
          src/win32/win32_util.c
  )
else()
  target_sources(
    zix-0
    PRIVATE src/posix/environment_posix.c
          src/posix/filesystem_posix.c
          src/posix/system_posix.c
          src/posix/thread_posix.c
  )
  if(APPLE)
    target_sources(zix-0 PRIVATE src/darwin/sem_darwin.c)
  else()
    target_sources(zix-0 PRIVATE src/posix/sem_posix.c)
  endif()
endif()

target_include_directories(
  zix-0
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_features(zix-0 PRIVATE c_std_99)

target_compile_definitions(zix-0 PRIVATE ZIX_INTERNAL)

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(zix-0 PUBLIC ZIX_STATIC)
endif()

if(WIN32)
  target_compile_definitions(
    zix-0
    PRIVATE UNICODE
            _UNICODE
            WINVER=0x0602
            _WIN32_WINNT=0x0602
            WIN32_LEAN_AND_MEAN
            NOMINMAX
            NOGDI
  )
elseif(APPLE)
  target_compile_definitions(zix-0 PRIVATE _DARWIN_C_SOURCE)
elseif(CMAKE_SYSTEM_NAME STREQUAL "FreeBSD")
  target_compile_definitions(zix-0 PRIVATE _BSD_SOURCE)
else()
  target_compile_definitions(
    zix-0
    PRIVATE _GNU_SOURCE
            _POSIX_C_SOURCE=200809L
            _XOPEN_SOURCE=600
  )
endif()

set_target_properties(zix-0 PROPERTIES C_VISIBILITY_PRESET hidden)

find_package(Threads REQUIRED)
target_link_libraries(zix-0 PRIVATE Threads::Threads)

include(GNUInstallDirs)
install(TARGETS zix-0)
install(DIRECTORY include/zix DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/zix-0)
