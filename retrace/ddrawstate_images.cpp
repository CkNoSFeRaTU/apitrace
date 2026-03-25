/**************************************************************************
 *
 * Copyright 2015 VMware, Inc.
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


#include <assert.h>
#include <initguid.h>
#include <stdint.h>

#include <list>

#include "image.hpp"
#include "state_writer.hpp"
#include "d3dcommon.hpp"
#include "d3dimports.hpp"
#include "d3dstate.hpp"

namespace d3dstate {

image::Image *
getRenderTargetImage(IDirectDraw *pDevice) {
    return nullptr;
}

image::Image *
getRenderTargetImage(IDirectDraw2 *pDevice) {
    return nullptr;
}

image::Image *
getRenderTargetImage(IDirectDraw4 *pDevice) {
    return nullptr;
}

image::Image *
getRenderTargetImage(IDirectDraw7 *pDevice) {
    return nullptr;
}

void
ddrawSurfaceDump(StateWriter &writer) {
    std::visit([&writer](auto& surf) {
        HRESULT hr = E_INVALIDARG;

        char label[128];

        using S = std::decay_t<decltype(surf)>;
        if constexpr (!std::is_same_v<S, std::monostate>) {
            S pLevel = surf;
            surf->AddRef();
            DWORD Level = 0;
            while (pLevel) {
                image::Image *image = getSurfaceImage(pLevel);
                if (image) {
                    _snprintf(label, sizeof label, "DDRAW_LEVEL_%lu", Level);

                    writer.beginMember(label);
                    StateWriter::ImageDesc imgDesc;
                    imgDesc.depth = 1;
                    imgDesc.format = image->formatName;
                    writer.writeImage(image, imgDesc);
                    writer.endMember();
                    delete image;
                }

                // Get next mip level
                using DT = std::conditional_t<std::is_same_v<S, IDirectDrawSurface7*>, DDSCAPS2,
                    std::conditional_t<std::is_same_v<S, IDirectDrawSurface4*>,
                        DDSCAPS2, DDSCAPS
                    >
                >;

                DT capsMips = {};
                capsMips.dwCaps  = DDSCAPS_TEXTURE | DDSCAPS_MIPMAP;

                S pNext = nullptr;
                hr = pLevel->GetAttachedSurface(&capsMips, &pNext);

                pLevel->Release();

                if (FAILED(hr) || !pNext) {
                    break;
                }

                pLevel = pNext;
                Level++;
            }
        }
    }, lastSetSurface);
}

void
dumpTextures(StateWriter &writer)
{
    writer.beginMember("textures");
    writer.beginObject();

    ddrawSurfaceDump(writer);

    writer.endObject();
    writer.endMember(); // textures
}

} /* namespace d3dstate */
