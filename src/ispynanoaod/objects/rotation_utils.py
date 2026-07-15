"""
Absolute-rotation helpers for pythreejs Object3D-derived widgets.

pythreejs' relative rotation methods (.rotateX(), .rotateY(), .rotateZ(), ...)
are sent to the frontend as fire-and-forget imperative comm messages
(exec_three_obj_method), distinct from regular synced state traits like
.position or .quaternion. On Google Colab's custom widget manager these
imperative messages are unreliably delivered/ordered, so relative rotations
can silently compound or get dropped across repeated calls on a persistent
object (e.g. reloading a new event). Regular state traits sync correctly
there, so orientations must be computed as an absolute quaternion and
assigned directly.
"""

import numpy as np


def direction_to_quaternion(v_from, v_to):
    """
    Absolute (x, y, z, w) quaternion that rotates unit vector `v_from` onto
    unit vector `v_to` (shortest-arc rotation), as a plain list.

    For axially symmetric geometry (cylinders, cones), this fully
    determines the visible orientation: rotation about the aligned axis
    itself ("roll") is not visually distinguishable for such shapes.
    """
    v_from = np.asarray(v_from, dtype=float)
    v_to = np.asarray(v_to, dtype=float)
    v_from = v_from / np.linalg.norm(v_from)
    v_to = v_to / np.linalg.norm(v_to)

    dot = np.dot(v_from, v_to)

    if dot < -1.0 + 1e-8:
        # v_from and v_to are opposite: dot/cross alone can't determine an
        # axis, so pick any axis perpendicular to v_from for a 180-degree
        # rotation.
        axis = np.cross([1.0, 0.0, 0.0], v_from)
        if np.linalg.norm(axis) < 1e-8:
            axis = np.cross([0.0, 1.0, 0.0], v_from)
        axis = axis / np.linalg.norm(axis)
        return [axis[0], axis[1], axis[2], 0.0]

    axis = np.cross(v_from, v_to)
    q = np.array([axis[0], axis[1], axis[2], 1.0 + dot])
    q = q / np.linalg.norm(q)
    return q.tolist()
