// =====================================================================
//  BEACON phone module - MagSafe enclosure with RX patch + TX monopole
//  VARIANT: 2.5 mm ring
//  REVISION: rev_pcb - copy of beacon_phone_magsafe_2p5mm_Latest.scad updated
//    to the final PCB parts (GCT USB4105-GF-A USB-C, Cinch 142-0711-821
//    end-launch SMA). Board outline, holes, TX notch, usb_x, tx_pos and
//    patch position are unchanged and match BEACON_PhoneModule.kicad_pcb.
//    See CHANGES.md next to this file.
//  Ring:    totalElement 54 x 46 x 2.5 mm N52 ring assembly with alignment magnet (listed 54.1 OD x 46 ID x 2.55 mm)
//  Defaults give 59.2 x 82.65 x 14.32 mm outside, a 55 x 78.45 mm board, snap-fit lid, PCB on 4x M2 x 4 pan-head screws into heat-set inserts.
//
//  Built to totalElement's MagSafe installation guide:
//   - magnet side toward the phone, steel backing away
//   - clocking magnet upright at 6 o'clock, centred, top edge 31.2 mm
//     below the ring centre (about 4.1 mm below the ring)
//   - protective layer 0.5-0.8 mm, the guide's "works well for 3D
//     printed parts" band. The skin here is an exact stack of printed
//     layers: first_layer_h + (skin_layers - 1) * layer_h = 0.68 mm
//     with Bambu's "0.12mm Fine" profile (0.20 first layer + 4 x 0.12).
//     An assert stops the render outside 0.5-0.8 mm. The slicer profile
//     must match first_layer_h / layer_h or the skin and pause height
//     will be wrong. For 0.20 mm Standard: layer_h 0.20, skin_layers 3,
//     cap_layers 3, mag_clr_z 0.15.
//
//  Print-in-place magnets
//   The ring and clocking bar are sealed inside the base. Add a pause in
//   the slicer at the height printed in the console ("PAUSE"); at the
//   pause the pockets are open, drop the magnets in and resume. The next
//   cap_layers bridge over them. The skin under them is unchanged.
//
//  Antennas
//   RX: Taoglas WDP.2458.25.4.B.02, 25 x 25 x 4 mm pin-fed ceramic
//       patch, taped to the board's top side so the board ground is its
//       ground plane. The lid keeps an air gap over it and is thinned to
//       a radome there (patch_window = true opens it instead).
//   TX: Taoglas GW.26.0111, 2.4 GHz monopole with an SMA(M) plug, on a
//       Cinch (Johnson) 142-0711-821 end-launch SMA(F) jack (standard
//       SMA, not RP-SMA; 0.250 in square x 0.065 in flange) at the board
//       edge. The barrel runs out through a U-slot in the side wall, the
//       jack body bears on the inside of the wall (the board is notched
//       for it), and a tongue on the lid closes the slot. On the default
//       right-hand wall the radiating part sits past the phone's edge
//       instead of lying a few mm over the phone's metal.
//
//  Parts
//   base : phone-side tray. Ring and clocking magnet are sealed in at a
//          print pause, magnet side down onto the skin. Four PCB
//          standoffs take M2 heat-set inserts. U-shaped USB-C opening
//          in the bottom (-Y) wall, toward the phone's own USB-C port;
//          the lid closes its top so it prints without bridging. U-slot
//          for the TX jack in a side wall.
//          The PCB screws straight down into the inserts with four small
//          M2 pan/cheese-head screws, independent of the lid.
//   lid  : snap-fit back cover. Its perimeter lip carries 45 degree beads
//          that click into matching grooves in the base walls; no lid
//          screws. Patch radome and the tongue that closes the TX slot.
//          A notch in the bottom wall gives a spudger or fingernail a
//          place to lever it off.
//
//  Coordinates (assembled): origin = ring centre on the phone-contact
//  face. +Y toward the top of the phone, -Y toward the bottom (USB-C,
//  clocking magnet), +X to the right seen from the back of the phone
//  (camera bump top-left). +Z away from the phone. Board coordinates
//  (pcb_holes, patch_pos, tx_pos, DXF export) start at the board's
//  lower-left corner seen from the component side, USB-C edge at the
//  bottom.
//
//  Print: part = "print_plate", no supports. Base prints phone face
//  down, lid prints outer face down. Match first_layer_h / layer_h to
//  your slicer profile. Use PETG rather than PLA (the RF chain heats a
//  closed box against a warm phone). Not ABS/ASA: their 90-100 C bed
//  would sit right under the magnets, and N52 is rated to 80 C (thin,
//  low-permeance magnets lose flux lower still). Drop the bed to about
//  60 C at the pause (custom G-code M140 S60 on the pause layer). No
//  metal- or carbon-filled filament (non-ferrous housing, and both
//  antennas want a plain dielectric over them).
//  Print the LID in light-coloured PETG (white or natural, no dark or
//  pigment-heavy colours): in full sun at 35 C a dark lid reaches about
//  78 C, at PETG's softening point (HDT ~70 C, the snap beads and insert
//  bosses creep), against about 50 C for a white lid (docs/
//  magnetics_thermal.md section 4). Optional lid vent slots: vent_slots
//  below (default off), placed over the LMX2582 and away from both
//  antennas.
//
//  Assembly
//   1. Before printing: let the clocking bar snap onto the back of the
//      phone just below the ring and mark the face pointing away from
//      the phone. It can't be flipped once it is sealed in.
//   2. At the pause: ring magnet side down, steel up, into the annular
//      pocket (the island text reads MAGNETS DOWN / STEEL UP); bar marked
//      side up. A dot of CA in each pocket keeps them from lifting toward
//      the nozzle. Nothing may stand above the pocket tops. Resume.
//   3. After the print: heat-set the four M2 x 3 inserts flush with the
//      standoff tops. Work quickly; the magnets are about 7 mm away.
//   4. PCB onto the standoffs: USB-C at the bottom opening, SMA barrel
//      down the side slot. 4x M2 pan-head screws (length printed in the
//      console) through the board into the inserts.
//   5. Press the lid on until the beads click (its tongue drops into the
//      TX slot), then screw the GW.26.0111 onto the jack. To open, lever
//      at the notch in the bottom wall.
//
//  The console ECHO lists outside size, board outline, hole positions,
//  antenna positions and screw length. part = "pcb_outline" renders the
//  board shape, jack notch included, for DXF export (F6, then Export as
//  DXF) into Altium/KiCad.
// =====================================================================

