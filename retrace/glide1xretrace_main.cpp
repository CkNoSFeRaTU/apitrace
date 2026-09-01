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


#include <string.h>

#include "os_string.hpp"
#include "os_time.hpp"

#include "retrace.hpp"
#include "glide1xretrace.hpp"

void
retrace::setFeatureLevel(const char *featureLevel) {
}


void
retrace::setUp(void) {
}

void
retrace::addCallbacks(retrace::Retracer &retracer)
{
    retracer.addCallbacks(glide1xretrace::glide1x_callbacks);
    retracer.addCallbacks(glideretrace::glide_misc_callbacks);
}


void
retrace::flushRendering(void) {
}

void
retrace::finishRendering(void) {
}

void
retrace::waitForInput(void) {
    flushRendering();
    while (glideretrace::processEvents()) {
        os::sleep(100*1000);
    }
}

void
retrace::cleanUp(void) {
}
