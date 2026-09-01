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
#include "glidestate_tmu_buffer.hpp"

#include <array>
#include <unordered_map>

namespace glidestate {
    class GlideTMU final {
    public:
        GlideTMU();
        ~GlideTMU();

        FxBool InsertTexture(FxU32 startAddress, GlideTMUBuffer::Metadata, int start = 0, int end = 0);

        const GlideTMUBuffer::TextureRegion* GetTexture(FxU32 startAddress);

        FxBool UpdateMetadata(FxU32 startAddress, GlideTMUBuffer::Metadata);

        FxBool SetTable(GrTexTable_t type, void *data, int start = 0, int stop = 0);

        const std::array<FxU32, 256>* GetPalette() const {
            return &m_palette;
        }

        const std::array<FxU32, 112>* GetNCC(bool first) const {
            if (first)
                return &m_ncc[0];
            else
                return &m_ncc[1];
        }

        void SetCombinerState(GrTextureCombineFnc_t fnc);

        void SetLastTexture(FxU32 startAddress) {
           m_lastTexture = startAddress;
        }

        const GlideTMUBuffer::TextureRegion* GetLastTexture() {
           return GetTexture(m_lastTexture);
        }

        struct {
            struct {
                FxU32 rgb;
                FxU32 a;
            } colorMask;
            struct {
                FxU32 alphaFunction;
                FxU32 alphaFactor;
                FxU32 alphaInvert;
                FxU32 rgbFunction;
                FxU32 rgbFactor;
                FxU32 rgbInvert;
            } texCombine;
            struct {
                FxU32 lodBias;
                FxU32 scale;
                float max;
            } texDetailControl;
            struct {
                FxU32 min;
                FxU32 mag;
            } texFilterMode;
            struct {
                FxU32 mode;
                FxU32 lodBlend;
            } texMipMapMode;
            struct {
              FxU32 s;
              FxU32 t;
            } texClampMode;
            float texLodBiasValue;
        } m_state;

    private:
        GlideTMUBuffer* m_buffer;

        FxI32 m_lastTexture = -1;
        std::array<FxU32, 256> m_palette = { };
        std::array<std::array<FxU32, 112>, 2> m_ncc = { };
    };
}