/* [Render] */
part    = "print_plate"; // [print_plate, base, lid, assembly, section, pcb_outline]
explode = 18;            // lid lift in the assembly view, mm

/* [Layer stack - match your slicer profile] */
first_layer_h = 0.20;
layer_h       = 0.12;    // Bambu 0.12mm Fine
skin_layers   = 5;       // printed layers between the magnets and the phone (0.68 mm)

/* [MagSafe ring] */
ring_od = 54.1;
ring_id = 46.0;
ring_t  = 2.55;

/* [Clocking (alignment) magnet] */
use_clock = true;
clock_w   = 6.0;         // Apple reference size from the guide; measure yours
clock_l   = 19.3;
clock_t   = 2.55;  // pocket depth covers the thicker of ring and bar
clock_top = 31.2;        // ring centre to the bar's top edge

/* [Magnet fit] */
mag_clr    = 0.15;       // radial clearance on ring OD, ring ID and bar sides
mag_clr_z  = 0.25;       // min headroom over the magnets at the pause height
cap_layers = 5;          // layers printed over the magnets after the pause (0.60 mm)
mag_margin = 0.6;        // floor between a pocket and the cavity wall

/* [PCB] */
pcb_w       = 0;         // X size; 0 = auto, largest board the cavity allows
pcb_l       = 0;         // Y size; 0 = auto
pcb_t       = 1.6;
pcb_r       = 3.0;       // board corner radius
pcb_x_off   = 0;         // board centre offset in X
pcb_clr     = 0.3;       // board edge to cavity wall
pcb_gap     = 1.5;       // min space under the board (THT legs, bottom parts)
top_parts_h = 3.35;      // tallest top-side part (GCT USB4105-GF-A 3.31; was 3.3)
hole_inset  = 3.5;       // auto hole pattern: hole centre to board edges
pcb_hole_d  = 2.2;       // board hole, used by the DXF export
pcb_holes   = [];        // [] = 4 corner holes; else [[x, y], ...] in board coords

/* [Fasteners] */
fastener      = "insert"; // [insert, selftap]
insert_d      = 3.2;     // hole for an M2 x 3 heat-set insert (OD ~3.6)
insert_len    = 3.0;
selftap_d     = 1.7;     // pilot for an M2 thread-forming screw
floor_web     = 1.0;     // plastic kept under any hole, above the phone face
standoff_d    = 6.0;
screw_head_d  = 3.8;     // M2 pan / cheese head, for clearance checks + preview
screw_head_h  = 1.6;

/* [USB-C: GCT USB4105-GF-A, drawing rev B4] */
usb_x        = 0;        // receptacle centre in X (board x 27.5; KiCad J1 origin 3.675 inside the edge)
usb_z_on_pcb = 1.73;     // receptacle centreline above the board top (GCT; was 1.63)
usb_open_w   = 12.6;     // sized for the cable overmold (spec max 12.35 x 6.5)
usb_open_h   = 6.7;
usb_open_r   = 1.5;
usb_body     = [8.94, 7.35, 3.31]; // receptacle W x L x H (GCT; was 8.94 x 7.3 x 3.26)
usb_overhang = 0;        // receptacle front past the board edge, preview only

/* [Shell] */
wall_t       = 1.8;
lid_t        = 1.6;
lip_h        = 3.0;      // lid lip depth into the base (carries the snap beads)
lip_t        = 1.2;
lip_clr      = 0.2;
seam_gap     = 0;        // lid plate sits on the wall tops
edge_chamfer = 0.4;
label        = true;     // deboss MAGNETS DOWN / STEEL UP inside the ring

/* [Snap fit] */
snap_p      = 0.45;      // bead protrusion from the lip face (45 deg flanks);
                         //   interference = snap_p - lip_clr. Raise for a
                         //   firmer click, lower if it is hard to open.
snap_len    = 12;        // length of each bead / groove
snap_clr    = 0.1;       // extra groove depth over the bead
snap_side_y = [-32, -2]; // bead centres on the left and right walls (ring-centre y)
snap_top_x  = [0];       // bead centres on the top wall (ring-centre x)
snap_bot_x  = [];        // bottom wall beads (USB-C sits mid-wall)
pry_notch   = true;      // lever notch in the bottom wall's outer top edge
pry_x       = 16;        // its centre (ring-centre x)
pry_w       = 8;

/* [RX patch: Taoglas WDP.2458.25.4.B.02] */
use_patch    = true;
patch_pos    = [];       // [] = board centre; else [x, y] in board coords
patch_sz     = 25.1;     // square, +/-0.3
patch_tol    = 0.3;
patch_h      = 4.1;      // 4.0 +/-0.1
patch_tape   = 0.3;      // adhesive under the patch (datasheet: 0.5 max)
patch_pin    = 2.8;      // feed pin length, 2.4 +/-0.4, checked against the floor
patch_gap    = 1.0;      // air between the patch top and the lid underside
patch_cover  = 1.2;      // lid thickness left over the patch (radome)
patch_margin = 1.5;      // radome recess margin around the patch
patch_window = false;    // true = open window in the lid over the patch

/* [TX antenna: Taoglas GW.26.0111 on a Cinch 142-0711-821 end-launch SMA(F) jack] */
use_tx      = true;
tx_side     = "right";   // [right, left, top, bottom]
tx_pos      = 66;        // jack centre along that board edge, board coords
                         //   (y for right/left, x for top/bottom)
