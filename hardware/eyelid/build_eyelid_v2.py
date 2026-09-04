"""
Eyelid blink mechanism v2 -- ONE shared MG90S servo drives BOTH eyelids
together via a crossbar link (real eyes always blink in sync, so no need
for 2 servos). Produces 5 parts:

  EyelidLeft.stl / EyelidRight.stl   -- the curved flap over each eye
  HingeAnchorLeft.stl / HingeAnchorRight.stl -- small brackets, glued/
      screwed inside the head, that hold each eyelid's hinge pin so it
      can pivot
  ServoBracket.stl -- holds the MG90S between the two eyes, servo horn
      facing forward
  Crossbar.stl -- rigid link from the servo horn to both eyelid tabs;
      one servo sweep pulls both lids shut, spring-back (or reverse
      sweep) opens them

EYE_SPACING below is an estimate (InMoov's EyeglassV4 part measures
~130mm wide overall) -- refine once the real InMoov eyeglass part is
in hand and eye-socket centers are measured directly.

All units mm. Servo: MG90S (already the blink-servo pick).
"""
import numpy as np
import trimesh

EYE_DIAMETER = 46.0
LID_RADIUS = EYE_DIAMETER / 2 + 3.0
LID_THICKNESS = 1.8
HINGE_PIN_DIA = 2.0
HORN_TAB_LEN = 12.0
HORN_TAB_WIDTH = 6.0
HORN_HOLE_DIA = 1.5

EYE_SPACING = 65.0  # center-to-center, estimate -- refine against the real InMoov part
SERVO_BODY = (23.0, 12.2, 24.0)  # MG90S body footprint, mm (W x D x H), approx


def half_dome_shell(radius, thickness, keep_front=True):
    outer = trimesh.creation.icosphere(subdivisions=4, radius=radius)
    top_cut = trimesh.creation.box(extents=[radius * 3, radius * 3, radius * 3])
    top_cut.apply_translation([0, 0, radius * 1.5])
    outer = outer.difference(top_cut)

    inner = trimesh.creation.icosphere(subdivisions=4, radius=radius - thickness)
    inner = inner.difference(top_cut.copy())

    shell = outer.difference(inner)

    side_cut = trimesh.creation.box(extents=[radius * 3, radius * 3, radius * 3])
    side_cut.apply_translation([0, radius * 1.5 * (1 if keep_front else -1), 0])
    shell = shell.difference(side_cut)
    return shell


def build_eyelid(mirror: bool):
    shell = half_dome_shell(LID_RADIUS, LID_THICKNESS)

    hinge = trimesh.creation.cylinder(radius=HINGE_PIN_DIA / 2, height=LID_RADIUS * 2 + 4, sections=16)
    rot = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    hinge.apply_transform(rot)
    shell = shell.difference(hinge)

    side = -1 if mirror else 1
    tab = trimesh.creation.box(extents=[HORN_TAB_WIDTH, HORN_TAB_LEN, LID_THICKNESS * 2])
    tab.apply_translation([side * (LID_RADIUS - HORN_TAB_WIDTH / 2 + 2), HORN_TAB_LEN / 2, 0])
    combined = trimesh.boolean.union([shell, tab])

    horn_hole = trimesh.creation.cylinder(radius=HORN_HOLE_DIA / 2, height=LID_THICKNESS * 4, sections=12)
    horn_hole.apply_translation([side * (LID_RADIUS - HORN_TAB_WIDTH / 2 + 2), HORN_TAB_LEN - 3, 0])
    combined = combined.difference(horn_hole)
    return combined


def build_hinge_anchor():
    """A small bracket with a hole for the hinge pin, meant to be glued/
    screwed to the inside of the head shell just above each eye socket."""
    base = trimesh.creation.box(extents=[10, 6, 4])
    hole = trimesh.creation.cylinder(radius=HINGE_PIN_DIA / 2 + 0.2, height=10, sections=16)
    rot = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    hole.apply_transform(rot)
    hole.apply_translation([0, 0, 0])
    return base.difference(hole)


def build_servo_bracket():
    """A simple open-frame cradle for the MG90S body, mounted between the
    two eyes, servo horn facing forward toward the crossbar."""
    w, d, h = SERVO_BODY
    wall = 2.0
    outer = trimesh.creation.box(extents=[w + wall * 2, d + wall * 2, h + wall])
    cavity = trimesh.creation.box(extents=[w, d, h + wall * 2])
    cavity.apply_translation([0, 0, wall])
    bracket = outer.difference(cavity)
    # open the front face so the servo horn can stick out
    front_open = trimesh.creation.box(extents=[w * 0.6, wall * 3, h * 0.6])
    front_open.apply_translation([0, -(d / 2 + wall / 2), h * 0.1])
    bracket = bracket.difference(front_open)
    return bracket


def build_crossbar():
    """Rigid link from the servo horn to both eyelid horn tabs. A shallow
    'V' / T-shape: center hole for the servo horn, two end holes that pin
    to each eyelid's horn tab."""
    half_span = EYE_SPACING / 2 - 5
    bar = trimesh.creation.box(extents=[half_span * 2 + 6, 5, 2])
    center_hole = trimesh.creation.cylinder(radius=HORN_HOLE_DIA / 2, height=6, sections=12)
    bar = bar.difference(center_hole)
    for side in (-1, 1):
        hole = trimesh.creation.cylinder(radius=HORN_HOLE_DIA / 2, height=6, sections=12)
        hole.apply_translation([side * half_span, 0, 0])
        bar = bar.difference(hole)
    return bar


def main():
    parts = {
        "EyelidLeft": build_eyelid(mirror=False),
        "EyelidRight": build_eyelid(mirror=True),
        "HingeAnchorLeft": build_hinge_anchor(),
        "HingeAnchorRight": build_hinge_anchor(),
        "ServoBracket": build_servo_bracket(),
        "Crossbar": build_crossbar(),
    }
    total_g = 0.0
    for name, mesh in parts.items():
        mesh.export(f"{name}.stl")
        vol_cm3 = abs(mesh.volume) / 1000.0
        weight_g = vol_cm3 * 1.24 * 0.30
        total_g += weight_g
        print(f"{name:<18} watertight={mesh.is_watertight!s:<6} weight~{weight_g:.2f}g")
    print(f"\nTotal estimated PLA weight (30% infill): {total_g:.1f} g")


if __name__ == "__main__":
    main()
