![](examples/screenshot.png)

# MosaVi (Mosaic Viewer)

A minimalist viewer for video image sequences. View multiple sets of images in a mosaic format and scroll through them in a synchronized manner.

## Quick Start
1. Install the python dependencies
```
pip install kivy
```
2. Execute the script using the provided example
```
python mosavi.py  -f 5 "example/frame_*.png" "example/flow_*.png" "example/metric*" "example/motion.png"
```
3.  You can now browse and play the sequences using the following hotkeys:'
up or left     previous
down or right  next
page_up        jump forward
page_down      jump backward
home           go to the beginning
end            go to the end
p              start/pause playing
h              help


## Usage
usage: mosavi.py [-h] [-s int int] [-f int] filePatterns [filePatterns ...]

positional arguments:
  filePatterns         one or several frame file paths. !!! Depending on the
                       shell, the paths may need to be enclosed in double quotes !!!
options:
  -h, --help           show this help message and exit
  -s, --shape int int  the mosaic shape (e.g., "width height")
  -f, --fps int        Number of frames per second when in play mode

## !!! Important !!!
In order to prevent file pattern expansion by the shell, you may need to enclose the patterns with double quotes (ex: "example/frame_*.png").