sma_axis_z  = 0.4;       // barrel axis above the board top. Cinch 142-0711-821:
                         //   ~0.4 (0.38-0.55, derived from the drawing, not
                         //   dimensioned; was 0.7). Measure the first jack.
sma_thread  = 6.35;      // 1/4"-36 UNS barrel
sma_clr     = 0.25;      // diametral clearance on the barrel (was 0.5): 0.125
                         //   radial; gives ~27 % more flange bearing on the
                         //   wall + tongue (6.6 vs 5.2 mm2). Go back to 0.4-0.5
                         //   if the measured axis sits above ~0.5.
sma_body    = [6.35, 1.65, 6.35];  // flange: 0.250 in sq x 0.065 in (was 6.5 x 1.6 x 6.5)
sma_barrel  = 7.87;      // barrel out from the flange front face (was 7.0)
tongue_clr  = 0.15;      // lid tongue side clearance in the slot
// Board notch, pinned to the KiCad Edge.Cuts (1.5 deep x 7.1 wide, board
// y 62.45-69.55). 0 = auto from sma_body (original formula: depth
// sma_body[1] + 0.2 - tx_gap, width sma_body[0] + 0.6), which for the Cinch
// flange would give 1.55 x 6.95 and no longer match the routed board.
tx_notch_d  = 1.5;
tx_notch_w  = 7.1;

/* [Lid vents (optional)] */
vent_slots  = false;     // through-slots in the lid plate; default off
vent_c      = [22, 65];  // slot-group centre, board coords (over U8 LMX2582
                         //   at board (22.6, 67.25), clear of the patch radome
                         //   and >= vent_keep from the TX jack)
vent_n      = 4;         // number of slots
vent_len    = 20;        // slot length (along X)
vent_w      = 1.2;       // slot width
vent_pitch  = 3.0;       // slot centre spacing (along Y)
vent_keep   = 10;        // min distance from the TX jack body (radome: 3 mm)

/* [Hidden] */
screw_lengths = [3, 4, 5, 6, 8, 10];  // stock M2 pan-head lengths
$fa = 2;
$fs = 0.3;
eps = 0.01;

// ---------------------------------------------------------------------
// Derived values
// ---------------------------------------------------------------------
function snap_up(z) = z <= first_layer_h ? first_layer_h
    : first_layer_h + ceil((z - first_layer_h) / layer_h - 1e-6) * layer_h;
function r2(x) = round(x * 100) / 100;
function rect_dist(p, a, b) =
    norm([max(a[0] - p[0], 0, p[0] - b[0]), max(a[1] - p[1], 0, p[1] - b[1])]);
function rects_hit(a0, a1, b0, b1, m) = a0[0] < b1[0] + m && b0[0] < a1[0] + m
                                     && a0[1] < b1[1] + m && b0[1] < a1[1] + m;
// side s: 0 top, 1 right, 2 bottom, 3 left. side_pt/side_ang give a local
// frame on the inner wall face: x along the wall, y = 0 at the face, +y out.
function side_pt(s, p) = s == 0 ? [p, cav_y1] : s == 1 ? [cav_x, p]
                       : s == 2 ? [p, cav_y0] : [-cav_x, p];
function side_ang(s)   = [0, -90, 180, 90][s];
function side_run(s)   = (s == 0 || s == 2) ? [-cav_x + cav_r, cav_x - cav_r]
                                            : [cav_y0 + cav_r, cav_y1 - cav_r];

// layer stack and magnet pockets
skin_t  = first_layer_h + (skin_layers - 1) * layer_h;
mag_t   = max(ring_t, use_clock ? clock_t : 0);
z_pause = snap_up(skin_t + mag_t + mag_clr_z);   // pocket tops: pause here
z_floor = z_pause + cap_layers * layer_h;          // sealed floor top
pause_layer = 1 + round((z_pause - first_layer_h) / layer_h);   // last layer before the pause
ring_ro = ring_od / 2 + mag_clr;
ring_ri = ring_id / 2 - mag_clr;
clk_x0  = -clock_w / 2 - mag_clr;
clk_x1  =  clock_w / 2 + mag_clr;
clk_y1  = -clock_top + mag_clr;                  // end nearest the ring
clk_y0  = -clock_top - clock_l - mag_clr;

// cavity: set by the magnets, grown if the board needs more room
env_x  = ring_ro + mag_margin;
env_y1 = ring_ro + mag_margin;
env_y0 = (use_clock ? clk_y0 : -ring_ro) - mag_margin;
cav_y0 = env_y0;
pcb_y0 = cav_y0 + pcb_clr;                       // USB-C edge at the bottom wall
pcb_W  = pcb_w > 0 ? pcb_w : 2 * (env_x - pcb_clr);
pcb_L  = pcb_l > 0 ? pcb_l : (env_y1 - pcb_clr) - pcb_y0;
pcb_x0 = pcb_x_off - pcb_W / 2;
cav_x  = max(env_x, abs(pcb_x_off) + pcb_W / 2 + pcb_clr);
cav_y1 = max(env_y1, pcb_y0 + pcb_L + pcb_clr);
cav_r  = max(pcb_r + pcb_clr, 1.0);
out_x  = cav_x + wall_t;
out_y0 = cav_y0 - wall_t;
out_y1 = cav_y1 + wall_t;
out_r  = cav_r + wall_t;

// mounting holes: board coords -> enclosure coords
holes_pcb = len(pcb_holes) > 0 ? pcb_holes
    : [[hole_inset, hole_inset], [pcb_W - hole_inset, hole_inset],
       [hole_inset, pcb_L - hole_inset], [pcb_W - hole_inset, pcb_L - hole_inset]];
holes = [for (h = holes_pcb) [pcb_x0 + h[0], pcb_y0 + h[1]]];

