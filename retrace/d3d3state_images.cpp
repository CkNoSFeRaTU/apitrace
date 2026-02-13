/**************************************************************************
 *
 * Copyright 2015 VMware, Inc.
 * All Rights Reserved.
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
    /*
     * TODO: there are no API to retrieve render target in d3d3 and prior.
     * There your "render target" is the surface you create d3d device from.
     * So we have to intercept d3d device creation via QueryInterface and save surface pointer.
     */

    return nullptr;
}


void
dumpTextures(StateWriter &writer, IDirect3DDevice *pDevice)
{
    writer.beginMember("textures");
    writer.beginObject();

    /*
     * TODO: everything in d3d3 and prior is done via execute buffer.
     * So if we want to dump textures we have to intercept and parse it's command stream.
     */

    writer.endObject();
    writer.endMember(); // textures
}

void
dumpFramebuffer(StateWriter &writer, IDirect3DDevice *pDevice)
{
    writer.beginMember("framebuffer");
    writer.beginObject();

    writer.endObject();
    writer.endMember(); // framebuffer
}


} /* namespace d3dstate */
