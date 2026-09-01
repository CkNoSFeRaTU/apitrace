# - try to find Glide include directories and libraries
#
# Once done this will define:
#
#  Glide_XYZ_INCLUDE_FOUND - system has the include for the XYZ API
#  Glide_XYZ_INCLUDE_DIR   - include directory for the XYZ API
#
# Where XYZ can be any of:
#
#  2X
#  3X
#


include (CheckIncludeFileCXX)
include (FindPackageMessage)


if (WIN32)

    if (CMAKE_SIZEOF_VOID_P EQUAL 8)
        set (Glide_ARCHITECTURE x64)
    else ()
        set (Glide_ARCHITECTURE x86)
    endif ()

    # Can't use "$ENV{ProgramFiles(x86)}" to avoid violating CMP0053.  See
    # http://public.kitware.com/pipermail/cmake-developers/2014-October/023190.html
    set (ProgramFiles_x86 "ProgramFiles(x86)")
    if ("$ENV{${ProgramFiles_x86}}")
        set (ProgramFiles "$ENV{${ProgramFiles_x86}}")
    else ()
        set (ProgramFiles "$ENV{ProgramFiles}")
    endif ()

    find_path (Glide_ROOT_DIR
        glide2x/glide.h
        PATHS
            "$ENV{GLIDE_DIR}"
        DOC "Glide SDK root directory"
    )
    if (Glide_ROOT_DIR)
        set (Glide_INC_SEARCH_PATH "${Glide_ROOT_DIR}")
    endif ()

    # Find a header in the Glide SDK
    macro (find_glidesdk_header var_name header)
        set (include_dir_var "Glide_${var_name}_INCLUDE_DIR")
        set (include_found_var "Glide_${var_name}_INCLUDE_FOUND")
        find_path (${include_dir_var} ${header}
            HINTS ${Glide_INC_SEARCH_PATH}
            DOC "The directory where ${header} resides"
            CMAKE_FIND_ROOT_PATH_BOTH
        )
        if (${include_dir_var})
            set (${include_found_var} TRUE)
            find_package_message (${var_name}_INC "Found Glide${var_name} ${header} header: ${${include_dir_var}}/${header}" "[${${include_dir_var}}]")
        endif ()
        mark_as_advanced (${include_found_var})
    endmacro ()

    find_glidesdk_header  (1X     glide.h)
    find_glidesdk_header  (2X     glide.h)
    find_glidesdk_header  (3X     glide.h)

endif ()
