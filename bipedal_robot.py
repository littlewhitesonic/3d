"""
Modular Bipedal Robot — CadQuery Script
========================================
Adjust the SCALE variable (and individual dimensions below) to resize the
entire robot proportionally.  Every module returns a CadQuery Workplane object
so parts can be exported individually or assembled into a single compound.

Requirements:
    pip install cadquery
Export with:
    python bipedal_robot.py        # writes one STEP file per part + assembly
"""

import cadquery as cq
import os

# ─────────────────────────────────────────────
#  GLOBAL SCALE & DIMENSIONS  (edit here only)
# ─────────────────────────────────────────────
SCALE = 1.0            # multiply everything by this factor (e.g. 0.5 = half size)

# --- Torso ---
TORSO_W      = 60 * SCALE   # width  (X)
TORSO_D      = 40 * SCALE   # depth  (Y)
TORSO_H      = 80 * SCALE   # height (Z)

# --- Head ---
HEAD_R       = 22 * SCALE   # sphere radius

# --- Upper arm ---
UARM_R       = 8  * SCALE   # cylinder radius
UARM_L       = 50 * SCALE   # cylinder length (along Z when upright)

# --- Lower arm ---
LARM_R       = 7  * SCALE
LARM_L       = 45 * SCALE

# --- Upper leg ---
ULEG_R       = 11 * SCALE
ULEG_L       = 60 * SCALE

# --- Lower leg ---
LLEG_R       = 9  * SCALE
LLEG_L       = 55 * SCALE

# --- Foot (small flat box) ---
FOOT_W       = 28 * SCALE
FOOT_D       = 40 * SCALE
FOOT_H       = 12 * SCALE

# --- Joints ---
HOLE_R       = 1.5 * SCALE  # 3 mm diameter connection hole radius
HOLE_DEPTH   = 10  * SCALE  # blind-hole depth for peg connections

# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────

def _drill_hole(wp, axis="Z", depth=None):
    """Cut a centred peg-hole through/into the last solid along *axis*."""
    depth = depth or HOLE_DEPTH
    return wp.faces(f">{axis}").workplane().hole(HOLE_R * 2, depth)


# ─────────────────────────────────────────────
#  MODULE: TORSO
# ─────────────────────────────────────────────

def make_torso() -> cq.Workplane:
    """
    Box torso with:
      • top-centre hole  → neck joint
      • two shoulder holes (left / right faces) → arm joints
      • two hip holes (bottom face, offset) → leg joints
    """
    torso = (
        cq.Workplane("XY")
        .box(TORSO_W, TORSO_D, TORSO_H)
    )

    # Neck joint — top face, centre
    torso = (
        torso.faces(">Z").workplane()
        .hole(HOLE_R * 2, HOLE_DEPTH)
    )

    # Shoulder joints — left (+X) and right (-X) faces, mid-height
    for sign in (+1, -1):
        torso = (
            torso.faces(f"{'>' if sign > 0 else '<'}X").workplane()
            .hole(HOLE_R * 2, HOLE_DEPTH)
        )

    # Hip joints — bottom face, offset left and right
    hip_offset = TORSO_W * 0.25
    torso = (
        torso.faces("<Z").workplane()
        .pushPoints([(+hip_offset, 0), (-hip_offset, 0)])
        .hole(HOLE_R * 2, HOLE_DEPTH)
    )

    return torso


# ─────────────────────────────────────────────
#  MODULE: HEAD
# ─────────────────────────────────────────────

def make_head() -> cq.Workplane:
    """
    Sphere head with a bottom pole hole → neck joint.
    CadQuery doesn't have a native sphere workplane selector, so we subtract
    the hole via a positioned cylinder.
    """
    head = cq.Workplane("XY").sphere(HEAD_R)

    # Neck peg hole drilled from the bottom
    neck_hole = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, -HEAD_R))
        .circle(HOLE_R)
        .extrude(HOLE_DEPTH)
    )
    head = head.cut(neck_hole)
    return head


# ─────────────────────────────────────────────
#  MODULE: ARM  (upper + lower, mirrored by caller)
# ─────────────────────────────────────────────

