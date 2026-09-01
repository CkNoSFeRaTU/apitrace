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

#include "glidestate_tmu.hpp"

#include <algorithm>

namespace glidestate {

    GlideTMU::GlideTMU()
    : m_buffer(new GlideTMUBuffer(this)) {
    }

    GlideTMU::~GlideTMU() {
        delete m_buffer;
    }

    FxBool GlideTMU::InsertTexture(FxU32 startAddress, GlideTMUBuffer::Metadata metadata, int start, int end) {
        if (metadata.data == nullptr)
            return FXFALSE;

        GlideTMUBuffer::Address endAddress = m_buffer->Insert(startAddress, metadata, start, end);
        if (!endAddress)
            return FXFALSE;

        return FXTRUE;
    }

    const GlideTMUBuffer::TextureRegion* GlideTMU::GetTexture(FxU32 startAddress) {
        return m_buffer->Retrieve(startAddress);
    }

    FxBool GlideTMU::UpdateMetadata(FxU32 startAddress, GlideTMUBuffer::Metadata metadata) {
        return m_buffer->UpdateMetadata(startAddress, metadata);
    }

    void GlideTMU::SetCombinerState(GrTextureCombineFnc_t fnc) {
        switch (fnc)  {
            case GR_TEXTURECOMBINE_ZERO:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_ZERO;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_NONE;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_ZERO;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_NONE;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_DECAL:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_LOCAL;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_NONE;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_LOCAL;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_NONE;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_ONE:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_ZERO;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_NONE;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_ZERO;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_NONE;
                m_state.texCombine.rgbInvert = FXTRUE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_ADD:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_SCALE_OTHER_ADD_LOCAL;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_ONE;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_SCALE_OTHER_ADD_LOCAL;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_ONE;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_MULTIPLY:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_SCALE_OTHER;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_LOCAL;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_SCALE_OTHER;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_LOCAL;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_DETAIL:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_ONE_MINUS_DETAIL_FACTOR;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_ONE_MINUS_DETAIL_FACTOR;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_DETAIL_OTHER:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_DETAIL_FACTOR;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_DETAIL_FACTOR;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_TRILINEAR_ODD:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_ONE_MINUS_LOD_FRACTION;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_ONE_MINUS_LOD_FRACTION;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_TRILINEAR_EVEN:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_LOD_FRACTION;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_BLEND;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_LOD_FRACTION;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_SUBTRACT:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_SCALE_OTHER_MINUS_LOCAL;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_ONE;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_SCALE_OTHER_MINUS_LOCAL;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_ONE;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
            case GR_TEXTURECOMBINE_OTHER:
                m_state.texCombine.rgbFunction = GR_COMBINE_FUNCTION_SCALE_OTHER;
                m_state.texCombine.rgbFactor = GR_COMBINE_FACTOR_ONE;
                m_state.texCombine.alphaFunction = GR_COMBINE_FUNCTION_SCALE_OTHER;
                m_state.texCombine.alphaFactor = GR_COMBINE_FACTOR_ONE;
                m_state.texCombine.rgbInvert = FXFALSE;
                m_state.texCombine.alphaInvert = FXFALSE;
                break;
        }
    }

    FxBool GlideTMU::SetTable(GrTexTable_t type, void *data, int start, int stop) {
        switch (type) {
            case(GR_TEXTABLE_PALETTE): {
                start = std::clamp(start, 0, 255);
                stop = std::clamp(stop, 0, 255);
                if (start > stop)
                    return FXFALSE;

                if (start == 0 && stop == 0)
                    stop = 255;

                FxU32 length = stop - start;
                memcpy(m_palette.data() + start * sizeof(FxU32), data, length * sizeof(FxU32));
                return FXTRUE;
            }
            case(GR_TEXTABLE_NCC0): {
                start = std::clamp(start, 0, 111);
                stop = std::clamp(stop, 0, 111);

                if (start > stop)
                    return FXFALSE;

                if (start == 0 && stop == 0)
                    stop = 111;

                FxU32 length = stop - start;
                memcpy(m_ncc[0].data() + start, data, length);
                return FXTRUE;
            }
            case(GR_TEXTABLE_NCC1): {
                start = std::clamp(start, 0, 111);
                stop = std::clamp(stop, 0, 111);

                if (start > stop)
                    return FXFALSE;

                if (start == 0 && stop == 0)
                    stop = 111;

                FxU32 length = stop - start;
                memcpy(m_ncc[1].data() + start, data, length);
                return FXTRUE;
            }
        }

        return FXFALSE;
    }

}