// Z stack (inserts need insert_len + 0.4 of hole plus floor_web under it)
hole_d     = fastener == "insert" ? insert_d : selftap_d;
z_pcb_bot  = snap_up(fastener == "insert"
                 ? max(z_floor + pcb_gap, insert_len + 0.4 + floor_web)
                 : z_floor + pcb_gap);
z_hole_bot = fastener == "insert" ? z_pcb_bot - (insert_len + 0.4) : floor_web;
z_pcb_top  = z_pcb_bot + pcb_t;
usb_zc     = z_pcb_top + usb_z_on_pcb;
usb_z0     = usb_zc - usb_open_h / 2;
// antennas: board coords -> enclosure coords
patch_c    = len(patch_pos) > 0 ? patch_pos : [pcb_W / 2, pcb_L / 2];
patch_xy   = [pcb_x0 + patch_c[0], pcb_y0 + patch_c[1]];
patch_fp   = patch_sz + patch_tol;               // worst-case footprint
radome_w   = patch_fp + 2 * patch_margin;
patch_stack = patch_tape + patch_h;
tx_s       = tx_side == "top" ? 0 : tx_side == "right" ? 1 : tx_side == "bottom" ? 2 : 3;
tx_along   = (tx_s == 1 || tx_s == 3) ? pcb_y0 + tx_pos : pcb_x0 + tx_pos;
tx_gap     = tx_s == 0 ? cav_y1 - (pcb_y0 + pcb_L) : tx_s == 1 ? cav_x - (pcb_x0 + pcb_W)
           : tx_s == 2 ? pcb_y0 - cav_y0 : pcb_x0 + cav_x;   // board edge to wall
tx_jw      = sma_body[0] / 2;
tx_jt      = sma_body[1];
tx_notch   = tx_notch_d > 0 ? tx_notch_d : tx_jt + 0.2 - tx_gap;   // jack body cut into the board edge
tx_nw      = tx_notch_w > 0 ? tx_notch_w / 2 : tx_jw + 0.3;        // notch half-width
sma_z      = z_pcb_top + sma_axis_z;
sma_hole   = sma_thread + sma_clr;
jack_a     = tx_s == 0 ? [tx_along - tx_jw, cav_y1 - tx_jt] : tx_s == 1 ? [cav_x - tx_jt, tx_along - tx_jw]
           : tx_s == 2 ? [tx_along - tx_jw, cav_y0]         : [-cav_x, tx_along - tx_jw];
jack_b     = tx_s == 0 ? [tx_along + tx_jw, cav_y1]         : tx_s == 1 ? [cav_x, tx_along + tx_jw]
           : tx_s == 2 ? [tx_along + tx_jw, cav_y0 + tx_jt] : [-cav_x + tx_jt, tx_along + tx_jw];
top_clear  = max(top_parts_h + 0.5, usb_zc + usb_open_h / 2 - z_pcb_top,
                 use_patch ? patch_stack + patch_gap : 0,
                 use_tx ? sma_axis_z + sma_body[2] / 2 + 0.5 : 0);
z_seam     = z_pcb_top + top_clear;              // lid underside
z_wall     = z_seam - seam_gap;                  // base wall top
z_top      = z_seam + lid_t;

// PCB screws: longest stock length (under the head) through the board
// whose tip stops 0.3 mm above the bottom of the insert / pilot hole
tip_z       = z_hole_bot + 0.3;
fits        = [for (l = screw_lengths) if (l <= z_pcb_top - tip_z) l];
screw_L     = len(fits) > 0 ? max(fits) : 0;
engage      = screw_L - pcb_t;                   // thread below the board

// snap fit: beads on the lid lip, grooves in the base walls
snap_z  = z_seam - lip_h + 0.4 + snap_p;         // bead centre height
snap_gd = snap_p - lip_clr + snap_clr;           // groove depth into the wall
snaps   = concat([for (y = snap_side_y) [1, y]], [for (y = snap_side_y) [3, y]],
                 [for (x = snap_top_x) [0, x]], [for (x = snap_bot_x) [2, x]]);

// optional lid vents: board coords -> enclosure coords
vent_xy = [pcb_x0 + vent_c[0], pcb_y0 + vent_c[1]];
vent_ys = [for (i = [0 : max(vent_n, 1) - 1]) vent_xy[1] + (i - (vent_n - 1) / 2) * vent_pitch];
vent_a  = [vent_xy[0] - vent_len / 2, vent_xy[1] - ((vent_n - 1) * vent_pitch + vent_w) / 2];
vent_b  = [vent_xy[0] + vent_len / 2, vent_xy[1] + ((vent_n - 1) * vent_pitch + vent_w) / 2];

// ---------------------------------------------------------------------
// Design checks
// ---------------------------------------------------------------------
assert(skin_t >= 0.5 - 1e-6 && skin_t <= 0.8 + 1e-6,
    str("Skin over the magnets is ", r2(skin_t),
        " mm; totalElement's 3D-print band is 0.5-0.8 mm. Change skin_layers."));
assert(pcb_W > 0 && pcb_L > 0, "PCB size must be positive");
assert(z_pause - skin_t - mag_t >= 0.1 - 1e-6,
    "Magnets would stand above the pause layer; raise mag_clr_z");
assert(cap_layers >= 2, "Use at least 2 cap layers over the magnets (the first one is a bridge)");
assert(screw_L > 0, "No stock screw length fits; extend screw_lengths");
assert(engage >= 1.5, "Less than 1.5 mm of PCB screw thread below the board");
assert(z_pcb_top + screw_head_h + 0.3 <= z_seam - lip_h || screw_head_h + 0.3 <= top_clear,
    "PCB screw heads hit the lid");
