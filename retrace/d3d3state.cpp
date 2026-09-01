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


#include <stdio.h>

#include <iostream>
#include <sstream>
#include <memory>

#include "state_writer.hpp"
#include "d3dimports.hpp"
#include "d3dcommon.hpp"
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
#define _DUMP_RS(x) { \
    DWORD rsDword = getRenderState(x); \
    writeRenderState(writer, #x, rsDword); \
}

    writer.beginMember("parameters");
    writer.beginObject();

    _DUMP_RS(D3DRENDERSTATE_ANTIALIAS);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREPERSPECTIVE);
    _DUMP_RS(D3DRENDERSTATE_ZENABLE);
    _DUMP_RS(D3DRENDERSTATE_FILLMODE);
    _DUMP_RS(D3DRENDERSTATE_SHADEMODE);
    _DUMP_RS(D3DRENDERSTATE_LINEPATTERN);
    _DUMP_RS(D3DRENDERSTATE_ZWRITEENABLE);
    _DUMP_RS(D3DRENDERSTATE_ALPHATESTENABLE);
    _DUMP_RS(D3DRENDERSTATE_LASTPIXEL);
    _DUMP_RS(D3DRENDERSTATE_SRCBLEND);
    _DUMP_RS(D3DRENDERSTATE_DESTBLEND);
    _DUMP_RS(D3DRENDERSTATE_CULLMODE);
    _DUMP_RS(D3DRENDERSTATE_ZFUNC);
    _DUMP_RS(D3DRENDERSTATE_ALPHAREF);
    _DUMP_RS(D3DRENDERSTATE_ALPHAFUNC);
    _DUMP_RS(D3DRENDERSTATE_DITHERENABLE);
    _DUMP_RS(D3DRENDERSTATE_ALPHABLENDENABLE);
    _DUMP_RS(D3DRENDERSTATE_FOGENABLE);
    _DUMP_RS(D3DRENDERSTATE_SPECULARENABLE);
    _DUMP_RS(D3DRENDERSTATE_ZVISIBLE);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEDALPHA);
    _DUMP_RS(D3DRENDERSTATE_FOGCOLOR);
    _DUMP_RS(D3DRENDERSTATE_FOGTABLEMODE);
    _DUMP_RS(D3DRENDERSTATE_FOGSTART);
    _DUMP_RS(D3DRENDERSTATE_FOGEND);
    _DUMP_RS(D3DRENDERSTATE_FOGDENSITY);
    _DUMP_RS(D3DRENDERSTATE_WRAP0);
    _DUMP_RS(D3DRENDERSTATE_WRAP1);
    _DUMP_RS(D3DRENDERSTATE_WRAP2);
    _DUMP_RS(D3DRENDERSTATE_WRAP3);
    _DUMP_RS(D3DRENDERSTATE_WRAP4);
    _DUMP_RS(D3DRENDERSTATE_WRAP5);
    _DUMP_RS(D3DRENDERSTATE_WRAP6);
    _DUMP_RS(D3DRENDERSTATE_WRAP7);

    // D3D6 and lower
    _DUMP_RS(D3DRENDERSTATE_TEXTUREHANDLE);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREADDRESS);
    _DUMP_RS(D3DRENDERSTATE_WRAPU);
    _DUMP_RS(D3DRENDERSTATE_WRAPV);
    _DUMP_RS(D3DRENDERSTATE_MONOENABLE);
    _DUMP_RS(D3DRENDERSTATE_ROP2);
    _DUMP_RS(D3DRENDERSTATE_PLANEMASK);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREMAG);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREMIN);
    _DUMP_RS(D3DRENDERSTATE_TEXTUREMAPBLEND);
    _DUMP_RS(D3DRENDERSTATE_SUBPIXEL);
    _DUMP_RS(D3DRENDERSTATE_SUBPIXELX);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEENABLE);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN00);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN01);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN02);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN03);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN04);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN05);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN06);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN07);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN08);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN09);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN10);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN11);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN12);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN13);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN14);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN15);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN16);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN17);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN18);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN19);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN20);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN21);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN22);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN23);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN24);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN25);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN26);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN27);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN28);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN29);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN30);
    _DUMP_RS(D3DRENDERSTATE_STIPPLEPATTERN31);

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
