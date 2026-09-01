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

#pragma once

#include "glideimports.hpp"

#include <cstdint>
#include <map>
#include <vector>

namespace glidestate {

    class GlideTMU;

    class GlideTMUBuffer {
    public:
        GlideTMUBuffer(GlideTMU *parent);
        ~GlideTMUBuffer();

        using Address = FxU32;

        struct Metadata {
            GrLOD_t smallLodLog2;
            GrLOD_t largeLodLog2;
            GrAspectRatio_t aspectRatioLog2;
            GrIntFmt_t format;
            FxU32 evenOdd;
            FxU32 width;
            FxU32 height;
            void *data;

            FxU32 size;
            std::vector<GlideMipMapOffset> mipmaps;
        };

        struct TextureRegion {
            Address start;
            Address end;
            Metadata metadata;

            FxBool contains(Address offset) const {
                return start <= offset && offset < end;
            }
        };

        GlideTMUBuffer::Address Insert(Address startAddress, Metadata metadata, int start, int end);
        const TextureRegion* Retrieve(Address startAddress);
        FxBool UpdateMetadata(Address startAddress, Metadata metadata);

    private:
        FxBool Validate(Address startAddress, Address endAddress, Metadata* metadata) const;
        FxBool Erase(Address startAddress);
        std::size_t Size() const;
        FxBool Empty() const;
        void Clear();

        GlideTMU*                        m_parent;

        std::vector<uint8_t>             m_buffer;
        std::map<Address, TextureRegion> m_regions;
    };
}