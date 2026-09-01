/**************************************************************************
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sub license,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.  IN NO EVENT SHALL
 * AUTHORS,
 * AND/OR THEIR SUPPLIERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
 * OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 **************************************************************************/


/*
 * Auxiliary functions to compute the size of array/blob arguments.
 */

#pragma once

#define TRANSLATE_ASPECT(_aspect) (_aspect)
#define TRANSLATE_LOD(_lod) (_lod)
#include "glidecommonsize.hpp"
#undef ASPECT_TRANSLATE

#include <string>
#include <fstream>

typedef FxU32 (__stdcall * PFN_GRGET)(FxU32 pname, FxU32 plength, FxI32 * params);
extern PFN_GRGET _grGet;
typedef FxU32 (__stdcall * PFN_GRTEXTEXTUREMEMREQUIRED)(FxU32 evenOdd, GrTexInfo* info);
extern PFN_GRTEXTEXTUREMEMREQUIRED _grTexTextureMemRequired;

static inline size_t
_getTexSizeAPI(GrLOD_t smallLodLog2, GrLOD_t largeLodLog2, GrAspectRatio_t aspectRatioLog2, GrTextureFormat_t format, FxU32 evenOdd = GR_MIPMAPLEVELMASK_BOTH) {
    GrTexInfo texInfo;
    texInfo.smallLodLog2 = smallLodLog2;
    texInfo.largeLodLog2 = largeLodLog2;
    texInfo.aspectRatioLog2 = aspectRatioLog2;
    texInfo.format = format;
    texInfo.data = nullptr;

    return _grTexTextureMemRequired(evenOdd, &texInfo);;
}

static inline size_t
_getVertexSize() {
    FxI32 size;
    _grGet(GR_GLIDE_VERTEXLAYOUT_SIZE, sizeof(size), &size);

    if (size < 0)
      return 0;

    return size;
}
