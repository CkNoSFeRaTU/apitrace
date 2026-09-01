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


from dlltrace import DllTracer
from specs.glide2x import glide2x
from specs.stdapi import API

class Glide2xTracer(DllTracer):
    def implementWrapperInterfaceMethodBody(self, interface, base, method):
        DllTracer.implementWrapperInterfaceMethodBody(self, interface, base, method, resultOverride = resultOverride, callFlags = callFlags, afterCall = afterCall)

    def traceFunctionImplBody(self, function):
        callFlags = "trace::FLAG_NONE"

        print('if (!std::exchange(g_apiSet, true)) {');
        print('    const trace::FunctionSig glide_sig = {%s, "Glide2X", 0, nullptr};' % self.getFunctionSigId())
        print('    unsigned _callAPI = trace::localWriter.beginEnter(&glide_sig, trace::FLAG_FAKE);')
        print('    trace::localWriter.endEnter();')
        print('    trace::localWriter.beginLeave(_callAPI);')
        print('    trace::localWriter.endLeave();')
        print('}');

        if function.name == 'grBufferSwap':
            print(r'    trace::Flags callFlags = static_cast<trace::Flags>(trace::FLAG_END_FRAME|trace::FLAG_SWAP_RENDERTARGET);')
            callFlags = "callFlags"

        if function.name == 'grLfbUnlock':
            print(r'    trace::Flags callFlags = trace::FLAG_NONE;')
            print(r'    if (g_locks[buffer].size > 0) {')
            self.emit_memcpy('g_locks[buffer].ptr', 'g_locks[buffer].size')
            print(r'        if (buffer == GR_BUFFER_FRONTBUFFER)')
            print(r'            callFlags = trace::FLAG_END_FRAME;')
            print(r'        g_locks[buffer].ptr = nullptr;')
            print(r'        g_locks[buffer].size = 0;')
            print(r'    }')
            callFlags = "callFlags"

        if function.name == 'grLfbWriteRegion':
            print(r'    trace::Flags callFlags = trace::FLAG_NONE;')
            print(r'    if (dst_buffer == GR_BUFFER_FRONTBUFFER)')
            print(r'        callFlags = trace::FLAG_END_FRAME;')
            callFlags = "callFlags"

        if function.name == 'guTexDownloadMipMapLevel':
            print(r'    uintptr_t *_origPtr = nullptr;')
            print(r'    g_mappedSize = _getTexSizeGU(mmid);')
            print(r'    if (src != nullptr && g_mappedSize > 0) {')
            print(r'        _origPtr = (uintptr_t*)*src;')
            self.emit_malloc('_origPtr', 'g_mappedSize')
            self.emit_memcpy('_origPtr', 'g_mappedSize')
            print(r'    }')

        DllTracer.traceFunctionImplBody(self, function, callFlags = callFlags)

        if function.name == 'guTexDownloadMipMapLevel':
            print(r'    if (_origPtr != nullptr && g_mappedSize > 0) {')
            self.emit_free('_origPtr')
            print(r'         g_mappedSize = 0;')
            print(r'    }')

        if function.name == 'grLfbLock':
            print(r'    if (info != nullptr && type != GR_LFB_READ_ONLY) {')
            print(r'        g_locks[buffer] = {info->lfbPtr, info->strideInBytes * g_height};')
            print(r'    }')

        if function.name == 'grSstWinOpen':
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
            print(r'        case(GR_RESOLUTION_1024x768): g_width = 1024; g_height = 768; break;')
            print(r'        case(GR_RESOLUTION_1280x1024): g_width = 1280; g_height = 1024; break;')
            print(r'        case(GR_RESOLUTION_1600x1200): g_width = 1600; g_height = 1200; break;')
            print(r'        case(GR_RESOLUTION_400x300): g_width = 400; g_height = 300; break;')
            print(r'    }')

if __name__ == '__main__':
    print('#include "glideimports.hpp"')
    print('#include "trace_writer_local.hpp"')
    print('#include "os.hpp"')
    print()
    print('#include <unordered_map>')
    print('#include <utility>')

    print('struct lockData {')
    print('    void *ptr;')
    print('    size_t size;')
    print('};')
    print('size_t g_mappedSize = 0;')
    print('static std::unordered_map<GrBuffer_t, lockData> g_locks = {};')
    print('static int g_width = 640, g_height = 480;');
    print('bool g_apiSet = false;');

    api = API()
    api.addModule(glide2x)

    tracer = Glide2xTracer()
    tracer.traceApi(api)