assert(snap_p > lip_clr, "snap_p must exceed lip_clr or the beads never engage");
assert(snap_z + snap_gd + 1.0 <= z_wall, "Snap grooves too close to the wall top; increase lip_h");
assert(snap_gd <= wall_t - 1.0, "Snap grooves leave less than 1 mm of wall");
for (s = snaps) {
    assert(s[1] - snap_len / 2 - 0.5 >= side_run(s[0])[0] && s[1] + snap_len / 2 + 0.5 <= side_run(s[0])[1],
        str("Snap bead ", s, " runs onto a corner radius"));
    assert(!use_tx || s[0] != tx_s || abs(s[1] - tx_along) >= snap_len / 2 + max(tx_jw, sma_hole / 2) + 1,
        str("Snap bead ", s, " runs into the TX slot"));
    assert(s[0] != 2 || abs(s[1] - usb_x) >= snap_len / 2 + usb_open_w / 2 + 1,
        str("Snap bead ", s, " runs into the USB-C opening"));
    assert(!pry_notch || s[0] != 2 || abs(s[1] - pry_x) >= snap_len / 2 + pry_w / 2 + 1,
        str("Snap bead ", s, " runs into the pry notch"));
}
assert(!pry_notch || (abs(pry_x - usb_x) >= usb_open_w / 2 + pry_w / 2 + 1
                   && pry_x - pry_w / 2 >= side_run(2)[0] && pry_x + pry_w / 2 <= side_run(2)[1]
                   && (!use_tx || tx_s != 2 || abs(pry_x - tx_along) >= pry_w / 2 + sma_hole / 2 + 1)),
    "Pry notch overlaps the USB-C opening, TX slot or a corner; move pry_x");
assert(z_hole_bot >= floor_web - 1e-6, "Fastener hole too close to the phone face");
assert(norm([cav_x - cav_r, cav_y1 - cav_r]) >= ring_ro,
    "Cavity corner radius cuts into the ring pocket; reduce pcb_r");
assert(!use_clock || clk_y0 - 0.4 >= cav_y0, "Clocking-magnet pocket runs into the bottom wall");
assert(usb_z0 >= z_floor + 0.5, "USB-C opening runs into the floor");
assert(abs(usb_x) + usb_open_w / 2 <= cav_x - cav_r, "USB-C opening runs into a corner");
assert(z_seam - lip_h >= z_pcb_top + 0.5, "Lid lip reaches the PCB");
for (i = [0 : len(holes) - 1]) {
    assert(norm(holes[i]) - standoff_d / 2 >= ring_ro + 0.5
           || norm(holes[i]) + standoff_d / 2 <= ring_ri - 0.5,
        str("Standoff for board hole ", holes_pcb[i], " lands on the ring pocket. Keep hole centres more than ",
            r2(ring_ro + 0.5 + standoff_d / 2), " mm or less than ", r2(ring_ri - 0.5 - standoff_d / 2),
            " mm from the ring centre, which is at board ", [r2(-pcb_x0), r2(-pcb_y0)]));
    assert(!use_clock
           || rect_dist(holes[i], [clk_x0, clk_y0], [clk_x1, clk_y1]) >= standoff_d / 2 + 0.5,
        str("Standoff for board hole ", holes_pcb[i], " lands on the clocking-magnet pocket"));
    assert(rect_dist(holes[i],
                     [usb_x - max(usb_open_w, usb_body[0]) / 2, cav_y0 - wall_t],
                     [usb_x + max(usb_open_w, usb_body[0]) / 2, pcb_y0 - usb_overhang + usb_body[1]])
           >= max(standoff_d, screw_head_d) / 2 + 0.3,
        str("Standoff for board hole ", holes_pcb[i], " collides with the USB-C receptacle or opening"));
    assert(holes_pcb[i][0] >= pcb_hole_d / 2 + 0.5 && holes_pcb[i][0] <= pcb_W - pcb_hole_d / 2 - 0.5
           && holes_pcb[i][1] >= pcb_hole_d / 2 + 0.5 && holes_pcb[i][1] <= pcb_L - pcb_hole_d / 2 - 0.5,
        str("Board hole ", holes_pcb[i], " is off the board"));
    assert(!use_patch || rect_dist(holes[i], patch_xy - [radome_w, radome_w] / 2,
                                   patch_xy + [radome_w, radome_w] / 2) >= screw_head_d / 2 + 0.3,
        str("Board hole ", holes_pcb[i], " lands on the RX patch radome; move patch_pos"));
    assert(!use_tx || rect_dist(holes[i], jack_a, jack_b) >= max(standoff_d, screw_head_d) / 2 + 0.3,
        str("Board hole ", holes_pcb[i], " collides with the TX jack; move tx_pos"));
}
assert(!use_patch || (patch_c[0] - patch_fp / 2 >= 1 && patch_c[0] + patch_fp / 2 <= pcb_W - 1
                   && patch_c[1] - patch_fp / 2 >= 1 && patch_c[1] + patch_fp / 2 <= pcb_L - 1),
    "RX patch footprint runs off the board; move patch_pos");
assert(!use_patch || z_pcb_bot - z_floor >= patch_pin - pcb_t + 0.3 - 1e-6,
    "RX patch feed pin and solder reach the floor; raise pcb_gap or trim the pin");
assert(patch_cover > 0 && patch_cover <= lid_t, "patch_cover must be in (0, lid_t]");
assert(!use_tx || (tx_along - max(tx_jw, sma_hole / 2) - 0.5 >= side_run(tx_s)[0]
                && tx_along + max(tx_jw, sma_hole / 2) + 0.5 <= side_run(tx_s)[1]),
    "TX jack runs onto a corner radius; move tx_pos");
assert(!use_tx || (tx_gap >= -1e-6 && tx_notch > 0),
    "Board edge on the TX side must sit within the jack body thickness of the wall");
assert(!use_tx || (tx_notch + tx_gap >= tx_jt + 0.1 - 1e-6 && tx_nw >= tx_jw + 0.2 - 1e-6),
    str("Board notch ", r2(tx_notch), " x ", r2(2 * tx_nw), " mm is too small for the ",
        sma_body[0], " x ", tx_jt, " mm jack flange; enlarge tx_notch_d / tx_notch_w"));
