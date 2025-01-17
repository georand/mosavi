"""
  MosaVi

  author: georand
  source: https://github.com/georand/mosaview
  licence = MIT
  date: 2025
"""

HELP = [
  ["up or left",    "previous"],
  ["down or right", "next"],
  ["page_up",       "jump forward"],
  ["page_down",     "jump backward"],
  ["home",          "go to the beginning"],
  ["end",           "go to the end"],
  ["p",             "start/pause playing"],
  ["h",             "help"]]

###############################################################################

import argparse, glob
from pathlib import PurePath
from os.path import (abspath as os_abspath,
                     expanduser as os_expanduser,
                     basename as os_basename)
from os import environ as os_environ
import math

os_environ["KIVY_NO_ARGS"] = '1'
os_environ["KIVY_NO_CONSOLELOG"] = '1'
os_environ["KIVY_NO_FILELOG"] = '1'

from kivy.app import App
from kivy.logger import Logger, LOG_LEVELS
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

###############################################################################

class MosaicApp(App):
  def __init__(self, fileLists, shape=None, fps=25, **kwargs):
    super(MosaicApp, self).__init__(**kwargs)
    self.fileLists = fileLists
    self.shape = shape
    self.fps = fps
    self.images = []
    self.index = 0
    self.play = False
    self.maxIndex = max(len(l) for l in self.fileLists)-1

  def build(self):
    self.title = "MosaVi"
    Window.size = (1280, 800)
    Window.left = 100
    Window.top = 100
    Window.bind(on_key_down=self.onKeyDown)

    if not self.shape:
      self.shape = mosaicDim(len(self.fileLists))

    self.layout = GridLayout(cols=self.shape[0], rows=self.shape[1],
                             size_hint=(1, 1))

    self.displayImages()

    return self.layout

  def displayImages(self):

    # Clear the layout and images list
    self.layout.clear_widgets()
    self.images.clear()

    # Add new images to the layout
    for l  in fileLists:
      boxLayout = BoxLayout(orientation='vertical')
      index = max(0, min(len(l) - 1, self.index))

      # loadImage
      imagePath = l[index]
      img = Image(source=imagePath, fit_mode = "contain", size_hint=(1, 1))
      self.images.append(img)

      # write image label
      p = PurePath(imagePath)
      s = p.parent.name+'/'+p.name
#      s = "xx"
      label = Label(text=s, halign='left',
                    color=(1, 1, 1, 1), size_hint=(1, None),)
      label.texture_update()
      label.height = label.texture_size[1]+10

      # Add the image and label to the FloatLayout
      boxLayout.add_widget(label)
      boxLayout.add_widget(img)

      # Add the FloatLayout to the main layout
      self.layout.add_widget(boxLayout)

  def playStart(self):
    self.play = True
    Clock.schedule_interval(self.playNextFrame, 1 / self.fps)

  def playPause(self):
    self.play = False
    Clock.unschedule(self.playNextFrame)

  def playNextFrame(self, dt):
    self.shiftFrame(1)
    if self.index >= self.maxIndex:
      self.index = 0

  def shiftFrame(self, shift=1):
    self.index += shift
    self.index = max(0, min(self.maxIndex, self.index))
    self.displayImages()

  def onKeyDown(self, window, key, *args):
    if key == 32 or key == 13: # spacebar or return
      if not self.play:
        self.playStart()
      else:
        self.playPause()
    elif key == 273 or key == 276:  # up or left
      self.shiftFrame(-1)
    elif key == 274 or key == 275:  # down or right
      self.shiftFrame(+1)
    elif key == 280: # pageUp
      self.shiftFrame(-int(self.maxIndex/10))
    elif key == 281: # pageDown
      self.shiftFrame(int(self.maxIndex/10))
    elif key == 278: # home
      self.shiftFrame(-0x7FFFFFFF)
    elif key == 279: # end
      self.index = 0x7FFFFFFF
    elif key == 104:  # h -> help  (since kivy catch F1)
      self.popupHelp()

  def popupHelp(self):
    layout = BoxLayout(orientation='horizontal')
    leftLayout = BoxLayout(orientation='vertical', size_hint_x=-1)
    rightLayout = BoxLayout(orientation='vertical', size_hint_x=-1)
    hLeft, hRight = "", ""
    for item in HELP:
      hLeft += item[0]+'\n'
      hRight += item[1]+'\n'
    leftLayout.add_widget(Label(text=hLeft, halign='right'))
    rightLayout.add_widget(Label(text=hRight, halign='left' ))
    layout.add_widget(leftLayout)
    layout.add_widget(rightLayout)
    popup = Popup(title='Help', content=layout, size_hint=(0.3, 0.3))
    popup.open()

  def on_start(self):
    pass

###############################################################################

def mosaicDim(n):
  def biggestDiv(n):
    d = []
    for i in range(int(n/2)+1, 0, -1):
      if n % i == 0:
        d.append(i)
        if i * i == n:
          pass
          d.append(i)
      if len(d) == 2:
        break
    return d
  d = biggestDiv(n)

  while len(d) != 2:
    n += 1
    d = biggestDiv(n)
  return d

###############################################################################

if __name__ == '__main__':

  description = "an image mosaic viewer allowing to view simultaneously\
  several set of images. Hit key 'h' to get help \n"
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('-s', '--shape', nargs=2, metavar='int', required=False,
                      dest='shape',  type= int, default = None,
                      help="the mosaic shape (e.g., \"width height\")")
  parser.add_argument('-f', '--fps', metavar='int', required=False,
                      dest='fps',  type= int,
                      choices=range(1, 100), default = 25,
                      help="Number of frames  per second when in play mode")
  parser.add_argument('filePatterns', nargs='+',
                      help = "one or several frame file paths. "
                      "!!! Depending on the shell, the paths may need "
                      "to be enclosed in double quotes !!!")
  args = parser.parse_args()

  if args.shape and len(args.filePatterns) > args.shape[0] * args.shape[1]:
    print("\n  Bad shape error: not enough mosaic cells"
          f" (shape_width * shape_height < {len(args.filePatterns)}).",
          "\n  Exiting...")
    exit(-1)

  fileLists = []
  error = False
  for fp in args.filePatterns:
    p = os_expanduser(fp)
    l = sorted(glob.glob(p))
    if not l:
      print(f"\nError no files corresponding to {fp})")
      error = True
    else:
      fileLists.append(l)
  if error:
    exit(-1)

  MosaicApp(fileLists, shape=args.shape, fps=args.fps).run()
