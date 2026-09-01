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

#include "image.hpp"
#include "state_writer.hpp"
#include "com_ptr.hpp"
#include "d3dcommon.hpp"
#include "d3dimports.hpp"
#include "d3dstate.hpp"

namespace d3dstate {

image::Image *
getRenderTargetImage(IDirect3DDevice *pDevice) {
    image::Image *image = nullptr;

    std::visit([&image](auto& surface) {
        using T = std::decay_t<decltype(surface)>;
        if constexpr (!std::is_same_v<T, std::monostate>) {
          image = getSurfaceImage(surface);
        }
    }, lastSetRenderTarget);

    return image;
}


void
dumpTextures(StateWriter &writer, IDirect3DDevice *pDevice)
{
    char label[128];
    int counter = 0;

    writer.beginMember("textures");
    writer.beginObject();

    IDirectDrawSurface *pLevel = nullptr;
    for (auto lastSetTexture : lastSetTextures) {
        HRESULT hr = E_INVALIDARG;
        std::visit([&hr, &pLevel](auto& texture) {
            using T = std::decay_t<decltype(texture)>;
            if constexpr (!std::is_same_v<T, std::monostate>) {
                hr = texture->QueryInterface(IID_IDirectDrawSurface4, (void **)&pLevel);
            }
        }, lastSetTexture);

        if (SUCCEEDED(hr) && pLevel) {
            DWORD Level = 0;
            while (pLevel) {
                image::Image *image = getSurfaceImage(pLevel);
                if (image) {
                    _snprintf(label, sizeof label, "EB_RESOURCE_%d_LEVEL_%lu", counter, Level);

                    writer.beginMember(label);
                    StateWriter::ImageDesc imgDesc;
                    imgDesc.depth = 1;
                    imgDesc.format = image->formatName;
                    writer.writeImage(image, imgDesc);
                    writer.endMember();
                    delete image;
                }

                // Get next mip level
                DDSCAPS capsMips = {};
                capsMips.dwCaps  = DDSCAPS_TEXTURE | DDSCAPS_MIPMAP;

                IDirectDrawSurface *pNext = nullptr;
                hr = pLevel->GetAttachedSurface(&capsMips, &pNext);

                pLevel->Release();

                if (FAILED(hr) || !pNext) {
                    break;
                }

                pLevel = pNext;
                Level++;
            }
        }

        counter++;
    }

    ddrawSurfaceDump(writer);

    writer.endObject();
    writer.endMember(); // textures
}

void
dumpFramebuffer(StateWriter &writer, IDirect3DDevice *pDevice)
{
    writer.beginMember("framebuffer");
    writer.beginObject();

    std::visit([pDevice, &writer](auto& surface) {
        using T = std::decay_t<decltype(surface)>;
        if constexpr (!std::is_same_v<T, std::monostate>) {
            image::Image *image = getSurfaceImage(surface);
            if (image) {
                writer.beginMember("RENDER_TARGET");
                StateWriter::ImageDesc imgDesc;
                imgDesc.depth = 1;
                imgDesc.format = image->formatName;
                writer.writeImage(image, imgDesc);
                writer.endMember(); // RENDER_TARGET
                delete image;
            }

            auto context = std::make_unique<struct CBContext<IDirect3DDevice>>(pDevice, &writer);
            surface->EnumAttachedSurfaces(context.get(), &EnumAttachedSurfacesCB);
        }
    }, lastSetRenderTarget);

    writer.endObject();
    writer.endMember(); // framebuffer
}


} /* namespace d3dstate */