// the slot, its lower arc and the tongue's arc are all concentric with the
// barrel at sma_hole, so the radial clearance is (sma_hole - sma_thread) / 2
assert(!use_tx || sma_hole - sma_thread >= 0.2 - 1e-6,
    "SMA slot/tongue leave under 0.1 mm radial on the 1/4-36 barrel; raise sma_clr");
assert(!vent_slots || (vent_n >= 1 && vent_pitch > vent_w + 0.8),
    "Vent slots need vent_n >= 1 and at least 0.8 mm of lid between slots");
assert(!vent_slots || (vent_a[0] >= -cav_x + lip_clr + lip_t + 1 && vent_b[0] <= cav_x - lip_clr - lip_t - 1
                    && vent_a[1] >= cav_y0 + lip_clr + lip_t + 1 && vent_b[1] <= cav_y1 - lip_clr - lip_t - 1),
    "Vent slots run onto the lid lip; move vent_c or shorten them");
assert(!vent_slots || !use_patch || !rects_hit(vent_a, vent_b, patch_xy - [radome_w, radome_w] / 2,
                                               patch_xy + [radome_w, radome_w] / 2, 3),
    "Vent slots within 3 mm of the RX patch radome; move vent_c");
assert(!vent_slots || !use_tx || !rects_hit(vent_a, vent_b, jack_a, jack_b, vent_keep),
    str("Vent slots within ", vent_keep, " mm of the TX jack; move vent_c"));
assert(!use_tx || sma_z - sma_body[2] / 2 >= z_floor + 0.2,
    "TX jack body hits the floor; raise pcb_gap or sma_axis_z");
assert(!use_tx || sma_z - sma_hole / 2 >= skin_t + 0.6, "TX jack hole reaches the skin");
assert(!use_tx || sma_barrel - wall_t >= 4.0,
    "Too little SMA thread outside the wall for the antenna to seat; use a longer-barrel jack");
assert(!use_tx || tx_s != 2 || abs(tx_along - usb_x) >= max(tx_jw, sma_hole / 2) + usb_open_w / 2 + 1,
    "TX jack and USB-C opening overlap on the bottom wall");
assert(!(use_tx && use_patch) || !rects_hit(patch_xy - [patch_fp, patch_fp] / 2,
                                           patch_xy + [patch_fp, patch_fp] / 2, jack_a, jack_b, 1),
    "RX patch runs into the TX jack");

echo(str("=== BEACON MagSafe enclosure, ", ring_t, " mm ring ==="));
echo(str("Skin over magnets: ", r2(skin_t), " mm (", skin_layers, " layers); pocket depth ",
         r2(z_pause - skin_t), " mm, ", r2(z_pause - skin_t - mag_t), " mm headroom; cap ",
         cap_layers, " layers to ", r2(z_floor), " mm"));
echo(str("PAUSE: after layer ", pause_layer, " (top at Z = ", r2(z_pause),
         " mm), i.e. before the layer that ends at Z = ", r2(z_pause + layer_h),
         " mm. Insert magnets, then resume."));
echo(str("Outside: ", r2(2 * out_x), " x ", r2(out_y1 - out_y0), " x ", r2(z_top),
         " mm; ring centre ", r2(out_y1), " mm below the top edge"));
echo(str("PCB: ", r2(pcb_W), " x ", r2(pcb_L), " x ", pcb_t, " mm, corner r ", pcb_r,
         ", underside ", r2(z_pcb_bot), " mm above the phone"));
echo(str("Ring centre in board coords: ", [r2(-pcb_x0), r2(-pcb_y0)]));
echo(str("Mounting holes in board coords: ", [for (h = holes_pcb) [r2(h[0]), r2(h[1])]],
         "; keep 6 mm pads clear on both sides"));
echo(str("Part height: under board ", r2(z_pcb_bot - z_floor), " mm, over board ", r2(top_clear),
         " mm (", r2(z_seam - lip_h - z_pcb_top), " mm within ", r2(lip_clr + lip_t - pcb_clr),
         " mm of the board edge, under the lid lip)"));
echo(str("PCB screws: 4x M2 x ", screw_L, " pan/cheese head, top-down through the board, ",
         r2(engage), " mm of thread in ",
         fastener == "insert" ? str("M2 x ", insert_len, " heat-set inserts") : "thread-forming pilots"));
echo(str("Lid: snap fit, ", len(snaps), " beads x ", snap_len, " mm, ", r2(snap_p - lip_clr),
         " mm interference, bead centre ", r2(z_seam - snap_z), " mm below the seam"));
echo(str("USB-C: centreline ", r2(usb_zc), " mm above the phone face, opening ",
         usb_open_w, " x ", usb_open_h, " mm"));
if (use_patch)
    echo(str("RX patch: centre ", [r2(patch_c[0]), r2(patch_c[1])], " in board coords, ",
             [r2(patch_xy[0]), r2(patch_xy[1])], " from the ring centre; ",
             patch_window ? str(r2(z_seam - z_pcb_top - patch_stack), " mm air, open window")
                          : str(r2(z_seam + lid_t - patch_cover - z_pcb_top - patch_stack),
                                " mm air under a ", patch_cover, " mm radome")));
if (use_tx)
    echo(str("TX jack: ", tx_side, " board edge at ", tx_pos, " mm; board notch ", r2(tx_notch),
             " x ", r2(2 * tx_nw), " mm; axis ", r2(sma_z), " mm above the phone face, ",
             r2(sma_barrel - wall_t), " mm of barrel outside the wall; slot ", r2(sma_hole),
             " mm (", r2((sma_hole - sma_thread) / 2), " mm radial on the thread)"));
