// ============================================================
//  MODULAR BIPEDAL ROBOT — OpenSCAD
//  All dimensions are in mm at scale = 1.0
//  Increase/decrease `scale_factor` to resize the whole robot.
// ============================================================

// ── Global scale ────────────────────────────────────────────
scale_factor = 1.0;   // Change this to resize everything

// ── Joint hole ──────────────────────────────────────────────
hole_d        = 3.0;  // Connection-pin hole diameter (mm)
hole_depth    = 6.0;  // How deep each pin hole goes

// ── Torso ───────────────────────────────────────────────────
torso_w       = 40;
torso_h       = 50;
torso_d       = 20;

// ── Head ────────────────────────────────────────────────────
head_r        = 14;   // Sphere radius
neck_h        = 6;    // Gap between torso top and head centre

// ── Shoulder / Arm ──────────────────────────────────────────
arm_r         = 5;    // Cylinder radius
arm_len       = 40;   // Full arm length (upper + lower combined)
shoulder_offset_x = torso_w / 2 + arm_r; // flush with torso side

// ── Hip / Leg ────────────────────────────────────────────────
leg_r         = 7;    // Cylinder radius
leg_len       = 55;   // Full leg length
hip_spacing   = torso_w / 4; // lateral offset of each leg from centre

// ============================================================
//  HELPERS
// ============================================================

// A centred pin hole pointing along Z
module pin_hole(depth = hole_depth) {
    cylinder(h = depth * scale_factor,
             d = hole_d * scale_factor,
             center = true, $fn = 16);
}

// ============================================================
//  TORSO
// ============================================================
module torso() {
    s = scale_factor;
    tw = torso_w * s;
    th = torso_h * s;
    td = torso_d * s;

    difference() {
        // Body block, centred in X/Y, sitting on Z = 0
        translate([-tw/2, -td/2, 0])
            cube([tw, td, th]);

        // ── Neck socket (top centre) ──
        translate([0, 0, th])
            pin_hole();

        // ── Left shoulder socket ──
        translate([-tw/2, 0, th * 0.75])
            rotate([0, 90, 0])
                pin_hole();

        // ── Right shoulder socket ──
        translate([tw/2, 0, th * 0.75])
            rotate([0, 90, 0])
                pin_hole();

        // ── Left hip socket ──
        translate([-hip_spacing * s, 0, 0])
            rotate([0, 0, 0])
                pin_hole();

        // ── Right hip socket ──
        translate([hip_spacing * s, 0, 0])
            rotate([0, 0, 0])
                pin_hole();
    }
}

// ============================================================
//  HEAD
// ============================================================
module head() {
    s  = scale_factor;
    hr = head_r * s;
    nh = neck_h  * s;
    th = torso_h * s;

    translate([0, 0, th + nh + hr]) {
        difference() {
            sphere(r = hr, $fn = 48);

            // Neck pin hole downward
            translate([0, 0, -hr])
                pin_hole();
        }
    }
}

// ============================================================
//  ARM  (mirrored for left / right by caller)
// ============================================================
//   side = +1 for right, -1 for left
module arm(side = 1) {
    s   = scale_factor;
    ar  = arm_r   * s;
    al  = arm_len * s;
    tw  = torso_w * s;
    th  = torso_h * s;
    sox = shoulder_offset_x * s;

    // Position: shoulder sits at the side of the torso, 75 % up
    translate([side * sox, 0, th * 0.75]) {
        // Rotate so the cylinder runs along X (outward)
        rotate([0, 90, 0]) {
            difference() {
                cylinder(h = al, r = ar, center = false, $fn = 32);

                // Shoulder pin hole at base
                translate([0, 0, 0])
                    pin_hole();

                // Wrist pin hole at tip
                translate([0, 0, al])
                    pin_hole();
            }
        }
    }
}

// ============================================================
//  LEG  (mirrored for left / right by caller)
// ============================================================
//   side = +1 for right, -1 for left
module leg(side = 1) {
    s   = scale_factor;
    lr  = leg_r * s;
    ll  = leg_len * s;
    hs  = hip_spacing * s;

    // Legs hang below the torso (Z = 0 is torso bottom)
    translate([side * hs, 0, -ll]) {
        difference() {
            cylinder(h = ll, r = lr, center = false, $fn = 32);

            // Hip pin hole at top
            translate([0, 0, ll])
                pin_hole();

            // Ankle/foot pin hole at bottom
            translate([0, 0, 0])
                pin_hole();
        }
    }
}

// ============================================================
//  FOOT  (flat pad at the base of each leg)
// ============================================================
module foot(side = 1) {
    s   = scale_factor;
    lr  = leg_r   * s;
    ll  = leg_len * s;
    hs  = hip_spacing * s;

    fw = lr * 4;   // foot width
    fd = lr * 3;   // foot depth
    fh = lr * 1.2; // foot height

    translate([side * hs, 0, -(ll + fh)]) {
        difference() {
            translate([-fw/2, -fd/2, 0])
                cube([fw, fd, fh]);

            // Ankle pin hole on top
            translate([0, 0, fh])
                pin_hole();
        }
    }
}

// ============================================================
//  ASSEMBLE
// ============================================================
torso();
head();
arm(side =  1);   // right arm
arm(side = -1);   // left arm
leg(side =  1);   // right leg
leg(side = -1);   // left leg
foot(side =  1);  // right foot
foot(side = -1);  // left foot
