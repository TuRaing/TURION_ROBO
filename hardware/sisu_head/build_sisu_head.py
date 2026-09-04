"""
Sisu head shell -- parametric 3D model, exported as a printable STL.
Proportions lifted from the earlier Main.dc.html 2D concept (cream head,
teal eyes, amber ear-mics, mouth speaker grille), scaled to a real
16cm-tall head (within the builder's chosen 15-18cm range).

All units: millimetres.
"""
import numpy as np
import trimesh

# ---- overall head size (16cm tall, proportions from the 2D concept) ----
HEAD_H = 160.0          # top-to-bottom
HEAD_W = 112.0          # left-to-right   (0.7 x height, from the SVG rect)
HEAD_D = 90.0           # front-to-back
RX, RY, RZ = HEAD_W / 2, HEAD_D / 2, HEAD_H / 2
WALL_T = 2.5            # shell wall thickness

CENTER_Z = 0.0          # head vertical center
EYE_Z = 12.0            # eyes sit slightly above center
EYE_X = 20.0            # left/right offset from center
EYE_OUTER_R = 18.0      # eye socket radius (rim)
EYE_HOLE_R = 10.0       # through-hole radius (camera lens / dummy lens)

EAR_Z = -4.0
EAR_BUMP_R = 21.0
EAR_HOLE_R = 4.5         # mic hole

MOUTH_Z = -35.0
MOUTH_W = 32.0
MOUTH_H = 14.0

BOTTOM_OPEN_Z = -55.0    # everything below this Z is cut open (neck mount)


def ellipsoid(rx, ry, rz, subdivisions=4):
    m = trimesh.creation.icosphere(subdivisions=subdivisions, radius=1.0)
    m.apply_scale([rx, ry, rz])
    return m


def cyl_along_y(radius, length, center):
    """Cylinder whose axis runs front-to-back (Y), for eye/mouth cuts."""
    m = trimesh.creation.cylinder(radius=radius, height=length, sections=48)
    # cylinder() builds along Z by default -> rotate onto Y
    rot = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    m.apply_transform(rot)
    m.apply_translation(center)
    return m


def capsule_along_x(radius, length, center):
    """Horizontal capsule (mouth slot), axis along X, then we'll push it
    through the shell wall along Y."""
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=32)
    rot = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])
    cyl.apply_transform(rot)
    cap1 = trimesh.creation.icosphere(subdivisions=3, radius=radius)
    cap1.apply_translation([length / 2, 0, 0])
    cap2 = trimesh.creation.icosphere(subdivisions=3, radius=radius)
    cap2.apply_translation([-length / 2, 0, 0])
    m = trimesh.util.concatenate([cyl, cap1, cap2])
    m = trimesh.boolean.union([cyl, cap1, cap2])
    m.apply_translation(center)
    return m


def main():
    print("Building outer/inner shell...")
    outer = ellipsoid(RX, RY, RZ)
    inner = ellipsoid(RX - WALL_T, RY - WALL_T, RZ - WALL_T)
    shell = outer.difference(inner)

    print("Opening the bottom (neck mount)...")
    cutter = trimesh.creation.box(extents=[HEAD_W * 2, HEAD_D * 2, 200])
    cutter.apply_translation([0, 0, BOTTOM_OPEN_Z - 100])
    shell = shell.difference(cutter)

    print("Adding ear bumps...")
    front_y = -RY  # front face is -Y
    for side in (-1, 1):
        ear = trimesh.creation.icosphere(subdivisions=3, radius=EAR_BUMP_R)
        ear.apply_scale([1.0, 0.55, 1.0])  # flatten toward the head surface
        ear.apply_translation([side * RX, 0, EAR_Z])
        shell = trimesh.boolean.union([shell, ear])

    print("Cutting eye holes...")
    for side in (-1, 1):
        hole = cyl_along_y(EYE_HOLE_R, HEAD_D + 40, [side * EYE_X, 0, EYE_Z])
        shell = shell.difference(hole)

    print("Cutting ear mic holes...")
    for side in (-1, 1):
        hole = cyl_along_y(EAR_HOLE_R, HEAD_W + 80, [0, 0, EAR_Z])
        rot = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1])
        hole.apply_transform(rot)
        hole.apply_translation([side * RX, 0, 0])
        shell = shell.difference(hole)

    print("Cutting mouth slot...")
    mouth = capsule_along_x(MOUTH_H / 2, MOUTH_W, [0, 0, MOUTH_Z])
    mouth_through = cyl_along_y(MOUTH_H / 2 + 2, HEAD_D + 40, [0, 0, 0])
    # simpler: just push a flattened box+capsule straight through along Y
    mouth_cut = trimesh.creation.box(extents=[MOUTH_W, HEAD_D + 40, MOUTH_H])
    mouth_cut.apply_translation([0, 0, MOUTH_Z])
    shell = shell.difference(mouth_cut)

    print("Exporting...")
    shell.export("sisu_head.stl")
    print(f"Done. Watertight: {shell.is_watertight}  Volume(mm3): {shell.volume:.0f}")
    print(f"Bounds: {shell.bounds}")


if __name__ == "__main__":
    main()