echo(str("Lid: print light-coloured PETG (white/natural). Vents ",
         vent_slots ? str(vent_n, " x ", vent_len, " x ", vent_w, " mm slots at board ", vent_c)
                    : "off"));

// ---------------------------------------------------------------------
// 2D helpers
// ---------------------------------------------------------------------
module rrect(x0, y0, x1, y1, r) {
    rr = max(min(r, (x1 - x0) / 2 - eps, (y1 - y0) / 2 - eps), eps);
    translate([x0 + rr, y0 + rr]) offset(r = rr) square([x1 - x0 - 2 * rr, y1 - y0 - 2 * rr]);
}
module outer2d(inset = 0)  rrect(-out_x + inset, out_y0 + inset, out_x - inset, out_y1 - inset, out_r - inset);
module cavity2d(inset = 0) rrect(-cav_x + inset, cav_y0 + inset, cav_x - inset, cav_y1 - inset, cav_r - inset);
module ring2d(ro, ri) difference() { circle(r = ro); circle(r = ri); }
module clock2d() {
    translate([clk_x0, clk_y0]) square([clk_x1 - clk_x0, clk_y1 - clk_y0]);
    for (x = [clk_x0, clk_x1], y = [clk_y0, clk_y1])   // corner reliefs for a square bar
        translate([x, y]) circle(d = 0.8);
}
module u_slot(w, z0, z1, r) hull() {               // x = across, y = height
    for (s = [-1, 1]) translate([s * (w / 2 - r), z0 + r]) circle(r = r);
    translate([-w / 2, z0 + r]) square([w, z1 - z0 - r]);
}
module at_side(s, p) translate(side_pt(s, p)) rotate([0, 0, side_ang(s)]) children();
module through_wall(d, z) translate([0, -1, z]) rotate([-90, 0, 0]) cylinder(d = d, h = wall_t + 2);
module pcb2d() difference() {
    rrect(0, 0, pcb_W, pcb_L, pcb_r);
    for (h = holes_pcb) translate(h) circle(d = pcb_hole_d);
    if (use_tx) {                                      // jack body notch at the TX edge
        if (tx_s == 0) translate([tx_pos - tx_nw, pcb_L - tx_notch]) square([2 * tx_nw, tx_notch + 1]);
        if (tx_s == 1) translate([pcb_W - tx_notch, tx_pos - tx_nw]) square([tx_notch + 1, 2 * tx_nw]);
        if (tx_s == 2) translate([tx_pos - tx_nw, -1]) square([2 * tx_nw, tx_notch + 1]);
        if (tx_s == 3) translate([-1, tx_pos - tx_nw]) square([tx_notch + 1, 2 * tx_nw]);
    }
}

// ---------------------------------------------------------------------
// Base (phone side), modelled as printed
// ---------------------------------------------------------------------
module base() {
    difference() {
        union() {
            difference() {
                hull() {                                   // chamfered bed edge
                    linear_extrude(eps) outer2d(edge_chamfer);
                    translate([0, 0, edge_chamfer]) linear_extrude(z_wall - edge_chamfer) outer2d();
                }
                translate([0, 0, z_floor]) linear_extrude(z_wall) cavity2d();
            }
            for (h = holes)                                // PCB standoffs
                translate([h[0], h[1], z_floor - eps])
                    cylinder(d = standoff_d, h = z_pcb_bot - z_floor + eps);
        }
        // sealed magnet pockets: skin_t below, cap_layers above, open only
        // until the pause
        translate([0, 0, skin_t]) linear_extrude(z_pause - skin_t) ring2d(ring_ro, ring_ri);
        if (use_clock) translate([0, 0, skin_t]) linear_extrude(z_pause - skin_t) clock2d();
        // insert or pilot holes with a lead-in chamfer
        for (h = holes) translate([h[0], h[1], 0]) {
            translate([0, 0, z_hole_bot]) cylinder(d = hole_d, h = z_pcb_bot - z_hole_bot + 1);
            translate([0, 0, z_pcb_bot - 0.4]) cylinder(d1 = hole_d, d2 = hole_d + 0.8, h = 0.4 + eps);
        }
        // USB-C opening: open-top U through the bottom wall, closed by the lid
        translate([usb_x, cav_y0 + 0.5, 0]) rotate([90, 0, 0])
            linear_extrude(wall_t + 1.5) u_slot(usb_open_w, usb_z0, z_top + 1, usb_open_r);
        // snap grooves in the inner wall faces (45 degree flanks, print upright)
        for (s = snaps) at_side(s[0], s[1])
            rotate([90, 0, 90]) linear_extrude(snap_len + 2 * snap_clr + 1, center = true)
                polygon([[-1, snap_z - snap_gd - 1], [snap_gd, snap_z], [-1, snap_z + snap_gd + 1]]);
        // lever notch in the outer half of the bottom wall, at the seam
        if (pry_notch) at_side(2, pry_x)
            translate([-pry_w / 2, wall_t / 2, z_wall - 1.2]) cube([pry_w, wall_t, 2]);
        // TX jack: barrel hole + U-slot up through the wall top (lid tongue closes it)
        if (use_tx) at_side(tx_s, tx_along) {
            through_wall(sma_hole, sma_z);
            translate([-sma_hole / 2, -1, sma_z]) cube([sma_hole, wall_t + 2, z_top]);
        }
        if (label) translate([0, 0, z_pause - 0.4]) linear_extrude(0.4 + eps) {   // read at the pause
            translate([0,  2.8]) text("MAGNETS DOWN", size = 3.5, halign = "center", valign = "center");
            translate([0, -2.8]) text("STEEL UP",     size = 3.5, halign = "center", valign = "center");
        }
    }
}

