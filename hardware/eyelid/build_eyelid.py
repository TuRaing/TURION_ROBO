"""
Simple eyelid/shutter flap for a blink mechanism -- InMoov has no eyelid
part of its own (only eyeball-rotation parts, which this build doesn't
use), so this is a custom design: a thin curved shell that pivots on a
hinge pin at the top and swings down to cover the eye opening.

Sized for a nominal 45mm eye opening (InMoov's own eyeball is ~40-45mm) --
EYE_DIAMETER below is the one constant to change once the real InMoov
eyeglass part is in hand and the exact socket size is measured.

Driven by one more MG90S servo (same pick as the jaw), via a small horn
tab molded into the hinge.
"""
import numpy as np
import trimesh

EYE_DIAMETER = 46.0          # mm, the opening the lid must fully cover
LID_RADIUS = EYE_DIAMETER / 2 + 3.0   # slight overlap margin
LID_THICKNESS = 1.8          # mm, thin shell -- light, easy for a small servo to move
HINGE_PIN_DIA = 2.0          # mm, fits a short length of 2mm steel rod
HORN_TAB_LEN = 12.0
HORN_TAB_WIDTH = 6.0
HORN_HOLE_DIA = 1.5          # for a small screw into the servo horn


def build_eyelid():
    # the lid itself: a half-dome (dish) shell, flat edge at the hinge (top),
    # curved down over the eye -- built as a UV sphere half, flattened
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=LID_RADIUS)
    # keep only the lower hemisphere (this becomes the domed lid surface)
    mask = sphere.vertices[:, 2] <= 0
    lower = sphere.copy()
    cutter = trimesh.creation.box(extents=[LID_RADIUS * 3, LID_RADIUS * 3, LID_RADIUS * 3])
    cutter.apply_translation([0, 0, LID_RADIUS * 1.5])
    lower = lower.difference(cutter)

    inner = trimesh.creation.icosphere(subdivisions=4, radius=LID_RADIUS - LID_THICKNESS)
    inner_cutter = cutter.copy()
    inner = inner.difference(inner_cutter)

    shell = lower.difference(inner)

    # trim to a half-dome (the lid swings from the top edge down over the eye,
    # so only need roughly the front half of the dome)
    front_cutter = trimesh.creation.box(extents=[LID_RADIUS * 3, LID_RADIUS * 3, LID_RADIUS * 3])
    front_cutter.apply_translation([0, LID_RADIUS * 1.5, 0])
    shell = shell.difference(front_cutter)

    # hinge pin holes along the top straight edge
    hinge = trimesh.creation.cylinder(radius=HINGE_PIN_DIA / 2, height=LID_RADIUS * 2 + 4, sections=16)
    rot = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    hinge.apply_transform(rot)
    hinge.apply_translation([0, 0, 0])
    shell_with_hinge_hole = shell.difference(hinge)

    # small horn tab sticking out from one end of the hinge edge, for the servo arm
    tab = trimesh.creation.box(extents=[HORN_TAB_WIDTH, HORN_TAB_LEN, LID_THICKNESS * 2])
    tab.apply_translation([LID_RADIUS - HORN_TAB_WIDTH / 2 + 2, HORN_TAB_LEN / 2, 0])
    combined = trimesh.boolean.union([shell_with_hinge_hole, tab])

    horn_hole = trimesh.creation.cylinder(radius=HORN_HOLE_DIA / 2, height=LID_THICKNESS * 4, sections=12)
    horn_hole.apply_translation([LID_RADIUS - HORN_TAB_WIDTH / 2 + 2, HORN_TAB_LEN - 3, 0])
    combined = combined.difference(horn_hole)

    return combined


def main():
    lid = build_eyelid()
    lid.export("eyelid.stl")
    print(f"Watertight: {lid.is_watertight}")
    print(f"Bounds (mm): {lid.bounds}")
    print(f"Estimated weight at 30% infill: {abs(lid.volume) / 1000 * 1.24 * 0.30:.2f} g")


if __name__ == "__main__":
    main()
