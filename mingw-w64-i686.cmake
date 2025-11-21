# cmake -B build -DCMAKE_TOOLCHAIN_FILE=mingw-w64-i686.cmake ..

set(CMAKE_SYSTEM_NAME Windows)
set(TOOLCHAIN_PREFIX i686-w64-mingw32)

# cross compilers to use for C, C++ and Fortran
set(CMAKE_C_COMPILER ${TOOLCHAIN_PREFIX}-gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PREFIX}-g++)
set(CMAKE_Fortran_COMPILER ${TOOLCHAIN_PREFIX}-gfortran)
set(CMAKE_RC_COMPILER ${TOOLCHAIN_PREFIX}-windres)

# target environment on the build host system
set(CMAKE_FIND_ROOT_PATH /usr/${TOOLCHAIN_PREFIX})

# modify default behavior of FIND_XXX() commands
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# ccache
set(CMAKE_C_COMPILER_LAUNCHER ccache)
set(CMAKE_CXX_COMPILER_LAUNCHER ccache)

# misc flags
set(CMAKE_CXX_FLAGS "-Wno-address -Wno-stringop-truncation -Wno-unused-variable -Wno-unused-but-set-variable")
