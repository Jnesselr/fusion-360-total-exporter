# Fusion 360 Total Exporter
Need to export all of your fusion data in a bunch of formats? We've got you covered. This will export your designs across all hubs, projects, files, and components. It exports them in STL, STEP, and IGES format. It also exports the sketches as DXF files. In addition to those, an f3d/f3z file will be exported for each component/assembly file in all of your projects, across all hubs. It doesn't ask what you want written out, it just writes out the latest version of everything, to the folder of your choice.

## How do I use this?
1. Download this project from [here](https://github.com/Jnesselr/fusion-360-total-exporter/archive/master.zip), and unzip it (Or clone this repo, if you are familiar with git)
2. Open Fusion 360
3. Click on "Tools" then "Scripts/Add-ins"
4. Click the + button and select the unzipped folder
5. Double click on the "Fusion 360 Total Export" script
6. Acknowledge that this might take a while (There's a menu, but you should probably internalize that)
7. Select where you want the output to go - we suggest making a dedicated folder, to help keep everything nice and organized 
8. Go do something else for a while or enjoy a walk down memory lane as every single design you have is opened, exported, then closed again.

## Why did you make this?
Autodesk just announced that they were limiting features in their free tier to a level that made people a wee bit upset. I pay for Fusion 360, but I get that it's too much of an expense for some people. I had experience with exporting STL files for BotQueue (shhh spoilers) and figured that if I wrote a plugin, no one would have to do manual exports. Yay! Automation reigns supreme!

### Extended feature
Use this script to backup all your projects and models as `f3d` file. Running the script again will only export the models which have been modified (validates the date), and all other files will be exported with the version number added to the file name (stl, step, ...).

## What happens if I don't like what this plugin does?
No warranty is implied, etc. etc. Go blame Autodesk for changing the free tier. If you want to blame me for anything, blame me and my sense of ethics for feeling like I need to write this program in the first place.

## What if I find a bug?
If an exception occurs, the script will let you know after it has exported everything that it can export. There will be a log file called output.log in your export folder. Submit an issue with that file attached. Please and thank you!

Also, if you can share the file that it failed on, that may help me, but it depends on what the exception actually shows.

### Failed exports
When an export fails a file is left with the ending `.failed`. The output file can provide details about the error.
You can search for the `.failed` files and manually try to export the desired output or resolve the error.

## I don't like your style of writing
That wasn't a question. But yeah... me too some days.