def make_upper_arm() -> cq.Workplane:
    """
    Cylinder upper arm with:
      • top hole  → shoulder joint (connects to torso)
      • bottom hole → elbow joint (connects to lower arm)
    """
    arm = (
        cq.Workplane("XY")
        .cylinder(UARM_L, UARM_R)
    )
    # Shoulder hole — top
    arm = arm.faces(">Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    # Elbow hole — bottom
    arm = arm.faces("<Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    return arm


def make_lower_arm() -> cq.Workplane:
    """
    Cylinder lower arm with:
      • top hole  → elbow joint
      • bottom hole → wrist (open end)
    """
    arm = (
        cq.Workplane("XY")
        .cylinder(LARM_L, LARM_R)
    )
    arm = arm.faces(">Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    arm = arm.faces("<Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    return arm


# ─────────────────────────────────────────────
#  MODULE: LEG  (left / right share same geometry)
# ─────────────────────────────────────────────

def make_upper_leg() -> cq.Workplane:
    """
    Cylinder upper leg with:
      • top hole  → hip joint (connects to torso)
      • bottom hole → knee joint (connects to lower leg)
    """
    leg = (
        cq.Workplane("XY")
        .cylinder(ULEG_L, ULEG_R)
    )
    leg = leg.faces(">Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    leg = leg.faces("<Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    return leg


def make_lower_leg() -> cq.Workplane:
    """
    Cylinder lower leg with:
      • top hole → knee joint
      • bottom hole → ankle joint (connects to foot)
    """
    leg = (
        cq.Workplane("XY")
        .cylinder(LLEG_L, LLEG_R)
    )
    leg = leg.faces(">Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    leg = leg.faces("<Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    return leg


def make_foot() -> cq.Workplane:
    """
    Flat box foot with:
      • top-centre hole → ankle joint
    """
    foot = (
        cq.Workplane("XY")
        .box(FOOT_W, FOOT_D, FOOT_H)
    )
    foot = foot.faces(">Z").workplane().hole(HOLE_R * 2, HOLE_DEPTH)
    return foot


# ─────────────────────────────────────────────
#  ASSEMBLY  (positional, for visual preview)
# ─────────────────────────────────────────────

def assemble_robot() -> cq.Assembly:
    """
    Place every part in its approximate anatomical position.
    All Z values are relative to the torso centre at Z=0.
    """
    asm = cq.Assembly(name="BipedalRobot")

    # — Torso (origin) —
    asm.add(make_torso(), name="torso", loc=cq.Location(cq.Vector(0, 0, 0)))

    # — Head (sit on top of torso) —
    head_z = TORSO_H / 2 + HEAD_R + 2 * SCALE
    asm.add(make_head(), name="head",
            loc=cq.Location(cq.Vector(0, 0, head_z)))

    # — Arms —
    arm_x   = TORSO_W / 2 + UARM_R + 2 * SCALE   # just outside shoulder
    arm_z   =  TORSO_H / 2 - UARM_L / 2           # hang from shoulder height

    asm.add(make_upper_arm(), name="upper_arm_L",
            loc=cq.Location(cq.Vector(+arm_x, 0, arm_z)))
    asm.add(make_lower_arm(), name="lower_arm_L",
            loc=cq.Location(cq.Vector(+arm_x, 0, arm_z - UARM_L / 2 - LARM_L / 2)))

    asm.add(make_upper_arm(), name="upper_arm_R",
            loc=cq.Location(cq.Vector(-arm_x, 0, arm_z)))
    asm.add(make_lower_arm(), name="lower_arm_R",
            loc=cq.Location(cq.Vector(-arm_x, 0, arm_z - UARM_L / 2 - LARM_L / 2)))

    # — Legs —
    hip_offset = TORSO_W * 0.25
    leg_z      = -(TORSO_H / 2 + ULEG_L / 2)      # hang below torso

    for side, sign in (("L", +1), ("R", -1)):
        lx = sign * hip_offset

        asm.add(make_upper_leg(), name=f"upper_leg_{side}",
                loc=cq.Location(cq.Vector(lx, 0, leg_z)))

        knee_z = leg_z - ULEG_L / 2 - LLEG_L / 2
        asm.add(make_lower_leg(), name=f"lower_leg_{side}",
                loc=cq.Location(cq.Vector(lx, 0, knee_z)))

        ankle_z = knee_z - LLEG_L / 2 - FOOT_H / 2
        asm.add(make_foot(), name=f"foot_{side}",
                loc=cq.Location(cq.Vector(lx, 0, ankle_z)))

    return asm


# ─────────────────────────────────────────────
#  EXPORT
# ─────────────────────────────────────────────

def export_all(out_dir: str = "robot_parts"):
    os.makedirs(out_dir, exist_ok=True)

    parts = {
        "torso":         make_torso(),
        "head":          make_head(),
        "upper_arm":     make_upper_arm(),
        "lower_arm":     make_lower_arm(),
        "upper_leg":     make_upper_leg(),
        "lower_leg":     make_lower_leg(),
        "foot":          make_foot(),
    }

    for name, part in parts.items():
        path = os.path.join(out_dir, f"{name}.step")
        cq.exporters.export(part, path)
        print(f"  ✓  {path}")

    asm = assemble_robot()
    asm_path = os.path.join(out_dir, "robot_assembly.step")
    asm.save(asm_path)
    print(f"  ✓  {asm_path}  (full assembly)")


if __name__ == "__main__":
    print(f"\nExporting bipedal robot at SCALE={SCALE} …\n")
    export_all()
    print("\nDone!  Open the STEP files in FreeCAD, Fusion 360, or any slicer.\n")
