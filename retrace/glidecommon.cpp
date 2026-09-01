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

#include <algorithm>
#include <list>
#include <sstream>
#include <variant>
#include <unordered_map>

#include "image.hpp"
#include "state_writer.hpp"
#include "glidecommon.hpp"

namespace glidestate {

std::array<GlideTMU, GLIDE_NUM_TMU> TMUs = {};
GViewport glideViewport = {};

static std::unordered_map<FxU32, FxU32> renderStates = {
    {GLIDERS_DITHERMODE, 0},
};

FxU32
getRenderState(FxU32 state) {
    return renderStates[state];
}

void
setRenderState(FxU32 state, FxU32 value) {
    renderStates[state] = value;
}

bool dumpBufferInternal(StateWriter &writer, GrBuffer_t buffer, int width, int height, bool depth) {
    bool result = false;

    std::string label;
    switch (buffer) {
        case GR_BUFFER_FRONTBUFFER:
            label = "FRONTBUFFER";
            break;
        case GR_BUFFER_BACKBUFFER:
            label = "BACKBUFFER";
            break;
        case GR_BUFFER_AUXBUFFER:
            label = "AUXBUFFER";
            break;
        default:
            label = "UNKNOWN";
            break;
    }

    if (depth)
        label += "_DEPTH";

#if defined(GLIDE_USE_REGIONREAD_FOR_LINEARREAD)
    std::vector<uint8_t> data;
    // original voodoo graphics and rush have fixed stride (framebuffer organized as 1024*1024 regardless of resolution).
    // same for format - only RGB565, so use that for full compatibility.
    size_t stride = width * 2;
    data.resize(width * height * 2);
    if (_grLfbReadRegion(buffer, 0, 0, width, height, stride, data.data())) {
        image::Image *image = getImage(GR_FMT_RGB_565, data.data(), stride, width, height);
        if (image) {
            writer.beginMember(label);
            StateWriter::ImageDesc imgDesc;
            imgDesc.depth = 1;
            imgDesc.format = image->formatName;
            writer.writeImage(image, imgDesc);
            writer.endMember();
            delete image;
            result = true;
        }
    }
#else
#ifdef GLIDE1X
    std::vector<uint8_t> data;
//    grLfbOrigin(GR_ORIGIN_UPPER_LEFT);
    const uint8_t *ptr = (uint8_t*)_grLfbGetReadPtr(buffer);
    if (ptr) {
        constexpr FxU32 s_width = 1024;
        constexpr FxU32 s_height = 1024;
        constexpr FxU32 s_stride = s_width * 2;

        const FxU32 w = std::min(static_cast<FxU32>(width), s_width);
        const FxU32 h = std::min(static_cast<FxU32>(height), s_height);
        size_t stride = width * 2;
        data.resize(width * height * 2);

        _grLfbBegin();
        for (int y = 0; y < h; ++y) {
            memcpy(data.data() + y * stride, ptr + y * s_stride, w * 2);
        }
        _grLfbEnd();

        image::Image *image = getImage(GR_FMT_RGB_565, data.data(), stride, width, height);
        if (image) {
            writer.beginMember(label);
            StateWriter::ImageDesc imgDesc;
            imgDesc.depth = 1;
            imgDesc.format = image->formatName;
            writer.writeImage(image, imgDesc);
            writer.endMember();
            delete image;
            result = true;
        }
    }
#else
    // we want to dump in the format closest to the one which was upload
    GrLfbWriteMode_t writeMode = GR_LFBWRITEMODE_ANY;
    if (depth)
#if defined(GLIDE1X)
        writeMode = GR_LFBWRITEMODE_DEPTH_DEPTH;
#else
//        writeMode = GR_LFBWRITEMODE_565_DEPTH;
        writeMode = GR_LFBWRITEMODE_ZA16;
#endif

    GrLfbInfo_t info;
    info.size = sizeof(info);
    if (_grLfbLock(GR_LFB_READ_ONLY, buffer, writeMode, GR_ORIGIN_UPPER_LEFT, true, &info)) {
        GrIntFmt_t format = LfbWriteModeToIFormat(info.writeMode);
        image::Image *image = getImage(format, (unsigned char*)info.lfbPtr, info.strideInBytes, width, height);
        if (image) {
            writer.beginMember(label);
            StateWriter::ImageDesc imgDesc;
            imgDesc.depth = 1;
            imgDesc.format = image->formatName;
            writer.writeImage(image, imgDesc);
            writer.endMember();
            delete image;
            result = true;
        }

        _grLfbUnlock(GR_LFB_READ_ONLY, buffer);
    }
#endif
#endif

    return result;
}

static inline void YUV2RGB(int Y, int U, int V, uint8_t& r, uint8_t& g, uint8_t& b, bool use601) {
    int C = Y - 16;
    int D = U - 128;
    int E = V - 128;

    int Rt = (298 * C + (use601 ? 409 : 459) * E + 128) >> 8;
    int Gt = (298 * C - (use601 ? 100 : 55) * D - (use601 ? 208 : 136) * E + 128) >> 8;
    int Bt = (298 * C + (use601 ? 516 : 541) * D + 128) >> 8;

    r = std::clamp(Rt, 0, 255);
    g = std::clamp(Gt, 0, 255);
    b = std::clamp(Bt, 0, 255);
}

image::Image* getImage(GrIntFmt_t format, const void *srcPtr, FxU32 srcPitch, FxU32 width, FxU32 height, const std::array<FxU32, 256> *palette) {
    size_t numChannels;
    image::ChannelType channelType = image::TYPE_UNORM8;

    if (srcPtr == nullptr || srcPitch == 0)
        return nullptr;

    switch (format) {
        case GR_FMT_RGB_332:
        case GR_FMT_RGB_555:
        case GR_FMT_RGB_565:
        case GR_FMT_RGB_888:
        case GR_FMT_P_8:
        case GR_FMT_UYVY_422:
        case GR_FMT_YUYV_422:
            numChannels = 3;
            break;
        case GR_FMT_ARGB_1555:
        case GR_FMT_ARGB_4444:
        case GR_FMT_ARGB_8332:
        case GR_FMT_ARGB_8888:
        case GR_FMT_A_8:
        case GR_FMT_I_8:
        case GR_FMT_AI_44:
        case GR_FMT_AI_88:
        case GR_FMT_AP_88:
        case GR_FMT_ZA_16:
            numChannels = 4;
            break;
        case GR_FMT_RGB_555_DEPTH:
        case GR_FMT_RGB_565_DEPTH:
        case GR_FMT_ARGB_1555_DEPTH:
            numChannels = 3;
//            srcPitch = width * 4;
            break;
        case GR_FMT_ARGB_CMP_FXT1:
        case GR_FMT_ARGB_CMP_DXT1:
        case GR_FMT_ARGB_CMP_DXT2:
        case GR_FMT_ARGB_CMP_DXT3:
        case GR_FMT_ARGB_CMP_DXT4:
        case GR_FMT_ARGB_CMP_DXT5:
            //srcPitch = (width + (BlockWidth - 1) / BlockWidth) * (blockSize / 8);
        default:
//            std::cerr << "unsupported dumping format " << IFormatToString(format) << "\n";
            return nullptr;
    }

    image::Image *image = new image::Image(width, height, numChannels, true, channelType);
    if (!image) {
        return nullptr;
    }

    if ((format == GR_FMT_P_8 || format == GR_FMT_AP_88) && palette == nullptr) {
        std::cerr << "paletted format " << IFormatToString(format) << " without palette" << "\n";
        return nullptr;
    }

    const bool use601 = true;
    const uint8_t *src = (const uint8_t*)srcPtr;
    uint8_t *dst = image->start();
    for (uint32_t y = 0; y < height; ++y) {
        switch (format) {
            case GR_FMT_RGB_332:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = src[x];
                    dst[numChannels * x + 0] = ((pixel >> 5)       ) * 0xff / 0x07;
                    dst[numChannels * x + 1] = ((pixel >> 2) & 0x07) * 0xff / 0x07;
                    dst[numChannels * x + 2] = ( pixel       & 0x03) * 0xff / 0x03;
                }
                break;
            case GR_FMT_ARGB_8332:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = ((const uint16_t *)src)[x];
                    dst[numChannels * x + 0] = ((pixel >> 5) & 0x07) * 0xff / 0x07;
                    dst[numChannels * x + 1] = ((pixel >> 2) & 0x07) * 0xff / 0x07;
                    dst[numChannels * x + 2] = ( pixel       & 0x03) * 0xff / 0x03;
                    dst[numChannels * x + 3] = ((pixel >> 8) & 0xff);
                }
                break;
            case GR_FMT_RGB_555:
            case GR_FMT_RGB_555_DEPTH:
                for (uint32_t x = 0; x < width; x++) {
                    const uint32_t pixel = ((const uint16_t *)src)[x];
                    dst[numChannels * x + 0] = (( pixel >> 11        ) * (2*0xff) + 0x1f) / (2*0x1f);
                    dst[numChannels * x + 1] = (((pixel >>  5) & 0x1f) * (2*0xff) + 0x1f) / (2*0x1f);
                    dst[numChannels * x + 2] = (( pixel        & 0x1f) * (2*0xff) + 0x1f) / (2*0x1f);
                }
                break;
            case GR_FMT_RGB_565:
            case GR_FMT_RGB_565_DEPTH:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = ((const uint16_t *)src)[x];
                    dst[numChannels * x + 0] = (( pixel >> 11        ) * (2*0xff) + 0x1f) / (2*0x1f);
                    dst[numChannels * x + 1] = (((pixel >>  5) & 0x3f) * (2*0xff) + 0x3f) / (2*0x3f);
                    dst[numChannels * x + 2] = (( pixel        & 0x1f) * (2*0xff) + 0x1f) / (2*0x1f);
                }
                break;
            case GR_FMT_RGB_888:
                for (uint32_t x = 0; x < width; ++x) {
                    dst[numChannels * x + 0] = src[numChannels * x + 0];
                    dst[numChannels * x + 1] = src[numChannels * x + 1];
                    dst[numChannels * x + 2] = src[numChannels * x + 2];
                }
                break;
            case GR_FMT_ARGB_1555:
            case GR_FMT_ARGB_1555_DEPTH:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = ((const uint16_t *)src)[x];
                    dst[numChannels * x + 0] = (((pixel >> 10) & 0x1f) * (2*0xff) + 0x1f) / (2*0x1f);
                    dst[numChannels * x + 1] = (((pixel >>  5) & 0x1f) * (2*0xff) + 0x1f) / (2*0x1f);
                    dst[numChannels * x + 2] = (( pixel        & 0x1f) * (2*0xff) + 0x1f) / (2*0x1f);
                    dst[numChannels * x + 3] = (((pixel >> 15)       ) ? 0xff : 0x00);
                }
                break;
            case GR_FMT_ARGB_4444:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = ((const uint16_t *)src)[x];
                    dst[numChannels * x + 0] = ((pixel >> 12) & 0x0f) * 0x11;
                    dst[numChannels * x + 1] = ((pixel >> 8)  & 0x0f) * 0x11;
                    dst[numChannels * x + 2] = ((pixel >> 4 ) & 0x0f) * 0x11;
                    dst[numChannels * x + 3] = ( pixel        & 0x0f) * 0x11;
                }
                break;
            case GR_FMT_ARGB_8888:
                for (uint32_t x = 0; x < width; ++x) {
                    dst[numChannels * x + 0] = src[numChannels * x + 2];
                    dst[numChannels * x + 1] = src[numChannels * x + 1];
                    dst[numChannels * x + 2] = src[numChannels * x + 0];
                    dst[numChannels * x + 3] = src[numChannels * x + 3];
                }
                break;
            case GR_FMT_A_8:
                for (uint32_t x = 0; x < width; ++x) {
                    dst[numChannels * x + 0] = 0xff;
                    dst[numChannels * x + 1] = 0xff;
                    dst[numChannels * x + 2] = 0xff;
                    dst[numChannels * x + 3] = src[x];
                }
                break;
            case GR_FMT_I_8:
                for (uint32_t x = 0; x < width; ++x) {
                    dst[numChannels * x + 0] = src[x];
                    dst[numChannels * x + 1] = src[x];
                    dst[numChannels * x + 2] = src[x];
                    dst[numChannels * x + 3] = 0xff;
                }
                break;
            case GR_FMT_AI_44:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint8_t intensity = (src[x] & 0x0f) * 0x11;
                    dst[numChannels * x + 0] = intensity;
                    dst[numChannels * x + 1] = intensity;
                    dst[numChannels * x + 2] = intensity;
                    dst[numChannels * x + 3] = (src[x] >> 4 & 0x0f) * 0x11;
                }
                break;
            case GR_FMT_AI_88:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = ((const uint16_t *)src)[x];
                    const uint8_t intensity = pixel & 0xff;
                    dst[numChannels * x + 0] = intensity;
                    dst[numChannels * x + 1] = intensity;
                    dst[numChannels * x + 2] = intensity;
                    dst[numChannels * x + 3] = (pixel >> 8) & 0xff;
                }
                break;
            case GR_FMT_P_8:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = palette->at(src[x]);
                    dst[numChannels * x + 0] = (pixel >> 16) & 0xFF;
                    dst[numChannels * x + 1] = (pixel >> 8 ) & 0xFF;
                    dst[numChannels * x + 2] = (pixel      ) & 0xFF;
                }
                break;
            case GR_FMT_AP_88:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = palette->at(src[2*x + 0]);
                    dst[numChannels * x + 0] = (pixel >> 16) & 0xFF;
                    dst[numChannels * x + 1] = (pixel >> 8) & 0xFF;
                    dst[numChannels * x + 2] = (pixel >> 0) & 0xFF;
                    dst[numChannels * x + 3] = src[2*x + 1];
                }
                break;
            case GR_FMT_ZA_16:
                for (uint32_t x = 0; x < width; ++x) {
                    const uint32_t pixel = src[2*x];
                    dst[numChannels * x + 0] = pixel;// / 256;
                    dst[numChannels * x + 1] = pixel;// / 256;
                    dst[numChannels * x + 2] = pixel;// / 256;
                    dst[numChannels * x + 3] = src[2*x+1];
                }
                break;
            case GR_FMT_UYVY_422:
                for (uint32_t x = 0; x < width; x += 2) {
                    uint8_t r, g, b;
                    YUV2RGB(src[x * 2 + 1], src[x * 2], src[x * 2 + 2], r, g, b, use601);
                    dst[numChannels * x + 0] = r;
                    dst[numChannels * x + 1] = g;
                    dst[numChannels * x + 2] = b;

                    YUV2RGB(src[x * 2 + 3], src[x * 2], src[x * 2 + 2], r, g, b, use601);
                    dst[numChannels * x + 3] = r;
                    dst[numChannels * x + 4] = g;
                    dst[numChannels * x + 5] = b;
                }
                break;
            case GR_FMT_YUYV_422:
                for (uint32_t x = 0; x < width; x += 2) {
                    uint8_t r, g, b;
                    YUV2RGB(src[x * 2 + 0], src[x * 2 + 1], src[x * 2 + 3], r, g, b, use601);
                    dst[numChannels * x + 0] = r;
                    dst[numChannels * x + 1] = g;
                    dst[numChannels * x + 2] = b;

                    YUV2RGB(src[x * 2 + 2], src[x * 2 + 1], src[x * 2 + 3], r, g, b, use601);
                    dst[numChannels * x + 3] = r;
                    dst[numChannels * x + 4] = g;
                    dst[numChannels * x + 5] = b;
                }
                break;
            default:
                assert(0);
                break;
      }

      src+= srcPitch;
      dst+= image->stride();
    }

    image->formatName = IFormatToString(format);

    return image;
}

