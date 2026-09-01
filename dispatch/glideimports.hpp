/**************************************************************************
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 **************************************************************************/

/*
 * Central place for all DDraw/D3D includes, and respective OS dependent headers.
 */

#pragma once


#include <windows.h>

#include <glide.h>
#include <gsstdef.h>
#include <fxvid.h>
#if defined(GLIDE3X)
#ifdef GLIDE_NUM_TMU
#undef GLIDE_NUM_TMU
#endif
// technically in Glide3X it is variable and you supposed to query GR_FOG_TABLE_ENTRIES via grGet, but all released hardware still used 64.
#define GR_FOG_TABLE_SIZE 64
#define GLIDE_NUM_TMU 4
#include <tlib.h>
#include <g3ext.h>
#else
#define GR_FOG_TABLE_SIZE 64
#define SST_TEXTURE_ALIGN 0x10UL
#define SST_TEXTURE_ALIGN_MASK (SST_TEXTURE_ALIGN - 0x01UL)
#include <gmovie.h>
#include <gump.h>
#define GLIDE_NUM_TMU 2
#endif

// use grLfbReadRegion instead of grLfbLock.
// cons - it is inferiour in the way we don't know format, nor stride. also not all popular wrappers implement them for glide 2.00-2.11
// pros - can access even non-used buffers where grLock fail
// #define GLIDE_USE_REGIONREAD_FOR_LINEARREAD

#define SST1_TEXTURE_ALIGN_MASK 8
#define GR_MIPMAPLEVELMASK_NONE 0

#if defined(GLIDE1X)
#include "glide1xsize.hpp"
#elif defined(GLIDE2X)
#include "glide2xsize.hpp"
#elif defined(GLIDE3X)
#include "glide3xsize.hpp"
#endif
