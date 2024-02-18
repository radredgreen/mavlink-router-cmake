cmake_minimum_required(VERSION 3.4.3)

set(CMAKE_VERBOSE_MAKEFILE ON)

set(CMAKE_CXX_STANDARD 11)

# Set the project name
project(mavlink-router)

# Tell CMake where to look for header files
include_directories(${CMAKE_SOURCE_DIR}/)
include_directories( "modules/mavlink_c_library_v2/ardupilotmega"
    "src")

find_package( PkgConfig )

find_library( AIO_LIB libaio )
include_directories(${AIO_LIB_INCLUDE_DIRS})

# not working since the site=local method doesn't copy .git for some reason
execute_process (
	COMMAND bash -c "cat src/version.h.in | sed  s/@VCS_TAG@/`${CMAKE_SOURCE_DIR}/tools/meson-vcs-tag.sh ${CMAKE_SOURCE_DIR}`/g > src/git_version.h"
)
add_definitions(-DPACKAGE="mavlink-routerd")

# The source files are all the *.c files
file(GLOB MAVLINK_ROUTERD_SRC_FILES 
	"src/autolog.cpp"
	"src/binlog.cpp"
	"src/dedup.cpp"
	"src/endpoint.cpp"
	"src/git_version.cpp"
	"src/logendpoint.cpp"
	"src/main.cpp"
	"src/mainloop.cpp"
	"src/pollable.cpp"
	"src/timeout.cpp"
	"src/ulog.cpp"
	"src/tlog.cpp"
	"src/common/conf_file.cpp"
	"src/common/log.cpp"
	"src/common/util.cpp"
	"src/common/xtermios.cpp")


######################
# Target Executables #
######################

add_executable(mavlink-routerd ${MAVLINK_ROUTERD_SRC_FILES})

#########################
# Linking Configuration #
#########################


set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
set(THREADS_PREFER_PTHREAD_FLAG TRUE)
find_package (Threads)
target_link_libraries (mavlink-routerd Threads::Threads) 

find_package( Threads REQUIRED )
target_link_libraries( mavlink-routerd ${CMAKE_THREAD_LIBS_INIT} )
target_link_libraries( Threads::Threads )
target_link_libraries( mavlink-routerd rt )
target_link_libraries( mavlink-routerd m )
target_link_libraries( mavlink-routerd pthread )

# static link of stdc++ if available
if (STATICSTDCPP)
  include(CheckCXXCompilerFlag)
  CHECK_CXX_COMPILER_FLAG("-static-libgcc" CXX_SUPPORTS_STATIC_LIBGCC)
  if (CXX_SUPPORTS_STATIC_LIBGCC) 
    target_link_libraries (mavlink-routerd -static-libgcc)
  endif()    
  CHECK_CXX_COMPILER_FLAG("-static-libstdc++" CXX_SUPPORTS_STATIC_LIBSTDCPP)
  if (CXX_SUPPORTS_STATIC_LIBSTDCPP) 
    target_link_libraries (mavlink-routerd -static-libstdc++)
  endif()
endif()

set_property(TARGET mavlink-routerd PROPERTY C_STANDARD 99)

install(TARGETS mavlink-routerd DESTINATION bin)


