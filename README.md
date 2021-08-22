# LardRenderQueue

The Lard Render Queue is a WIP Python script to automatically queue and run headless renders and bakes of Blender projects (`.blend` files).

Note that the script is currently under development and only some features are usable in its current state.

For license information, see [LICENSE.md](LICENSE.md).

---

## Features

The following features are complete and ready for use.

- Render `.blend` files, including animations and still images
- Queue multiple renders
- Pause and resume renders
- Log the completion status of renders and report the exit codes from Blender on failure

The following features are currently under development.

- Bake all dynamics in `.blend` files
- Modify the order in which tasks are queued
- Detect when bakes have failed and report the corresponding exit codes from Blender
- Pause and resume bakes (if possible)

The following features are planned for the future.

- "Headless" script operation to modify the queue without running tasks
- Queue any kind of script, including python, batch, shell, bash, and any executable accessible via the command line
- LAN file sharing and remote queueing for render farm support
- Support for photogrammetry with Meshroom

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
