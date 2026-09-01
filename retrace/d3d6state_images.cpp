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
getRenderTargetImage(IDirect3DDevice3 *pDevice) {
    HRESULT hr;

    IDirectDrawSurface4 *pRenderTarget = nullptr;
    hr = pDevice->GetRenderTarget(&pRenderTarget);
    if (FAILED(hr)) {
        return NULL;
    }
    assert(pRenderTarget);

    return getSurfaceImage(pRenderTarget);
}


void
dumpTextures(StateWriter &writer, IDirect3DDevice3 *pDevice)
{
    char label[128];
    HRESULT hr;

    writer.beginMember("textures");
    writer.beginObject();

    for (DWORD Stage = 0; Stage < 8; ++Stage) {
        IDirect3DTexture2 *pTexture = nullptr;
        hr = pDevice->GetTexture(Stage, &pTexture);
        if (FAILED(hr) || !pTexture) {
            continue;
        }

        IDirectDrawSurface4 *pLevel = nullptr;
        hr = pTexture->QueryInterface(IID_IDirectDrawSurface4, (void **)&pLevel);
        if (FAILED(hr) || !pLevel) {
            pTexture->Release();
            continue;
        }

        DWORD Level = 0;
        while (pLevel) {
            image::Image *image = getSurfaceImage(pLevel);
            if (image) {
                _snprintf(label, sizeof label, "PS_RESOURCE_%lu_LEVEL_%lu", Stage, Level);

                writer.beginMember(label);
                StateWriter::ImageDesc imgDesc;
                imgDesc.depth = 1;
                imgDesc.format = image->formatName;
                writer.writeImage(image, imgDesc);
                writer.endMember();
                delete image;
            }

            // Get next mip level
            DDSCAPS2 capsMips = {};
            capsMips.dwCaps  = DDSCAPS_TEXTURE | DDSCAPS_MIPMAP;
            capsMips.dwCaps2 = 0;

            IDirectDrawSurface4 *pNext = nullptr;
            hr = pLevel->GetAttachedSurface(&capsMips, &pNext);

            pLevel->Release();

            if (FAILED(hr) || !pNext) {
                break;
            }

            pLevel = pNext;
            Level++;
        }
    }

    ddrawSurfaceDump(writer);

    writer.endObject();
    writer.endMember(); // textures
}

void
dumpFramebuffer(StateWriter &writer, IDirect3DDevice3 *pDevice)
{
    HRESULT hr;

    writer.beginMember("framebuffer");
    writer.beginObject();

    IDirectDrawSurface4 *pRenderTarget = nullptr;
    hr = pDevice->GetRenderTarget(&pRenderTarget);
    if (SUCCEEDED(hr) && pRenderTarget) {
        image::Image *image;
        image = getSurfaceImage(pRenderTarget);
        if (image) {
            writer.beginMember("RENDER_TARGET");
            StateWriter::ImageDesc imgDesc;
            imgDesc.depth = 1;
            imgDesc.format = image->formatName;
            writer.writeImage(image, imgDesc);
            writer.endMember(); // RENDER_TARGET
            delete image;
        }

        auto context = std::make_unique<struct CBContext<IDirect3DDevice3>>(pDevice, &writer);
        pRenderTarget->EnumAttachedSurfaces(context.get(), &EnumAttachedSurfacesCB);
    }

    writer.endObject();
    writer.endMember(); // framebuffer
}


} /* namespace d3dstate */
