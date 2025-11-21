/**************************************************************************
 *
 * Copyright 2012 VMware, Inc.
 * All Rights Reserved.
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

#include "winsdk_compat.h"

#include <ddraw.h>
#include <d3d.h>


#ifndef DDBLT_EXTENDED_FLAGS
#define DDBLT_EXTENDED_FLAGS 0x40000000l
#endif

#ifndef DDBLT_EXTENDED_LINEAR_CONTENT
#define DDBLT_EXTENDED_LINEAR_CONTENT 0x00000004l
#endif

#ifndef D3DLIGHT_PARALLELPOINT
#define D3DLIGHT_PARALLELPOINT (D3DLIGHTTYPE)4
#endif

#ifndef D3DLIGHT_GLSPOT
#define D3DLIGHT_GLSPOT (D3DLIGHTTYPE)5
#endif

#ifndef DDENUMOVERLAYZ_BACKTOFRONT
#define DDENUMOVERLAYZ_BACKTOFRONT 0x00000000l
#endif

#ifndef DDENUMOVERLAYZ_FRONTTOBACK
#define DDENUMOVERLAYZ_FRONTTOBACK 0x00000001l
#endif

#ifndef DDOVERZ_SENDTOFRONT
#define DDOVERZ_SENDTOFRONT 0x00000000l
#endif

#ifndef DDOVERZ_SENDTOBACK
#define DDOVERZ_SENDTOBACK 0x00000001l
#endif

#ifndef DDOVERZ_MOVEFORWARD
#define DDOVERZ_MOVEFORWARD 0x00000002l
#endif

#ifndef DDOVERZ_MOVEBACKWARD
#define DDOVERZ_MOVEBACKWARD 0x00000003l
#endif

#ifndef DDOVERZ_INSERTINFRONTOF
#define DDOVERZ_INSERTINFRONTOF 0x00000004l
#endif

#ifndef DDOVERZ_INSERTINBACKOF
#define DDOVERZ_INSERTINBACKOF 0x00000005l
#endif

#ifndef DDSGR_CALIBRATE
#define DDSGR_CALIBRATE 0x00000001L
#endif

#ifndef DDSMT_ISTESTREQUIRED
#define DDSMT_ISTESTREQUIRED 0x00000001L
#endif

#ifndef DDEM_MODEPASSED
#define DDEM_MODEPASSED 0x00000001L
#endif

#ifndef DDEM_MODEFAILED
#define DDEM_MODEFAILED 0x00000002L
#endif

#ifdef DDSCAPS_RESERVED3
#undef DDSCAPS_PRIMARYSURFACELEFT
#define DDSCAPS_PRIMARYSURFACELEFT DDSCAPS_RESERVED3
#endif

#ifdef DDSCAPS2_RESERVED4
#undef DDSCAPS2_HARDWAREDEINTERLACE
#define DDSCAPS2_HARDWAREDEINTERLACE DDSCAPS2_RESERVED4
#endif

#ifndef D3DRENDERSTATE_OLDALPHABLENDENABLE
#define D3DRENDERSTATE_OLDALPHABLENDENABLE (D3DRENDERSTATETYPE)42
#endif

#undef DDPCAPS_INITIALIZE
#define DDPCAPS_INITIALIZE 0x08
