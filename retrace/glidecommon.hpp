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


#include "glideimports.hpp"

#include <array>
#include <string>
#include <vector>
#include <unordered_map>

#include "image.hpp"
#include "state_writer.hpp"
#include "glidestate_tmu.hpp"

#if defined(GLIDE1X)
typedef void (__stdcall * PFN_GRLFBBEGIN)(void);
typedef void (__stdcall * PFN_GRLFBEND)(void);
typedef const FxU32 * (__stdcall * PFN_GRLFBGETREADPTR)(FxI32 buffer);
extern PFN_GRLFBBEGIN _grLfbBegin;
extern PFN_GRLFBEND _grLfbEnd;
extern PFN_GRLFBGETREADPTR _grLfbGetReadPtr;
#else
typedef FxBool (__stdcall * PFN_GRLFBLOCK)(FxU32 type, FxI32 buffer, FxI32 writeMode, FxI32 origin, FxBool pixelPipeline, GrLfbInfo_t *info);
typedef FxBool (__stdcall * PFN_GRLFBUNLOCK)(FxU32 type, FxI32 buffer);
extern PFN_GRLFBLOCK _grLfbLock;
extern PFN_GRLFBUNLOCK _grLfbUnlock;
#endif
typedef FxBool (__stdcall * PFN_GRLFBREADREGION)(FxI32 src_buffer, FxU32 src_x, FxU32 src_y, FxU32 src_width, FxU32 src_height, FxU32 dst_stride, void * dst_data);
extern PFN_GRLFBREADREGION _grLfbReadRegion;

namespace glidestate {

struct GViewport {
    FxI32 x;
    FxI32 y;
    FxI32 width;
    FxI32 height;
};

enum GLIDERENDERSTATE : FxU32 {
    GLIDERS_ALPHATESTREFERENCEVALUE,
    GLIDERS_COLORMASK_RGB,
    GLIDERS_COLORMASK_A,
    GLIDERS_CONSTANTCOLORVALUE,
    GLIDERS_CHROMAKEYVALUE,
    GLIDERS_CHROMAKEYMODE,
    GLIDERS_CULLMODE,
    GLIDERS_GAMMACORRECTIONVALUE,
    GLIDERS_DITHERMODE,
    GLIDERS_DEPTHBIASLEVEL,
    GLIDERS_DEPTHBUFFERMODE,
    GLIDERS_DEPTHMASK,
    GLIDERS_FOGMODE,
    GLIDERS_FOGCOLORVALUE,

    //for TMU
    GLIDETS_TEXCLAMPMODE,
    GLIDETS_TEXCOMBINEFACTOR,
    GLIDETS_TEXCOMBINEFUNCTION,
    GLIDETS_TEXFILTERMODE,
    GLIDETS_TEXMIPMAPMODE,
};

FxU32
getRenderState(FxU32 state);

void
setRenderState(FxU32 state, FxU32 value);

image::Image*
getImage(GrIntFmt_t format, const void *srcPtr, FxU32 srcPitch, FxU32 width, FxU32 height, const std::array<FxU32, 256> *palette = nullptr);

bool
dumpBufferInternal(StateWriter &writer, GrBuffer_t buffer, int width, int height, bool depth = false);

extern GViewport glideViewport;
extern std::array<GlideTMU, GLIDE_NUM_TMU> TMUs;

extern std::string decodeRenderState(glidestate::GLIDERENDERSTATE state, FxU32 value);

void
dumpRenderstate(StateWriter &writer);

} /* namespace glidestate */
