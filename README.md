Resolve Camera Track
====================

Addon for Blender implementing 3D point reconstruction using multiple camera angles.

Installation
------------

The process is the same as any other Blender addon:

1. Open the User Preferences window (Ctrl + Alt + U) to the "Addons" tab.
2. Press "Install from File...".
3. In the resulting file browser pane, select `Resolve Camera Tracks.py`.
4. The addon entry should appear in the user preferences window.
5. Check the checkbox at the top right of the entry, beside the running man icon.

Alternatively, run the script from within a Text Editor window.

Workflow
--------

The following is a recommended workflow for working with the addon:

1. In the real world, mark a point on the ground as the real reference point. This is the center of the stage, so to speak.
2. Pick a point in Blender as the virtual reference point. The origin is generally a good choice.
3. Set up two or more cameras facing the reference point. For two cameras, the best setup is having the cameras facing 90 degrees to each other.
4. In Blender, add the same number of cameras, and set their properties such as sensor size to the same values as the real-world cameras. These values can often be found online by searching for the camera model, or in the user manual for the camera.
5. Measure and record the distance and angle from each real camera to the reference point.
6. Move the Blender cameras so that they are the same distance and angle from the virtual reference point as their associated real cameras are from the real reference point.
7. Start recording with both cameras.
8. Begin the performance near the reference point, ensuring that points of interest are visible to the cameras as much as possible.
9. Stop recording.
10. Synchronize and trim the video footage from all cameras with a video editor such as Avidemux, or use Blender for this.
11. Ensure the video footage from all cameras all start at the same moment in real time.
12. In Blender, track the points of interest using the motion tracker, ensuring the camera settings such as focal length are set to the same as the real cameras.
13. Use `Movie Clip Editor > Reconstruction > Link Empty to Track` for each track, making sure they are associated with the correct Blender camera.
14. Follow the steps in the During section below, under the Usage heading, for each real-world point tracked.
15. You should now have a set of Empty objects that track in 3D the locations of the real-world markers. An example usage would be using these as hooks for a rig.

Usage
-----

The operator is accessible via `View3D > Object > Resolve Camera Tracks`, or `Search > Resolve Camera Tracks`.

### Before

* The video footage is shot from two or more non-moving cameras facing the target at different angles.
* The video footage from all camera angles are synchronized and begin at the same point in real time.
* There are the same number of Blender cameras, positioned in the same orientation and relative position.
* The Blender cameras are calibrated with respect to the focal length and any other relevant settings.
* Your video has been tracked - there are virtual markers in Blender tracking each real world point of interest on your target.
* Each track has an associated Empty object linked to its path (this is done using `Movie Clip Editor > Reconstruction > Link Empty to Track`).

### During

1. Mentally pick a single physical point to reconstruct.
2. Select the Empty objects from each camera that track the physical point.
3. Invoke the Resolve Camera Tracks operator from the menu or searchbar, as described above.

### After

There should be a new Empty object with its location animated such that at every frame, it **tracks the physical marker in 3D**.

The resulting Empty object will only be keyframed when at least 2 of the Blender markers it is tracking are enabled - when its 3D position can be unambiguously determined.

Possible errors include:

* `Non-empty object selected`: when invoking the operator, one of the selected objects was not of the type Empty.
    * Select only empty objects.
* `Motion Tracking constraint to be converted not found`: one of the selected objects was missing the Follow Track constraint that makes it follow the track.
    * Ensure each object has a Follow Track constraint.
* `Movie clip to use tracking data from isn't set`: one of the selected objects' Follow Track constraint did not have its Clip property set.
    * Check the Follow Track constraint settings for each object to ensure the Clip property is set.
* `Tracked object not found`: one of the selected objects' Follow Track constraint did not have a correctly associated track.
    * Check the Follow Track constraint settings for each object to ensure the Track property is set.
* `At least 2 cameras need to be available`: the selected empties must represent views from two or more cameras, but only represented 0 or 1.
    * Select empties representing views from more than 1 camera.
* `Lines are too close to parallel`: the rays shot from the two cameras to their associated Empty objects are parallel.
    * Shoot the footage from cameras at a larger angle apart.