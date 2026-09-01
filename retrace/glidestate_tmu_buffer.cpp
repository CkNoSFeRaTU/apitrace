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

#include "glidestate_tmu_buffer.hpp"

namespace glidestate {

    GlideTMUBuffer::GlideTMUBuffer(GlideTMU *parent)
    : m_parent(parent) {
    }

    GlideTMUBuffer::~GlideTMUBuffer() {
    }

    GlideTMUBuffer::Address GlideTMUBuffer::Insert(Address startAddress, Metadata metadata, int start, int end) {
        if (metadata.data == nullptr)
            return 0;

        metadata.size = _getITexSize(metadata.smallLodLog2, metadata.largeLodLog2, metadata.aspectRatioLog2, metadata.format, metadata.evenOdd, true, &metadata.mipmaps);

        Address endAddress = startAddress + metadata.size;
        if (endAddress >= m_buffer.size())
            m_buffer.resize(endAddress);

        auto it = m_regions.lower_bound(startAddress);

        if (it != m_regions.begin()) {
            auto prev = std::prev(it);

            if (prev->second.end > startAddress)
                it = prev;
        }

        while (it != m_regions.end() && it->second.start < endAddress) {
            it = m_regions.erase(it);
        }

        TextureRegion t;
        t.start = startAddress;
        t.end = endAddress;
        t.metadata = metadata;
        m_regions.emplace(startAddress, std::move(t));

        _getTexDimensions(metadata.smallLodLog2, metadata.largeLodLog2, metadata.aspectRatioLog2, metadata.width, metadata.height);

        if (end != 0 && start < end) {
            FxU32 blockSize;
            end = std::min(end, static_cast<int>(metadata.height));
            start = std::min(start, end);
            _getTexFormatSize(metadata.format, &blockSize);
            memcpy(m_buffer.data() + startAddress + start * metadata.width * (blockSize >> 3), metadata.data, (end - start) * metadata.width * (blockSize >> 3));
        } else {
            memcpy(m_buffer.data() + startAddress, metadata.data, metadata.size);
        }
        metadata.data = m_buffer.data() + startAddress;
        return endAddress;
    }

    const GlideTMUBuffer::TextureRegion* GlideTMUBuffer::Retrieve(Address startAddress) {
        auto it = m_regions.find(startAddress);

        if (it == m_regions.end())
            return nullptr;

        it->second.metadata.data = m_buffer.data() + startAddress;
        return &it->second;
    }

    FxBool GlideTMUBuffer::UpdateMetadata(Address startAddress, Metadata metadata) {
        auto it = m_regions.find(startAddress);

        if (it == m_regions.end())
            return FXFALSE;

        metadata.size = _getITexSize(metadata.smallLodLog2, metadata.largeLodLog2, metadata.aspectRatioLog2, metadata.format, metadata.evenOdd, true, &metadata.mipmaps);
        _getTexDimensions(metadata.smallLodLog2, metadata.largeLodLog2, metadata.aspectRatioLog2, metadata.width, metadata.height);
        it->second.metadata = metadata;

        return FXTRUE;
    }

    FxBool GlideTMUBuffer::Erase(Address startAddress) {
        return m_regions.erase(startAddress) != 0;
    }

    std::size_t GlideTMUBuffer::Size() const {
        return m_regions.size();
    }

    FxBool GlideTMUBuffer::Empty() const {
        return m_regions.empty();
    }

    void GlideTMUBuffer::Clear() {
        m_regions.clear();
    }
}