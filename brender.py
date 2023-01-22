
'''
brender
The python script that is run directly in Blender itself to perform render tasks (both animations and stills)

For autocomplete for bpy, install fake-bpy-module with:
pip install fake-bpy-module-2.93
Or replace 2.93 with the relevant version.
See https://github.com/nutti/fake-bpy-module for more details.
This is NOT required to use the render queue.
'''

import sys

import bpy


# Get the command line arguments
# See tasks for how command line arguments are passed into this script
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

# Parse command line arguments. This must match tasks.render_animation() and tasks.render_still()
# Arg 0: whether to render an animation (if false, then this is a still image)
arg_animation = bool(int(argv[0]))




# Enable GPUs (kept for older versions. May remove soon)

#def enable_gpus(device_type, use_cpus=False):
#    preferences = bpy.context.preferences
#    cycles_preferences = preferences.addons["cycles"].preferences
#    cuda_devices, opencl_devices = cycles_preferences.get_devices()
#
#    if device_type == "CUDA":
#        devices = cuda_devices
#    elif device_type == "OPENCL":
#        devices = opencl_devices
#    else:
#        raise RuntimeError("Unsupported device type")
#
#    activated_gpus = []
#
#    for device in devices:
#        if device.type == "CPU":
#            device.use = use_cpus
#        else:
#            device.use = True
#            activated_gpus.append(device.name)
#
#    cycles_preferences.compute_device_type = device_type
#    bpy.context.scene.cycles.device = "GPU"
#
#    return activated_gpus


#enable_gpus("CUDA")


# TODO: Check output format, directory, etc.

# Disable file overwriting so that resuming renders does not redundantly re-render frames
bpy.context.scene.render.use_overwrite = False

# Begin the render
bpy.ops.render.render(animation=arg_animation, write_still=True)