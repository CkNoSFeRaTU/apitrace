##########################################################################
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
##########################################################################/


"""GLide retracer generator."""


import re
import sys

from dllretrace import DllRetracer as Retracer
from specs.stdapi import API
from specs.glidecommon import *
from specs.glide1x import glide1x, HWND, GrFogMode_t

class GlideRetracer(Retracer):
    def retraceApi(self, api):
        print('// Swizzling mapping for lock addresses')
        print('struct {')
        print('    GrBuffer_t type;')
        print('    GrLfbWriteMode_t mode;')
        print('    void *ptr;')
        print('    size_t size;')
        print('} g_lock;')
        print('static HWND g_hWnd{0};')
        print('FxU32 g_width = 640, g_height = 480;');

        print()

        Retracer.retraceApi(self, api)

    def retraceFunctionBody(self, function):
        Retracer.retraceFunctionBody(self, function)

    def invokeFunction(self, function):
        if function.name == 'grSstOpen':
            print(r'    switch(screen_resolution) {')
            print(r'        case(GR_RESOLUTION_320x200): g_width = 320; g_height = 200; break;')
            print(r'        case(GR_RESOLUTION_320x240): g_width = 320; g_height = 240; break;')
            print(r'        case(GR_RESOLUTION_400x256): g_width = 400; g_height = 256; break;')
            print(r'        case(GR_RESOLUTION_512x384): g_width = 512; g_height = 384; break;')
            print(r'        case(GR_RESOLUTION_640x200): g_width = 640; g_height = 200; break;')
            print(r'        case(GR_RESOLUTION_640x350): g_width = 640; g_height = 350; break;')
            print(r'        case(GR_RESOLUTION_640x400): g_width = 640; g_height = 400; break;')
            print(r'        case(GR_RESOLUTION_640x480): g_width = 640; g_height = 480; break;')
            print(r'        case(GR_RESOLUTION_800x600): g_width = 800; g_height = 600; break;')
            print(r'        case(GR_RESOLUTION_960x720): g_width = 960; g_height = 720; break;')
            print(r'        case(GR_RESOLUTION_856x480): g_width = 856; g_height = 480; break;')
            print(r'        case(GR_RESOLUTION_512x256): g_width = 512; g_height = 256; break;')
            print(r'    }')
            print(r'    g_lock.type = GR_BUFFER_BACKBUFFER;')
            print(r'    g_lock.mode = GR_LFBWRITEMODE_565;')
            print(r'    g_lock.ptr = nullptr;')
            print(r'    g_lock.size = 0;')
            print(r'    g_hWnd = glideretrace::createWindow(g_hWnd, g_width, g_height, WS_POPUP | WS_VISIBLE, WS_EX_APPWINDOW);')
            print(r'    glidestate::glideViewport.x = 0;')
            print(r'    glidestate::glideViewport.y = 0;')
            print(r'    glidestate::glideViewport.width = g_width;')
            print(r'    glidestate::glideViewport.height = g_height;')

        if function.name == 'grLfbGetWritePtr':
            resultOverride = "_result"
            print(r'    _result = _grLfbGetWritePtr(buffer);')
            print(r'    if (g_lock.size == 0 && _result != nullptr) {')
            print(r'        if (g_lock.ptr != nullptr && g_lock.ptr != _result) {')
            print(r'        retrace::delRegionByPointer(g_lock.ptr);')
            print(r'        }')
            print(r'        g_lock.type = buffer;')
            print(r'        g_lock.ptr = _result;')
            print(r'        g_lock.size = 1024 * 1024 * 2;')
            print(r'        retrace::addRegion(call, (*call.ret).toUIntPtr(), g_lock.ptr, g_lock.size);')
            print(r'    }')

        Retracer.invokeFunction(self, function)

        if function.name == 'grLfbEnd':
            print(r'    if (g_lock.size > 0) {')
            print(r'        retrace::delRegionByPointer(g_lock.ptr);')
            print(r'        g_lock.ptr = nullptr;')
            print(r'        g_lock.size = 0;')
            print(r'    }')

        if function.name.startswith('grTexDownloadTable'):
            print(r'    if (data != nullptr && tmu >= 0 && tmu < GLIDE_NUM_TMU) {')
            if function.name == 'grTexDownloadTablePartial':
                print(r'        glidestate::TMUs[tmu].SetTable(type, data, start, end);')
            else:
                print(r'        glidestate::TMUs[tmu].SetTable(type, data);')
            print(r'    }')

        if function.name == 'grTexDownloadMipMap':
            print(r'    if (info->data != nullptr && tmu >= 0 && tmu < GLIDE_NUM_TMU) {')
            print(r'        glidestate::GlideTMUBuffer::Metadata m;')
            print(r'        m.smallLodLog2 = TRANSLATE_LOD(info->smallLod);')
            print(r'        m.largeLodLog2 = TRANSLATE_LOD(info->largeLod);')
            print(r'        m.aspectRatioLog2 = TRANSLATE_ASPECT(info->aspectRatio);')
            print(r'        m.format = TexFormatToIFormat(info->format);')
            print(r'        m.evenOdd = evenOdd;')
            print(r'        m.data = info->data;')
            print(r'        glidestate::TMUs[tmu].InsertTexture(startAddress, std::move(m));')
            print(r'    }')

        if function.name.startswith('grTexDownloadMipMapLevel'):
            print(r'    if (data != nullptr && tmu >= 0 && tmu < GLIDE_NUM_TMU) {')
            print(r'        glidestate::GlideTMUBuffer::Metadata m;')
            print(r'        m.smallLodLog2 = TRANSLATE_LOD(thisLod);')
            print(r'        m.largeLodLog2 = TRANSLATE_LOD(largeLod);')
            print(r'        m.aspectRatioLog2 = TRANSLATE_ASPECT(aspectRatio);')
            print(r'        m.format = TexFormatToIFormat(format);')
            print(r'        m.evenOdd = evenOdd;')
            print(r'        m.data = data;')
            if function.name == 'grTexDownloadMipMapLevelPartial':
                print(r'        glidestate::TMUs[tmu].InsertTexture(startAddress, std::move(m), start, end);')
            else:
                print(r'        glidestate::TMUs[tmu].InsertTexture(startAddress, std::move(m));')
            print(r'    }')

        if function.name == 'grTexSource':
            print(r'    if (info != nullptr && tmu >= 0 && tmu < GLIDE_NUM_TMU) {')
            print(r'        glidestate::GlideTMUBuffer::Metadata m;')
            print(r'        m.smallLodLog2 = TRANSLATE_LOD(info->smallLod);')
            print(r'        m.largeLodLog2 = TRANSLATE_LOD(info->largeLod);')
            print(r'        m.aspectRatioLog2 = TRANSLATE_ASPECT(info->aspectRatio);')
            print(r'        m.format = TexFormatToIFormat(info->format);')
            print(r'        m.evenOdd = evenOdd;')
            print(r'        glidestate::TMUs[tmu].UpdateMetadata(startAddress, std::move(m));')
            print(r'        glidestate::TMUs[tmu].SetLastTexture(startAddress);')
            print(r'    }')

        if function.name.startswith('guTexDownloadMipMap'):
            print(r'    if (src != nullptr) {')
            print(r'        GrMipMapInfo* mminfo = guTexGetMipMapInfo(mmid);')
            print(r'        glidestate::GlideTMUBuffer::Metadata m;')
            if function.name == 'grTexDownloadMipMapLevel':
                print(r'        m.smallLodLog2 = TRANSLATE_LOD(lod);')
            else:
                print(r'        m.smallLodLog2 = TRANSLATE_LOD(mminfo->lod_min);')
            print(r'        m.largeLodLog2 = TRANSLATE_LOD(mminfo->lod_max);')
            print(r'        m.aspectRatioLog2 = TRANSLATE_ASPECT(mminfo->aspect_ratio);')
            print(r'        m.format = TexFormatToIFormat(mminfo->format);')
            print(r'        m.evenOdd = mminfo->odd_even_mask;')
            print(r'        m.data = src;')
            print(r'        glidestate::TMUs[mminfo->tmu].InsertTexture(mminfo->tmu_base_address, std::move(m));')
            if function.name == 'guTexDownloadMipMap':
                print(r'        if (table != nullptr) {')
                print(r'            if (mminfo->format == GR_TEXFMT_YIQ_422)')
                print(r'                glidestate::TMUs[mminfo->tmu].SetTable(GR_TEXTABLE_NCC0, table);')
                print(r'            else if (mminfo->format == GR_TEXFMT_AYIQ_8422)')
                print(r'                glidestate::TMUs[mminfo->tmu].SetTable(GR_TEXTABLE_NCC1, table);')
                print(r'        }')
            print(r'    }')

        if function.name == 'guTexSource':
            print(r'    GrMipMapInfo* mminfo = guTexGetMipMapInfo(id);')
            print(r'    if (mminfo != nullptr && mminfo->tmu >= 0 && mminfo->tmu < GLIDE_NUM_TMU) {')
            print(r'        glidestate::TMUs[mminfo->tmu].SetLastTexture(mminfo->tmu_base_address);')
            print(r'    }')

        if function.name == 'grAlphaTestReferenceValue':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_ALPHATESTREFERENCEVALUE, value);')

        if function.name == 'grColorMask':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_COLORMASK_RGB, rgb);')
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_COLORMASK_A, a);')

        if function.name == 'grConstantColorValue':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_CONSTANTCOLORVALUE, value);')

        if function.name == 'grChromakeyMode':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_CHROMAKEYMODE, mode);')

        if function.name == 'grChromakeyValue':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_CHROMAKEYVALUE, value);')

        if function.name == 'grCullMode':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_CULLMODE, mode);')

        if function.name == 'grGammaCorrectionValue':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_GAMMACORRECTIONVALUE, value);')

        if function.name == 'grDepthBiasLevel':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_DEPTHBIASLEVEL, level);')

        if function.name == 'grDepthBufferMode':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_DEPTHBUFFERMODE, mode);')

        if function.name == 'grDepthMask':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_DEPTHMASK, mask);')

        if function.name == 'grDitherMode':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_DITHERMODE, mode);')

        if function.name == 'grFogMode"':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_FOGMODE, fog);')

        if function.name == 'grFogColorValue':
            print(r'    glidestate::setRenderState(glidestate::GLIDERS_FOGCOLORVALUE, fogcolor);')

        if function.name == 'grTexClampMode':
            print(r'    glidestate::TMUs[tmu].m_state.texClampMode.s = s_clampmode;')
            print(r'    glidestate::TMUs[tmu].m_state.texClampMode.t = t_clampmode;')

        if function.name == 'grTexCombine':
            print(r'    glidestate::TMUs[tmu].m_state.texCombine.rgbFunction = rgb_function;')
            print(r'    glidestate::TMUs[tmu].m_state.texCombine.rgbFactor = rgb_factor;')
            print(r'    glidestate::TMUs[tmu].m_state.texCombine.rgbInvert = rgb_invert;')
            print(r'    glidestate::TMUs[tmu].m_state.texCombine.alphaFunction = alpha_function;')
            print(r'    glidestate::TMUs[tmu].m_state.texCombine.alphaFactor = alpha_factor;')
            print(r'    glidestate::TMUs[tmu].m_state.texCombine.alphaInvert = alpha_invert;')

        if function.name == 'grTexCombineFunction' or function.name == 'guTexCombineFunction':
            print(r'    glidestate::TMUs[tmu].SetCombinerState(fnc);')

        if function.name == 'grTexDetailControl':
            print(r'    glidestate::TMUs[tmu].m_state.texDetailControl.lodBias = lod_bias;')
            print(r'    glidestate::TMUs[tmu].m_state.texDetailControl.scale = detail_scale;')
            print(r'    glidestate::TMUs[tmu].m_state.texDetailControl.max = detail_max;')

        if function.name == 'grTexFilterMode':
            print(r'    glidestate::TMUs[tmu].m_state.texFilterMode.mag = magfilter_mode;')
            print(r'    glidestate::TMUs[tmu].m_state.texFilterMode.min = minfilter_mode;')

        if function.name == 'grTexLodBiasValue':
            print(r'    glidestate::TMUs[tmu].m_state.texLodBiasValue = bias;')

        if function.name == 'grTexMipMapModel':
            print(r'    glidestate::TMUs[tmu].m_state.texMipMapMode.mode = mode;')
            print(r'    glidestate::TMUs[tmu].m_state.texMipMapMode.lodBlend = lod_blend;')

