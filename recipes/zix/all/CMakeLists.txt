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

find_package(Threads REQUIRED)
target_link_libraries(zix-0 PRIVATE Threads::Threads)

# Feature probes: the library is built with ZIX_NO_DEFAULT_CONFIG plus an
# explicit HAVE_* define for every system feature that compiles and links
# here, instead of the compile-time assumptions in zix_config.h
include(CheckCSourceCompiles)

set(ZIX_SYSTEM_DEFINES)
if(CMAKE_SYSTEM_NAME MATCHES "Linux|GNU")
  set(ZIX_SYSTEM_DEFINES _GNU_SOURCE _POSIX_C_SOURCE=200809L _XOPEN_SOURCE=600)
elseif(APPLE)
  set(ZIX_SYSTEM_DEFINES _DARWIN_C_SOURCE)
elseif(CMAKE_SYSTEM_NAME STREQUAL "FreeBSD")
  set(ZIX_SYSTEM_DEFINES _BSD_SOURCE)
elseif(WIN32)
  set(
    ZIX_SYSTEM_DEFINES
    UNICODE
    _UNICODE
    WINVER=0x0602
    _WIN32_WINNT=0x0602
    WIN32_LEAN_AND_MEAN
    NOMINMAX
    NOGDI
  )
endif()

foreach(zix_define IN LISTS ZIX_SYSTEM_DEFINES)
  list(APPEND CMAKE_REQUIRED_DEFINITIONS "-D${zix_define}")
endforeach()
if(UNIX)
  set(CMAKE_REQUIRED_LIBRARIES "${CMAKE_THREAD_LIBS_INIT}")
endif()

function(zix_check_feature name code)
  check_c_source_compiles("${code}" "ZIX_HAVE_${name}")
  if(ZIX_HAVE_${name})
    target_compile_definitions(zix-0 PRIVATE "HAVE_${name}=1")
  endif()
endfunction()

if(WIN32)
  zix_check_feature(
    sopen_s
    [[#include <io.h>
    int main(void) { int fd; return (int)_sopen_s(&fd, "/", 0, 0, 0644); }]]
  )
  if(NOT MINGW)
    zix_check_feature(
      CreateFile2
      [[#include <windows.h>
      int main(void) {
        CREATEFILE2_EXTENDED_PARAMETERS p = {0};
        return CreateFile2(NULL, FILE_READ_ATTRIBUTES, 0U, OPEN_EXISTING, &p);
      }]]
    )
  endif()
  zix_check_feature(
    CreateHardLink
    [[#include <windows.h>
    int main(void) { return CreateHardLink(TEXT("l"), TEXT("t"), NULL); }]]
  )
  if(NOT MINGW)
    zix_check_feature(
      CreateSymbolicLink
      [[#include <windows.h>
      int main(void) {
        return CreateSymbolicLink(TEXT("l"), TEXT("t"),
                                   SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE);
      }]]
    )
  endif()
  zix_check_feature(
    GetFinalPathNameByHandle
    [[#include <windows.h>
    int main(void) { return GetFinalPathNameByHandle(NULL, NULL, 0U, 0U); }]]
  )
  zix_check_feature(
    VirtualLock
    [[#include <windows.h>
    int main(void) { return VirtualLock(NULL, sizeof(void*)); }]]
  )
else()
  zix_check_feature(
    clock_gettime
    [[#include <time.h>
    int main(void) {
      struct timespec t;
      return clock_gettime(CLOCK_MONOTONIC, &t);
    }]]
  )
  zix_check_feature(
    copy_file_range
    [[#include <unistd.h>
    int main(void) { return copy_file_range(0, NULL, 1, NULL, 0U, 0U); }]]
  )
  zix_check_feature(
    fileno
    [[#include <stdio.h>
    int main(void) { return fileno(stdin); }]]
  )
  zix_check_feature(
    flock
    [[#include <sys/file.h>
    int main(void) { return flock(0, 0); }]]
  )
  zix_check_feature(
    lstat
    [[#include <sys/stat.h>
    int main(void) {
      struct stat s;
      return lstat("/", &s);
    }]]
  )
  zix_check_feature(
    mlock
    [[#include <sys/mman.h>
    int main(void) { return mlock(0, 0); }]]
  )
  zix_check_feature(
    pathconf
    [[#include <unistd.h>
    int main(void) { return pathconf("/", _PC_PATH_MAX) > 0L; }]]
  )
  zix_check_feature(
    posix_fadvise
    [[#include <fcntl.h>
    int main(void) {
      return posix_fadvise(0, 0, 4096, POSIX_FADV_SEQUENTIAL);
    }]]
  )
  zix_check_feature(
    posix_memalign
    [[#include <stdlib.h>
    int main(void) {
      void* mem = NULL;
      return posix_memalign(&mem, 8U, 8U);
    }]]
  )
  zix_check_feature(
    realpath
    [[#include <stdlib.h>
    int main(void) { return realpath("/", NULL) != NULL; }]]
  )
  zix_check_feature(
    sysconf
    [[#include <unistd.h>
    int main(void) { return sysconf(_SC_PAGE_SIZE) > 0L; }]]
  )
  if(APPLE)
    zix_check_feature(
      clonefile
      [[#include <sys/clonefile.h>
      int main(void) { return clonefile("/src", "/dst", 0); }]]
    )
  else()
    zix_check_feature(
      sem_timedwait
      [[#include <semaphore.h>
      #include <time.h>
      int main(void) {
        sem_t s;
        struct timespec t;
        return sem_timedwait(&s, &t);
      }]]
    )
  endif()
endif()

target_compile_definitions(zix-0 PRIVATE ZIX_NO_DEFAULT_CONFIG ${ZIX_SYSTEM_DEFINES})

set_target_properties(zix-0 PROPERTIES C_VISIBILITY_PRESET hidden)

include(GNUInstallDirs)
install(TARGETS zix-0)
install(DIRECTORY include/zix DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/zix-0)