// ---------------------------------------------------------------------
// Lid (back cover), modelled in assembled position
// ---------------------------------------------------------------------
module lid() {
    difference() {
        union() {
            hull() {                                       // plate, chamfered outer edge
                translate([0, 0, z_seam]) linear_extrude(lid_t - edge_chamfer) outer2d();
                translate([0, 0, z_top - eps]) linear_extrude(eps) outer2d(edge_chamfer);
            }
            difference() {                                 // locating lip, notched at USB-C and TX jack
                translate([0, 0, z_seam - lip_h]) linear_extrude(lip_h + eps)
                    difference() { cavity2d(lip_clr); cavity2d(lip_clr + lip_t); }
                translate([usb_x - usb_open_w / 2 - 0.3, cav_y0 - 1, z_seam - lip_h - 1])
                    cube([usb_open_w + 0.6, lip_clr + lip_t + 1.5, lip_h + 2]);
                if (use_tx) at_side(tx_s, tx_along)
                    translate([-(tx_jw + 0.5), -(lip_clr + lip_t + 0.5), z_seam - lip_h - 1])
                        cube([2 * (tx_jw + 0.5), lip_clr + lip_t + 1.5, lip_h + 2]);
            }
            for (s = snaps) at_side(s[0], s[1])            // snap beads on the lip face
                rotate([90, 0, 90]) linear_extrude(snap_len, center = true)
                    polygon([[-lip_clr - 0.3, snap_z - snap_p - 0.3], [-lip_clr + snap_p, snap_z],
                             [-lip_clr - 0.3, snap_z + snap_p + 0.3]]);
            if (use_tx) at_side(tx_s, tx_along)            // tongue closing the TX slot
                difference() {
                    translate([-(sma_hole / 2 - tongue_clr), 0, sma_z])
                        cube([sma_hole - 2 * tongue_clr, wall_t, z_seam - sma_z + eps]);
                    through_wall(sma_hole, sma_z);
                }
        }
        if (use_patch) translate([patch_xy[0], patch_xy[1], 0]) {   // RX radome / window
            if (patch_window)
                translate([0, 0, z_seam - 1]) linear_extrude(lid_t + 2)
                    square(patch_fp + 1, center = true);
            else if (patch_cover < lid_t)
                translate([0, 0, z_seam - 1]) linear_extrude(1 + lid_t - patch_cover)
                    square(radome_w, center = true);
        }
        if (vent_slots)                                    // optional vent slots
            translate([0, 0, z_seam - 1]) linear_extrude(lid_t + 2)
                for (y = vent_ys) hull()
                    for (s = [-1, 1]) translate([vent_xy[0] + s * (vent_len - vent_w) / 2, y])
                        circle(d = vent_w);
    }
}
module lid_print() rotate([180, 0, 0]) translate([0, 0, -z_top]) lid();

// ---------------------------------------------------------------------
// Preview-only parts
// ---------------------------------------------------------------------
module magnets_ghost() {
    color("firebrick") translate([0, 0, skin_t])
        linear_extrude(ring_t * 0.65) ring2d(ring_od / 2, ring_id / 2);
    color("silver") translate([0, 0, skin_t + ring_t * 0.65])
        linear_extrude(ring_t * 0.35) ring2d(ring_od / 2, ring_id / 2);
    if (use_clock) color("firebrick")
        translate([-clock_w / 2, -clock_top - clock_l, skin_t]) cube([clock_w, clock_l, clock_t]);
}
module pcb_ghost() {
    color("darkgreen") translate([pcb_x0, pcb_y0, z_pcb_bot]) linear_extrude(pcb_t) pcb2d();
    color("lightgrey") translate([usb_x - usb_body[0] / 2, pcb_y0 - usb_overhang, z_pcb_top]) cube(usb_body);
}
module antennas_ghost() {
    if (use_patch) color("wheat")
        translate([patch_xy[0], patch_xy[1], z_pcb_top + patch_tape])
            linear_extrude(patch_h - 0.1) offset(r = 1.5) square(patch_sz - 3, center = true);
    if (use_tx) at_side(tx_s, tx_along) {
        color("gold") {
            translate([-tx_jw, -tx_jt, sma_z - sma_body[2] / 2]) cube([2 * tx_jw, tx_jt, sma_body[2]]);
            translate([0, 0, sma_z]) rotate([-90, 0, 0]) cylinder(d = sma_thread, h = sma_barrel);
            translate([0, sma_barrel - 4, sma_z]) rotate([-90, 0, 0])   // SMA(M) coupling nut
                cylinder(d = 8 / cos(30), h = 8.4, $fn = 6);
        }
        color("dimgray") translate([0, sma_barrel - 4 + 8.4, sma_z]) rotate([-90, 0, 0]) {
            cylinder(d = 7.9, h = 21.5 - 3.95);                        // 30 mm overall
            translate([0, 0, 21.5 - 3.95]) sphere(d = 7.9);
        }
    }
}
module screws_ghost() {
    for (h = holes) color("dimgray") translate([h[0], h[1], 0]) {
        translate([0, 0, z_pcb_top - screw_L]) cylinder(d = 2, h = screw_L);
        translate([0, 0, z_pcb_top]) cylinder(d = screw_head_d, h = screw_head_h);
    }
}
module assembly(lift) {
    color("gainsboro") base();
    magnets_ghost();
    pcb_ghost();
    antennas_ghost();
    screws_ghost();
    translate([0, 0, lift]) color("lightsteelblue", 0.8) lid();
}
module half() intersection() {                          // keep x >= 0
    children();
    translate([0, -500, -1]) cube([500, 1000, 100]);
}
module print_plate() {
    base();
    translate([2 * out_x + 8, out_y0 + out_y1, 0]) lid_print();
}

// ---------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------
if (part == "base") base();
else if (part == "lid") lid_print();
else if (part == "assembly") assembly(explode);
else if (part == "section") {
    color("gainsboro") half() base();
    half() magnets_ghost();
    half() pcb_ghost();
    half() antennas_ghost();
    color("lightsteelblue") half() lid();
    half() screws_ghost();
}
else if (part == "pcb_outline") pcb2d();
else print_plate();
