Wagtail Editor's Guide
======================

This guide is designed for Wagtail editors of SecureDrop.org. It will explain where to find certain settings and the ins and outs of this particular Wagtail site.

General information about editing Wagtail sites can be found in `Wagtail's documentation <https://guide.wagtail.org/>`_.

Table of Contents
-----------------

* `Site Settings`_
   * `Site Footer`_
   * `Site Alert`_
   * `Tor Alert`_
   * `Social Sharing SEO`_
   * `Directory Settings`_
* `Page Settings`_
   * `Directory Page`_
   * `Blog Index Page (News)`_
   * `FAQ and SimplePageWithSidebar`_
* `Snippets`_
   * `Menus`_
   * `Result Groups`_

Site Settings
-------------

This site makes heavy use of settings in an attempt to be almost fully customizable by the user. All of the settings mentioned below are custom settings for this repository that are editable via the settings menu in Wagtail.

Site Footer
+++++++++++
The footer contains two menus which can be edited via the snippets panel, and assigned to the footer in this panel. Various other links and text displayed in the footer can be updated here.

Site Alert
++++++++++
This is a site-wide alert that is displayed at the top of the screen in read, meant for security notices and other important warnings.

Tor Alert
+++++++++
These alerts are aimed at sources only, and are only displayed on the homepage, directory page, and individual instance pages. `Tor not detected` is meant to provide information for sources how are not yet using Tor, while `Tor settings too low` is meant for Tor users who have not disabled JavaScript.

Social Sharing SEO
++++++++++++++++++
These are settings for social media and search engine optimization, including a default site description and image as well as social media settings.

Directory Settings
++++++++++++++++++
These are settings that are used on the SecureDrop instance pages (DirectoryEntry) that users and admins can create. The text in these settings will show up on every SecureDrop page.

You can also change which user group will receive alerts when SecureDrop instances are submitted.

Page Settings
-------------
In addition to site-wide settings, some pages also have settings that are important to note. These settings can be reached via the ``Settings`` tab on each individual page.

Directory Page
++++++++++++++
In the settings tab on the Directory Page, you'll find settings for a variety of information on the page, making it easily customizable. This is information displayed with directory forms, as well as text and links on the Directory Page itself.

Blog Index Page (News)
++++++++++++++++++++++
The settings tab on the blog index page contains link text, titles, and pagination settings.

FAQ and SimplePageWithSidebar
+++++++++++++++++++++++++++++
These pages allow you to choose a menu (created in the Snippets panel) that will be displayed in the sidebar of the page. These menus can be used to link pages together.

Snippets
--------
There are two types of snippets used on the site. Snippets can be accessed from the main Wagtail menu.

Menus
+++++
Menus are groups of links used throughout the site. The Main Menu is displayed on the home page. Other menus can be linked to the footer, or FAQ and SimplePageWithSidebar.

Result Groups
+++++++++++++
Result Groups are used to display results from scanning a SecureDrop landing page. The title of each group is displayed as a header. Each ``result state`` in a result group must have the exact name of a field in the Result model (in the ``directory`` app).

These result states three types of text. A success text, displayed if the corresponding field on the Result model is ``True``; a failure text, displayed if the corresponding field on a model is ``False``; and a fix text, which is displayed immediately after a user scans their page and shows them what to do to pass that test. Result states also contain an 'is warning' field, which will cause the failure text to display with a yellow flag if checked, or a red x if left unchecked.
