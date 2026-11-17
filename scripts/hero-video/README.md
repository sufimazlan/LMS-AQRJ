# Home page video

The looping classroom video at the top of the home page is a 3D scene built and
rendered with Blender by `classroom.py`. Nobody in it is a real person.

- **People:** made with [MPFB](https://github.com/makehumancommunity/mpfb2), the MakeHuman
  plug-in for Blender. It gives real human proportions for children and adults.
- **Clothes, room, furniture, light and motion:** built by `classroom.py`.

## Set up (once)

```sh
pip install bpy                                   # Blender as a Python module, about 400 MB
git clone --depth 1 https://github.com/makehumancommunity/mpfb2.git
BLENDER=$(python3 -c "import bpy; print('%d.%d' % bpy.app.version[:2])")
mkdir -p ~/.config/blender/$BLENDER/extensions/user_default
ln -s "$PWD/mpfb2/src/mpfb" ~/.config/blender/$BLENDER/extensions/user_default/mpfb
```

Tested with Blender 5.3 and MPFB 2.0.18. MPFB is not copied into this repository:
its code is GPL-3.0 and its base human model is CC0.

## Change the scene

Edit `classroom.py` (colours, people, camera, light, motion), then look at one frame
before rendering them all:

```sh
python3 classroom.py --out test --end 1      # one frame, about a minute
python3 classroom.py --out frames            # 80 frames, about 50 s each on 2 CPU cores
```

A stopped render carries on where it left off.

## Turn the frames into the files the page uses

```sh
ffmpeg -y -framerate 16 -i frames/frame_%04d.png -c:v libx264 -preset veryslow -crf 25 \
  -pix_fmt yuv420p -movflags +faststart -an ../../src/lib/assets/kelas.mp4
ffmpeg -y -framerate 16 -i frames/frame_%04d.png -c:v libsvtav1 -preset 3 -crf 38 \
  -pix_fmt yuv420p -movflags +faststart -an ../../src/lib/assets/kelas.av1.mp4
ffmpeg -y -i frames/frame_0000.png -quality 70 ../../static/media/kelas.webp
```

The page offers the AV1 file first (about half the size) and falls back to H.264,
which every browser plays. Keep each under about 600 kB: the video is the first
big thing a phone downloads on the home page. The frames are not kept in the repository.

## How the page loads it

- The still picture (`kelas.webp`, about 30 kB) is preloaded and shown at once.
  The video replaces it when enough has arrived to play.
- The video is 960 x 540. Phones show a taller 4:3 crop of the same file, so the
  people stay large on a narrow screen. Keep the ustazah and the board near the
  middle of the frame.
- The page plays the video through `/api/video/...`, not as a plain file, because
  iPhones need the server to send the file in parts. See the note in
  `src/routes/api/video/[name]/+server.ts`.
- People who ask their device for less motion get the still picture only.
