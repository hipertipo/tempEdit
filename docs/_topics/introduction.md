---
layout: default
title: Introduction to TempEdit
---

TempEdit offers a fast and flexible workflow for editing fonts with large designspaces.
{: .lead }

* Table of Contents
{:toc}


The problem
-----------

Working with large font families containing many source files can be challenging. To edit various versions of the same glyph simultaneously, several full fonts have to be opened in the interface, making the application slower, and making it harder to jump between glyphs in different fonts.


<div class="card text-dark bg-light my-3">
<div class="card-header">see also</div>
<div class="card-body" markdown='1'>
[What computer performance metrics are most relevant to RF performance?](http://forum.robofont.com/topic/672/what-computer-performance-metrics-are-most-relevant-to-rf-performance)
{: .card-text }
</div>
</div>


A solution
----------

TempEdit offers a method for editing various versions of a glyph across multiple sources without having to open their full fonts. The glyphs are imported into one or more temporary font(s) for editing, and are saved back into their source UFOs when editing is over. The multiple source glyphs can be imported as layers of a single font, as parallel glyphs, or as separate fonts.


Implementation details
----------------------

When a glyph is imported into the temporary font, the path to its parent glyph set is stored in the glyph lib. This makes it possible for the glyph to find its way back to its source font when exporting.

```xml
<key>com.hipertipo.tempEdit.glyphSetPath</key>
<string>path/to/glyphSet</string>
```
