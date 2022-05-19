---
title  : Installing TempEdit
layout : default
order  : 4
---

TempEdit is packaged and distributed as a [RoboFont extension].
{: .lead}

{% comment %}
<div class="card text-dark bg-light my-3">
<div class="card-header">note</div>
<div class="card-body" markdown='1'>
TempEdit currently requires that [hTools3] is installed.  
If you wish to use TempEdit without hTools3, please [get in touch].
</div>
</div>
{% endcomment %}

Installing with Mechanic
------------------------

It is recommended to install TempEdit using [Mechanic], so it can automatically check for updates and install them.

1. After acquiring a license, you will receive a `TempEdit.mechanic` file per email.
2. Go to the Mechanic extension’s settings.
3. Use the plus button to add the `.mechanic` file to the list of *Single Extension Items*.

Installing manually
-------------------

The TempEdit extension can also be installed manually if you have the extension package.

Simply double-click the file `TempEdit.roboFontExt` to have it installed in RoboFont.

<div class="card text-dark bg-light my-3">
<div class="card-header">warning</div>
<div class="card-body" markdown='1'>
If you install TempEdit manually, you will *not* be notified about updates.
</div>
</div>

{% comment %}

Installing from source
----------------------

TempEdit can be used directly from the source code if you have access to the repository.

This mode allows developers to make changes to the code while using and testing the tools in RoboFont.

1. Clone the repository using `git clone` (recommended) or download the source code.
2. In the RoboFont Preferences window, go to [Extensions > Start Up Scripts].
3. Add the file `TempEdit/Lib/start.py` to the list of start-up scripts.
4. Save the settings and restart RoboFont – TempEdit will now appear under the *Extensions* menu.

{% endcomment %}

[RoboFont extension]: http://robofont.com/documentation/extensions/
[Mechanic]: http://github.com/robofont-mechanic/mechanic-2
[hTools3]: http://hipertipo.gitlab.io/htools3-extension/
[get in touch]: mailto:gustavo@hipertipo.com
[Extensions > Start Up Scripts]: https://robofont.com/documentation/workspace/preferences-window/extensions/#start-up-scripts

