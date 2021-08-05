# LardRenderQueue

The Lard Render Queue is a WIP Python script to automatically queue and run headless renders of Blender projects (`.blend` files).

Note that the script is currently under development and is not usable in its current state.

---

## Features

This is a list of features to be implemented by the time of the script's first usable version.

- Render `.blend` files, including still images and animations
- Bake all dynamics in `.blend` files
- Queue multiple renders/bakes and modify the order in which they are queued
- Detect when renders/bakes have failed and report the corresponding exit codes from Blender
- Pause and resume renders (animations only) and bakes (if possible) for user convenience

---

## Getting Started

The script is developed with Python 3.7 but may work with earlier versions.

Blender must be installed and in your `PATH` such that it is accessible via the command line. bpy updates along with Blender so it is recommended to use a relatively recent version.

To run the script, run the following:

    python repo_path/RenderQueue

The script is developed in Visual Studio, and thus includes solution and project files, but only the `.py` files are needed to run.

---

### External Links

[Blender Website](https://www.blender.org)

The Blender Foundation does not endorse this project in any way.
