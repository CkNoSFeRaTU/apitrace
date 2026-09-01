About **repository**
==================

This repository contains a fork of [apitrace](https://github.com/apitrace/apitrace)
with not yet upstreamed changes for support of now legacy and considered retro API.
Those are DirectDraw, Direct3D2 - Direct3D7, 3Dfx Glide 2.0 - 3.1.


About **apitrace**
==================

**apitrace** consists of a set of tools to:

* trace OpenGL, Direct3D, and DirectDraw APIs calls to a file;

* replay OpenGL and Direct3D calls from a file;

* inspect OpenGL and Direct3D state at any call while retracing;

* visualize and edit trace files.

See the [apitrace homepage](https://apitrace.github.io/) for more details.


Status
======

TL;DR: Apitrace is still being maintained, but the maintainer has very little
time to work on it, so patches/issues/requests are addressed if/as time permits.

Long version [here](https://jrfonseca.blogspot.co.uk/2016/10/apitrace-maintenance.html)


Obtaining **apitrace**
======================

To obtain apitrace either [download the latest
binaries](https://apitrace.github.io/#download) for your platform if available,
or follow [these instructions](docs/INSTALL.markdown) to build and install it
yourself.

On 64bits Linux and Windows platforms you'll need apitrace binaries that match
the architecture (32bits or 64bits) of the application being traced.


Usage
=====

Detailed usage instructions are available [here](docs/USAGE.markdown).
