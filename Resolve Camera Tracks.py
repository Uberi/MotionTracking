from mathutils import Vector
import bpy
import itertools

bl_info = {
    "name": "Resolve Camera Tracks",
    "author": "Anthony Zhang",
    "category": "Animation",
    "version": (1, 0),
    "blender": (2, 69, 0),
    "location": "View3D > Object > Resolve Camera Tracks or Search > Resolve Camera Tracks",
    "description": "3D point reconstruction from multiple camera angles",
}

class ResolveCameraTracks(bpy.types.Operator):
    bl_idname = "animation.resolve_camera_tracks"
    bl_label = "Resolve Camera Tracks"
    bl_options = {"REGISTER", "UNDO"}  # enable undo for operator
    
    def execute(self, context):
        targets = []
        for obj in context.selected_objects:
            if obj.type == "EMPTY":
                targets.append(obj)
            else:
                self.report({"ERROR_INVALID_INPUT"}, "Non-empty object selected")
                return {"CANCELLED"}
        
        bpy.ops.clip.constraint_to_fcurve() # apply motion track for all targets
        return self.add_resolved_empty(targets)
    
    def get_target_locations(self, target):
        """
        Obtains a list of positions in world space for a given target for each frame in its tracking clip.
        
        Returns the list of positions, the associated camera, the start frame, and the end frame.
        """
        # find the follow track constraint and obtain the associated track
        for c in target.constraints:
            if c.type == "FOLLOW_TRACK":
                track_constraint = c
        if not track_constraint:
            raise Exception("Motion Tracking constraint to be converted not found")
        if not track_constraint.clip:
            raise Exception("Movie clip to use tracking data from isn't set")
        tracks = (track for obj in track_constraint.clip.tracking.objects for track in obj.tracks) #wip: this is a workaround for when clip.tracking.tracks is empty when it shouldn't be
        track = None
        for t in tracks:
            if t.name == track_constraint.track:
                track = t
        if track == None:
            raise Exception("Tracked object not found")
        
        # obtain track information
        marker_frames = {marker.frame for marker in track.markers if not marker.mute} # set of frames of enabled markers
        start_frame, end_frame = min(marker_frames), max(marker_frames)
        
        # store object world locations
        locations = []
        print("start")
        for i in range(start_frame, end_frame + 1):
            if i in marker_frames:
                bpy.context.scene.frame_set(i)
                locations.append(target.matrix_world.to_translation())
            else:
                locations.append(None)
        return locations, track_constraint.camera, start_frame, end_frame
    
    def add_resolved_empty(self, targets):
        """
        Adds an empty animated to stay at the point closest to every target in `targets`.
        """
        
        # obtain target information
        target_points, target_cams, target_starts, target_ends = [], [], [], []
        for target in targets:
            try:
                points, cam, start, end = self.get_target_locations(target)
            except Exception as e:
                self.report({"ERROR_INVALID_INPUT"}, str(e))
                return {"CANCELLED"}
            target_points.append(points + [None]) # the last element must be None
            target_cams.append(cam)
            target_starts.append(start)
            target_ends.append(end)
        
        if len(set(target_cams)) < 2: # two camera is the minimum number of cameras
            self.report({"ERROR_INVALID_INPUT"}, "At least 2 cameras need to be available")
            return {"CANCELLED"}
        
        # add the empty object
        bpy.ops.object.add(type="EMPTY")
        resolved = bpy.context.active_object
        
        # set up keyframes for each location
        original_frame = bpy.context.scene.frame_current
        for frame in range(min(target_starts), max(target_ends)):
            # clamp indices to the last value, None, if outside of range
            indices = []
            for start, end in zip(target_starts, target_ends):
                index = frame - start
                indices.append(-1 if index < 0 or index > end - start else index)
            
            bpy.context.scene.frame_set(frame) # move to the current frame
            
            # go through each possible combination of targets and find the one that gives the best result
            best_location = None
            best_distance = float("inf")
            for pair in itertools.combinations(range(0, len(targets)), 2):
                first, second = pair[0], pair[1]
                cam1, cam2 = target_cams[first].location, target_cams[second].location
                location1, location2 = target_points[first][indices[first]], target_points[second][indices[second]]
                if location1 != None and location2 != None:
                    try:
                        location, distance = closest_point(cam1, cam2, location1, location2)
                    except Exception as e:
                        self.report({"ERROR_INVALID_INPUT"}, str(e))
                        return {"CANCELLED"}
                    if distance < best_distance: # better result than current best
                        best_distance = distance
                        best_location = location
            
            # add keyframe if possible
            if best_location != None:
                resolved.location = best_location
                resolved.keyframe_insert(data_path="location")
        bpy.context.scene.frame_set(original_frame) # move back to the original frame
        return {"FINISHED"}

def closest_point(cam1, cam2, point1, point2):
    """
    Produces the point closest to the lines formed from `cam1` to `point1` and from `cam2` to `point2`, and the total distance between this point and the lines.
    
    Reference: http://www.gbuffer.net/archives/361
    """
    dir1 = point1 - cam1
    dir2 = point2 - cam2
    dir3 = cam2 - cam1
    a = dir1 * dir1
    b = -dir1 * dir2
    c = dir2 * dir2
    d = dir3 * dir1
    e = -dir3 * dir2
    if abs((c * a) - (b ** 2)) < 0.0001: # lines are nearly parallel
        raise Exception("Lines are too close to parallel")
    extent1 = ((d * c) - (e * b)) / ((c * a) - (b ** 2))
    extent2 = (e - (b * extent1)) / c
    point1 = cam1 + (extent1 * dir1)
    point2 = cam2 + (extent2 * dir2)
    return (point1 + point2) / 2, (point1 - point2).magnitude

def add_object_button(self, context):
    self.layout.operator(ResolveCameraTracks.bl_idname,
        text="Reconstruct Camera Tracks", icon="PLUGIN")

def register():
    bpy.utils.register_class(ResolveCameraTracks)
    bpy.types.VIEW3D_MT_object.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(ResolveCameraTracks)
    bpy.types.VIEW3D_MT_object.remove(add_object_button)

if __name__ == "__main__":
    register()