# Fusion 360 Total Exporter
Need to export all of your fusion data in a bunch of formats? We've got you covered. This will export your designs across all hubs, projects, files, and components. It exports them in STL, STEP, and IGES format. It also exports the sketches as DXF. It doesn't ask what you want written out, it just writes out the latest version of everything.

## How do I use this?
1. Clone this repo somewhere on your computer
2. Open Fusion 360
3. Click on "Tools" then "Scripts/Add-ins"
4. Click the + button and select the cloned directory
5. Double click on the "Fusion 360 Total Export" script
6. Acknowledge that this might take a while (There's a menu, but you should probably internalize that)
7. Select where you want the output to go
8. Go do something else for a while or enjoy a walk down memory lane as every single design you have is opened, exported, then closed again.

## Why did you make this?
Autodesk just announced that they were limiting features in their free tier to a level that made people a wee bit upset. I pay for Fusion 360, but I get that it's too much of an expense for some people. I had experience with exporting STL files for BotQueue (shhh spoilers) and figured that if I wrote a plugin, no one would have to do manual exports. Yay! Automation reigns supreme!

## What happens if I don't like what this plugin does?
No warrenty is implied, etc. etc. Go blame Autodesk for changing the free tier. If you want to blame me for anything, blame me and my sense of ethics for feeling like I need to write this program in the first place.

## What if I find a bug?
If an exception occurs, it should tell you what file it happened on in a message box and THEN another message box will pop up with the exception itself. Take screenshots of both. Submit an issue. Please and thank you!

Also, if you can share the file that it failed on, that may help me, but it depends on what the exception actually shows.

## I don't like your style of writing
That wasn't a question. But yeah... me too some days.
