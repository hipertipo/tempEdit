---
title  : TempEdit
layout : default
order  : 1
---

A tool to edit glyphs from multiple designspace sources using temporary font(s).
{: .lead}

<div class='row'>

<div class='col-sm-4' markdown='1'>
  <img class='img-fluid' src='{{ site.url }}/images/tempedit_tool.png' />
</div>

<div class='col-sm-8' markdown='1'>
designspaces
: a list of designspace files  
  
  - drag one or more `.designspace` files from Finder to add them to the list
  - select and press backspace to remove files from the list

sources
: a list os sources in the selected designspace
  
  - select one or more sources to import glyphs from

glyphs
: a list of glyph names to import from the selected sources

import glyphs
: import glyphs with the given glyph names from the selected designspace sources for editing  

export selected glyphs
: export selected glyphs in the current temp font back into their parent fonts
  
</div>

</div>

Import modes
------------

TempEdit offers 3 different import modes:

fonts → fonts  
: ^
  Import glyph(s) from each source into a separate font.
  
  <img class='img-fluid' src='{{ site.url }}/images/tempedit_mode-fonts.png' />

fonts → glyphs  
: ^
  Import each glyph source into a separate glyph of a single font
  
  <img class='img-fluid' src='{{ site.url }}/images/tempedit_mode-glyphs.png' />

fonts → layers  
: ^
  Import glyph sources as layers of a single font.
  
  <img class='img-fluid' src='{{ site.url }}/images/tempedit_mode-layers-1.png' />
  <img class='img-fluid' src='{{ site.url }}/images/tempedit_mode-layers-2.png' />
