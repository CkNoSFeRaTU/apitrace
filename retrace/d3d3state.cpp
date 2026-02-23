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


#include <stdio.h>

#include <iostream>
#include <sstream>
#include <memory>

#include "state_writer.hpp"
#include "d3dimports.hpp"
#include "d3dstate.hpp"


namespace d3dstate {

static void
dumpViewport(StateWriter &writer, IDirect3DDevice *pDevice)
{
    char label[128];
    int counter = 0;

    // There are no API to retrieve current viewport in d3d3, so let's dump all viewports.
    IDirect3DViewport *vp1 = nullptr;
    HRESULT hr = pDevice->NextViewport(NULL, &vp1, D3DNEXT_HEAD);
    while (SUCCEEDED(hr) && vp1) {
        D3DVIEWPORT vp;
        ZeroMemory(&vp, sizeof(vp));
        vp.dwSize = sizeof(vp);
        hr = vp1->GetViewport(&vp);
        if (SUCCEEDED(hr)) {
            sprintf(label, "Viewport_%d", counter++);

            writer.beginMember(label);
            writer.beginObject();

            writer.writeIntMember("X", vp.dwX);
            writer.writeIntMember("Y", vp.dwY);
            writer.writeIntMember("Width", vp.dwWidth);
            writer.writeIntMember("Height", vp.dwHeight);
            writer.writeFloatMember("MinZ", vp.dvMinZ);
            writer.writeFloatMember("MaxZ", vp.dvMaxZ);

            writer.endObject();
            writer.endMember();

            IDirect3DViewport *vpNext = nullptr;
            hr = pDevice->NextViewport(vp1, &vpNext, D3DNEXT_NEXT);

            vp1->Release();
            vp1 = vpNext;
        }
    }

}

static void
dumpRenderstate(StateWriter &writer, IDirect3DDevice *pDevice)
{
    /*
     * TODO: There are no API for render and texture states retrieval in d3d3 and prior.
     * If we want to dump their states we have to intercept CreateExecuteBuffer
     * and parse command stream to save their states.
     */

    writer.beginMember("parameters");
    writer.beginObject();

    dumpViewport(writer, pDevice);

    writer.endObject();
    writer.endMember(); // parameters
}

void
dumpDevice(StateWriter &writer, IDirect3DDevice *pDevice)
{
    dumpRenderstate(writer, pDevice);

    writer.beginMember("shaders");
    writer.beginObject();
    writer.endObject();
    writer.endMember(); // shaders

    dumpTextures(writer, pDevice);

    dumpFramebuffer(writer, pDevice);
}


} /* namespace d3dstate */
