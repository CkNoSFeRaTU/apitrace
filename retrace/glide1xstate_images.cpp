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
#include <stdint.h>

#include <list>
#include <vector>

#include "image.hpp"
#include "state_writer.hpp"
#include "glideimports.hpp"
#include "glidecommon.hpp"
#include "glide1xstate.hpp"

extern FxU32 g_width, g_height;

namespace glide1xstate {
using namespace glidestate;

void dumpBuffer(StateWriter &writer, GrBuffer_t buffer) {
    if (dumpBufferInternal(writer, buffer, g_width, g_height, false))
        dumpBufferInternal(writer, buffer, g_width, g_height, true);
}

image::Image *
getRenderTargetImage() {
    image::Image *image = nullptr;

    const uint8_t *ptr = (uint8_t*)_grLfbGetReadPtr(GR_BUFFER_FRONTBUFFER);
    if (ptr) {
        constexpr FxU32 s_width = 1024;
        constexpr FxU32 s_height = 1024;
        constexpr FxU32 s_stride = s_width * 2;

        const FxU32 w = std::min(g_width, s_width);
        const FxU32 h = std::min(g_height, s_height);
        size_t stride = g_width * 2;
        std::vector<uint8_t> data;
        data.resize(g_width * g_height * 2);

        _grLfbBegin();
        for (int y = 0; y < h; ++y) {
            memcpy(data.data() + y * stride, ptr + y * s_stride, w * 2);
        }
        _grLfbEnd();

        return getImage(GR_FMT_RGB_565, data.data(), stride, g_width, g_height);
    }

    return image;
}

void
dumpTextures(StateWriter &writer)
{
    char label[128];

    writer.beginMember("textures");
    writer.beginObject();

    size_t tmu = 0;
    for (auto& currentTMU : TMUs) {
        const GlideTMUBuffer::TextureRegion* t = currentTMU.GetLastTexture();
        if (t != nullptr) {
            FxU32 blockSize;
            _getTexFormatSize(t->metadata.format, &blockSize);
            blockSize >>= 3;
            size_t count = 0;
            for (const auto& mipmap : t->metadata.mipmaps) {
                const void* ptr = static_cast<uint8_t*>(t->metadata.data) + mipmap.offset;
                image::Image *image = getImage(t->metadata.format, ptr, mipmap.width * blockSize, mipmap.width, mipmap.height, currentTMU.GetPalette());
                if (image) {
                    _snprintf(label, sizeof label, "TMU_%lu_%lu", tmu, count);
                    writer.beginMember(label);
                    StateWriter::ImageDesc imgDesc;
                    imgDesc.depth = 1;
                    imgDesc.format = image->formatName;
                    writer.writeImage(image, imgDesc);
                    writer.endMember();
                    delete image;
                }

                count++;
            }
        }

        tmu++;
    }

    writer.endObject();
    writer.endMember(); // textures
}

} /* namespace glide1xstate */
