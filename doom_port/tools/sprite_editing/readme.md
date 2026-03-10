# Sprite Editing (Work in Progress)

## Explanation

### Explanation as to how the sprites work
The sprite files cover the in game objects and walls. They are stored in `.SPR` files, each of which contain multiple images. The sprite data is in hex files, which first list the number of images within the file, then the x,y sizes for each, then the raw data for the files themselves.

For example:
```
03 50 50 60 60 70 70 60 60 60 ....
```
- `03` converted to hex would be `3`. `0c` would be `12`. That's the number of images within this sprite.
- `50` in hex is `80` in decimal, so the first image is **80x80 pixels**.
- `60` in hex is `96` in decimal, so the second image is **96x96 pixels**.
- `70` in hex is `112` in decimal, so the third image is **112x112 pixels**.

The data after this is the raw image data. So for the above example:
- If it's **80x80**, the next **6400 decimal numbers** are the first image.
- The next **9216** are the second image.
- The next **12544** are the third image.

There are no delimiters within the image data itself; you need to split it based on the lengths defined from the starting sizes.

### Palettes
The `.IMG` files relate to the floor and HUD (see section on `.IMG`), but I noted that when making edits to these files, it ended up affecting the palette for the sprites on that level. With that in mind, I found that you can select the relevant floor `.IMG` for that level, extract the palette from it, and then apply this palette to the sprites in question.

I will look at adding some code and explanation for this shortly. When doing it myself, I extracted these separately in Python first, but I don't want to share any of the original game code. Therefore, I need to make it so that you can just drag and drop one of the `.GIF` files to auto-extract the palette. This may take me a little while to get updated into the code, so bear with me.

## Editor
As this is currently still in progress, I need to combine and rework some of these tools. However, the current breakdown of the tools is as follows:

- **`jsviewer.html`** – A really simple tool that lets you paste in a string of hex, set the width, and then preview this with a random color palette. This is superseded but left here for reference as it might be of use to people.
- **`imageconvert.html`** – This lets you load a `.PNG` file, applies the palette to it, and then has an export image option. This will export the image **into browser local storage**. This can then be imported in the main sprite editor. I know this is a janky setup and will need to be updated, but that's just the way I have it working for now during my own testing.
- **`1_simple_html_to_open_sprite6.html`** – This is the main sprite editor. I hard-coded the palette, which I will need to strip before sharing here, so I need to get this updated. I'll put the current code here for now. Please see the following screenshots for explanations.

**NOTE!**  These tools make sense for me, however are not at all user friendly. I must stress that I will be updating them to make them useable, but am sharing them in advance.
---
## 1_simple_html_to_open_sprite6.html - the main editor. WIP



 ![Sprites](../../images/screenshots/sprite_editor.png)

 ![Sprites](../../images/screenshots/image_import.png)



**NOTE!** I will look at getting this all updated so that you can drag on a GIF file and set it automatically, but I'm rushing to get all the tools out. It has been a few months since I worked on this, so I will need to come back to it.  

I removed my hard-coded `kfloor` palette here. For now you will need to extract the gif palette in question and set it here, or edit the browser localstorage "colorPalette_predefined_kfloor" :  


### Line 378:
```js
'kfloor': () => {
    palette = {



