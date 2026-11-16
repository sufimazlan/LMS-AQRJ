# Home page video

The looping classroom video at the top of the home page is a 3D scene built and
rendered with Blender by `classroom.py`. Nothing in it is a photo of a real person.

## Change it

Edit `classroom.py` (colours, people, camera, motion), then:

```sh
pip install bpy                       # Blender as a Python module, about 400 MB
python3 classroom.py --out frames     # 100 PNG frames, about 20 s each on 2 CPU cores
```

A stopped render carries on where it left off. For a quick look at one frame:
`python3 classroom.py --out test --end 1`.

## Turn the frames into the files the page uses

```sh
ffmpeg -y -framerate 20 -i frames/frame_%04d.png -c:v libx264 -preset veryslow -crf 27 \
  -pix_fmt yuv420p -movflags +faststart -an ../../src/lib/assets/kelas.mp4
ffmpeg -y -i frames/frame_0000.png -quality 72 ../../static/media/kelas.webp
```

Keep the video under about 1 MB: it is the first thing a phone downloads on the
home page. The frames themselves are not kept in the repository.

The page plays the video through `/api/video/kelas`, not as a plain file, because
iPhones need the server to send the file in parts. See the note in
`src/routes/api/video/kelas/+server.ts`.
