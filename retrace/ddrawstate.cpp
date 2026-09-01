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
#include "d3dstate.hpp"


namespace d3dstate {

void
dumpDevice(StateWriter &writer)
{
    writer.beginMember("parameters");
    writer.beginObject();
    writer.endObject();
    writer.endMember(); // parameters

    writer.beginMember("shaders");
    writer.beginObject();
    writer.endObject();
    writer.endMember(); // shaders

    dumpTextures(writer);

    writer.beginMember("framebuffer");
    writer.beginObject();

    writer.endObject();
    writer.endMember(); // framebuffer
}

void
dumpDevice(StateWriter &writer, IDirectDraw *pDevice)
{
    dumpDevice(writer);
}
void

dumpDevice(StateWriter &writer, IDirectDraw2 *pDevice)
{
    dumpDevice(writer);
}

void
dumpDevice(StateWriter &writer, IDirectDraw4 *pDevice)
{
    dumpDevice(writer);
}

void
dumpDevice(StateWriter &writer, IDirectDraw7 *pDevice)
{
    dumpDevice(writer);
}

} /* namespace d3dstate */
