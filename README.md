# AmbiCam

Scripts for extracting LED Colors for "AmbiLight"-Clones using a RaspberryPi and the PiCamera.

**NOTE** This is a pre-alpha, work-in-progress, hobby project and is not (yet) destined to work for anybody else than my setup.

## Getting started

AmbiCam does perform a homomorphic transformation to the image captured to not
require the camera to be positioned directly opposite the screen.

First, start `ambicam` with `-o` to save the capture image (and stop using after a
bit using Ctrl+C):

```sh
./ambicam --nosend -o img.bmp
```

Then, using some image processing tool like gimp, find the pixel positions of
the top left, top right, bottom right and bottom left corners and provide the
image and corner positions to `calibrate`:

``` sh
./calibrate img.bmp "(145,243) (575,250) (576,486) (140,485)"
```

The resulting calibration will be written as `ambicam.calib` and can be given to
`ambicam` now:

``` sh
./ambicam -c ambicam.calib
```

## TODO

* Use Hyperion LED geometry (from config)
* Fix / re-enable custom warping of the border regions
* Automatic calibration using OpenCV and controlling leds
* Configurable border, offset, blurring and mean calculations
* Proper blackborder detection


## Licence

AmbiCam is released under the [Mozilla Public License Version 2.0](http://www.mozilla.org/MPL/).
