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
#include "glideimports.hpp"
#include "glidecommon.hpp"
#include "glide1xstate.hpp"

namespace glide1xstate {

void
dumpDevice(StateWriter &writer)
{
    glidestate::dumpRenderstate(writer);

    writer.beginMember("shaders");
    writer.beginObject();
    writer.endObject();
    writer.endMember(); // shaders

    dumpTextures(writer);

    writer.beginMember("framebuffer");
    writer.beginObject();

    dumpBuffer(writer, GR_BUFFER_FRONTBUFFER);
    dumpBuffer(writer, GR_BUFFER_BACKBUFFER);
    dumpBuffer(writer, GR_BUFFER_AUXBUFFER);
    dumpBuffer(writer, GR_BUFFER_DEPTHBUFFER);

    writer.endObject();
    writer.endMember(); // framebuffer
}

} /* namespace glide1xstate */