def dumpEnumSwitch(var, enum):
    print('        switch (%s) {' % var)
    for value in enum.values:
        print('            case %s:' % value)
        print('                return "%s";' % value)
    print('            default:')
    print('                return "TODO: enum";')
    print('}')
    print()

def main():
    print(r'#include "glideimports.hpp"')
    print(r'#include "glidecommon.hpp"')
    print()
    print(r'#include "glideretrace_misc.hpp"')
    print(r'#include "glide1xretrace.hpp"')
    print()
    print(r'#include <unordered_map>')

    print()
    print('''static glide1xretrace::GlideDumper glideDumper;''')
    print()

    api = API()

    api.addModule(glide1x)
    retracer = GlideRetracer()
    retracer.table_name = 'glide1xretrace::glide1x_callbacks'
    retracer.retraceApi(api)

    print('namespace glidestate {')
    print('std::string decodeRenderState(glidestate::GLIDERENDERSTATE state, FxU32 value) {')
    print('    switch(state) {')
    print('        case glidestate::GLIDERS_CHROMAKEYMODE:')
    dumpEnumSwitch('value', GrChromakeyMode_t)
    print('            break;')
    print('        case glidestate::GLIDERS_CULLMODE:')
    dumpEnumSwitch('value', GrCullMode_t)
    print('            break;')
    print('        case glidestate::GLIDERS_DEPTHBUFFERMODE:')
    dumpEnumSwitch('value', GrDepthBufferMode_t)
    print('            break;')
    print('        case glidestate::GLIDERS_DITHERMODE:')
    dumpEnumSwitch('value', GrDitherMode_t)
    print('            break;')
    print('        case glidestate::GLIDERS_FOGMODE:')
    dumpEnumSwitch('value', GrFogMode_t)
    print('            break;')
    print('        case glidestate::GLIDETS_TEXCLAMPMODE:')
    dumpEnumSwitch('value', GrTextureClampMode_t)
    print('            break;')
    print('        case glidestate::GLIDETS_TEXCOMBINEFACTOR:')
    dumpEnumSwitch('value', GrCombineFactor_t)
    print('            break;')
    print('        case glidestate::GLIDETS_TEXCOMBINEFUNCTION:')
    dumpEnumSwitch('value', GrTextureCombineFnc_t)
    print('            break;')
    print('        case glidestate::GLIDETS_TEXFILTERMODE:')
    dumpEnumSwitch('value', GrTextureFilterMode_t)
    print('            break;')
    print('        case glidestate::GLIDETS_TEXMIPMAPMODE:')
    dumpEnumSwitch('value', GrMipMapMode_t)
    print('            break;')
    print('    }')
    print('    return "TODO: decoder";')
    print('}')
    print('}')

if __name__ == '__main__':
    main()
