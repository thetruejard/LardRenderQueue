# LardRenderQueue

The Lard Render Queue is a WIP Python script to automatically queue and run headless renders and bakes of Blender projects (`.blend` files).

Note that the script is currently under development and only some features are usable in its current state.

For license information, see [LICENSE.md](LICENSE.md).

---

## Features

The following features are complete and ready for use.

- Render `.blend` files (animations only)
- Queue multiple renders
- Pause and resume renders

The following features are NOT yet complete and ready for use.

- Render `.blend` files (still images)
- Bake all dynamics in `.blend` files
- Modify the order in which tasks are queued
- Detect when renders/bakes have failed and report the corresponding exit codes from Blender
- Pause and resume bakes (if possible)

---

## Getting Started

The script is developed with Python 3.7 but may work with other versions.

Blender must be installed and in your `PATH` such that it is accessible via the command line. bpy updates along with Blender so it is recommended to use a relatively recent version.

To run the script, run the following:

    python repo_path/RenderQueue

The script is developed in Visual Studio, and thus includes solution and project files, but only the `.py` files are needed to run.

---

### External Links

[Blender Website](https://www.blender.org)

The Blender Foundation does not endorse this project in any way.