static inline
void dumpState(StateWriter &writer, const char *name, glidestate::GLIDERENDERSTATE state) {
    writer.writeStringMember(name, decodeRenderState(state, glidestate::getRenderState(state)).c_str());
}

static inline
void dumpStateTMU(StateWriter &writer, const char *name, glidestate::GLIDERENDERSTATE state, FxU32 value) {
    writer.writeStringMember(name, decodeRenderState(state, value).c_str());
}

void
dumpRenderstate(StateWriter &writer)
{
    char label[128];

    writer.beginMember("parameters");
    writer.beginObject();

    writer.writeIntMember("grAlphaTestReferenceValue", glidestate::getRenderState(glidestate::GLIDERS_ALPHATESTREFERENCEVALUE));
    writer.beginMember("grColorMask");
    writer.beginObject();
    writer.writeBoolMember("RGB", glidestate::getRenderState(glidestate::GLIDERS_COLORMASK_RGB));
    writer.writeBoolMember("Alpha", glidestate::getRenderState(glidestate::GLIDERS_COLORMASK_A));
    writer.endObject();
    writer.endMember();
    writer.writeIntMember("grConstantColorValue", glidestate::getRenderState(glidestate::GLIDERS_CONSTANTCOLORVALUE));
    dumpState(writer, "grChromakeyMode", glidestate::GLIDERS_CHROMAKEYMODE);
    writer.writeIntMember("grChromakeyValue", glidestate::getRenderState(glidestate::GLIDERS_CHROMAKEYVALUE));
    dumpState(writer, "grCullMode", glidestate::GLIDERS_CULLMODE);
    writer.writeIntMember("grGammaCorrectionValue", glidestate::getRenderState(glidestate::GLIDERS_GAMMACORRECTIONVALUE));
    dumpState(writer, "grDitherMode", glidestate::GLIDERS_DITHERMODE);
    dumpState(writer, "grDepthBufferMode", glidestate::GLIDERS_DEPTHBUFFERMODE);
    writer.writeIntMember("grDepthBiasLevel", glidestate::getRenderState(glidestate::GLIDERS_DEPTHBIASLEVEL));
    writer.writeBoolMember("grDepthMask", glidestate::getRenderState(glidestate::GLIDERS_DEPTHMASK));
    dumpState(writer, "grFogMode", glidestate::GLIDERS_FOGMODE);
    writer.writeIntMember("grFogColorValue", glidestate::getRenderState(glidestate::GLIDERS_FOGCOLORVALUE));

    for (int i = 0; i < GLIDE_NUM_TMU; i++) {
        const auto& state = glidestate::TMUs[i].m_state;

        snprintf(label, sizeof(label) - 1, "TMU%d", i);
        writer.beginMember(label);
        writer.beginObject();

        writer.beginMember("grTexClampMode");
        writer.beginObject();
        dumpStateTMU(writer, "s", glidestate::GLIDETS_TEXCLAMPMODE, state.texClampMode.s);
        dumpStateTMU(writer, "t", glidestate::GLIDETS_TEXCLAMPMODE, state.texClampMode.t);
        writer.endObject();
        writer.endMember();

        writer.beginMember("grTexCombine");
        writer.beginObject();
        dumpStateTMU(writer, "alphaFunction", glidestate::GLIDETS_TEXCOMBINEFUNCTION, state.texCombine.alphaFunction);
        dumpStateTMU(writer, "alphaFactor", glidestate::GLIDETS_TEXCOMBINEFACTOR, state.texCombine.alphaFactor);
        writer.writeBoolMember("alphaInvert", state.texCombine.alphaInvert);
        dumpStateTMU(writer, "rgbFunction", glidestate::GLIDETS_TEXCOMBINEFUNCTION, state.texCombine.rgbFunction);
        dumpStateTMU(writer, "rgbFactor", glidestate::GLIDETS_TEXCOMBINEFACTOR, state.texCombine.rgbFactor);
        writer.writeBoolMember("rgbInvert", state.texCombine.rgbInvert);
        writer.endObject();
        writer.endMember();

        writer.beginMember("grTexDetailControl");
        writer.beginObject();
        writer.writeIntMember("lodBias", state.texDetailControl.lodBias);
        writer.writeIntMember("scale", state.texDetailControl.scale);
        writer.writeFloatMember("max", state.texDetailControl.max);
        writer.endObject();
        writer.endMember();

        writer.writeFloatMember("grTexLodBiasValue", state.texLodBiasValue);

        writer.beginMember("grTexMipMapMode");
        writer.beginObject();
        dumpStateTMU(writer, "mode", glidestate::GLIDETS_TEXMIPMAPMODE, state.texMipMapMode.mode);
        writer.writeBoolMember("lodBlend", state.texMipMapMode.lodBlend);
        writer.endObject();
        writer.endMember();

        writer.beginMember("grTexFilterMode");
        writer.beginObject();
        dumpStateTMU(writer, "min", glidestate::GLIDETS_TEXFILTERMODE, state.texFilterMode.min);
        dumpStateTMU(writer, "mag", glidestate::GLIDETS_TEXFILTERMODE, state.texFilterMode.mag);
        writer.endObject();
        writer.endMember();

        writer.endObject();
        writer.endMember();

    }
    writer.beginMember("Viewport");
    writer.beginObject();
    writer.writeIntMember("X", glidestate::glideViewport.x);
    writer.writeIntMember("Y", glidestate::glideViewport.y);
    writer.writeIntMember("Width", glidestate::glideViewport.width);
    writer.writeIntMember("Height", glidestate::glideViewport.height);
    writer.endObject();
    writer.endMember();

    writer.endObject();
    writer.endMember(); // parameters
}

} /* namespace glidestate */
