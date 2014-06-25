Fontuley
========

This project is intended to provide some tools to make it easier to work with
fonts; eg,
- inspect fonts; eg,
  - view the cmap including the tables and segments
  - view the font's license (the name table info)
- modify fonts
  - subset a font
  - convert from ttf to woff

The initial tool will display the table of contents of a TrueType/OpenType font.

The tools will be accessed thru a web server. Initially this project will
use the Google App Engine as the web server. Other servers may be considered
in the future.

The tools and server in this project will be based on the Python fontTools.
Currently (June 2014) there is the original/older version of fontTools:
* http://sourceforge.net/projects/fonttools/

and the newer version

* https://github.com/behdad/fonttools/

This project will start with the newer version.

