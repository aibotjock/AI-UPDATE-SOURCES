# Infrastructure fixtures

These files test rendering infrastructure. They are not episode content, real model results, a completed feature demonstration or a quality-approved narration voice.

`voice-sample.wav` was generated offline on October 13, 2026 using FFmpeg 6.1.1's installed Flite `slt` generic voice. Source text: “Welcome to A I Update. I am Doctor Chris. When an A I model tops a leaderboard, how do you know whether it is right for your work?” The voice is synthetic and does not impersonate Dr. Chris. Naturalness and pronunciation have not received listening-based approval.

`title-frame.png` is a frame extracted at 1.5 seconds from a four-second original infrastructure sample, generated in FFmpeg with a navy background and the text AI UPDATE. It is an original branding test, with no source/benchmark evidence.

Installed Flite notices were inspected at `/usr/share/doc/libflite1/copyright`. Flite's main license permits use and distribution without restriction, including commercial use, subject to preservation of code notices, marking modifications, keeping author names and avoiding endorsement claims. These fixtures contain generated audio and image output, not Flite code or binaries.

Fixture binaries are regenerated locally by test_renderer.ensure_samples using FFmpeg Flite and a plain title frame. They are excluded from Git to avoid duplicated audio/images. Regenerated frames have no benchmark or documentary claims.
