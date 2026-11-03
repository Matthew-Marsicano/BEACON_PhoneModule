// =====================================================================
//  BEACON phone module - MagSafe enclosure with RX patch + TX flex antenna
//  VARIANT: 2.5 mm ring
//  REVISION: round - derived from beacon_phone_magsafe_fxp70_inlid.scad
//    Same board, Z stack, FXP70 flex in the lid pocket, open patch window,
//    cable route, snap lid and asserts as fxp70_inlid. New: a rounded
//    "pebble" shell instead of the 0.4 mm chamfers, so the module slides
//    into a pocket:
//     - side profile (same on all four sides): 45 deg chamfer + R bot_r
//       round off the flat phone face, a convex side (R side_r, widest
//       +bulge at Z bulge_z), and an R top_r round over the lid edge that
//       meets the flat lid face at top_ang (60 deg overhang, printable face
//       down). Every transition is tangent; the only creases are the two
//       obtuse (135 / 120 deg) ones where the chamfers meet the flat faces.
//     - plan corners: outside corner radius corner_r (0 = auto, the largest
//       the board corner allows with wall_min of wall), 5.1 -> 7.6 mm with
//       the current r 3 board.
//     - pcb_r (board corner radius) is the one switch for rounder plan
//       corners; asserts keep pcb_keep_d (standoff) clear of the board edge.
//       The default pcb_r = 3 exports the same pcb_outline DXF.
//    See ROUND.md (this revision), FXP70_INLID.md and LOWPROFILE.md.
//  Ring:    totalElement 54 x 46 x 2.5 mm N52 ring assembly with alignment magnet (listed 54.1 OD x 46 ID x 2.55 mm)
//  Defaults give 61.2 x 84.65 x 11.41 mm outside at the widest section (nominal
//  outline 59.2 x 82.65 at the seam band, phone face 56.2 x 79.65 flat).
//
//  Z STACK (defaults, same as lowprofile / fxp70)
//   skin 0.68, magnets to 3.23, pause 3.56, floor top 4.16
//   board bottom 4.76 (pcb_gap 0.6, set by the USB-C overmold opening)
//   board top 6.36, lid underside 10.21 (top_clear 3.85 = USB4105 3.31 + 0.5),
//   lid 1.2, top 11.41. Flex pocket ceiling 10.61 (lid_skin 0.8 left), flex
//   (nominal) 10.47-10.55, i.e. about 4.15 above the board-top GND pour and
//   4.4 above the solid L2 GND.
//
//  Antennas
//   RX: Taoglas WDP.2458.25.4.B.02 patch on the board top, open lid window
//       (28.4 sq at the board centre), unchanged.
//   TX: FXP70 flex in the lid, 26.9 along X x 24.9 along Y, between the
//       patch window (1.6 nominal lid web) and the top edge of the box
//       (it runs over the top wall; the lid lip is cut there). Its cable
//       exit edge faces the window; viewed from outside the lid the cable
//       is at the +X end, so the flex is pushed to X <= 20.6 and the cable
//       drops into the free strip right of the patch (board x > 41).
//       Cable route (53 +/-2, no loops): along the lid underside in clip
//       rails toward -Y, one tilted 180 deg hairpin (R 4.5) down to the
//       board ground at the board's right edge, back +Y on the board under
//       lid keepers, an S-jog (R 4.5) to the plug axis and into J3 from -Y.
//       The hairpin floats and takes up the cable length tolerance.
//
//  Parts
//   base : as lowprofile (no bay, no wall slot). Snap grooves follow the
//          moved beads.
//   lid  : flat plate, patch window, USB-C notch, lip + beads. New: flex
//          pocket (lid underside), cable groove at the flex exit, clip
//          rails, board-leg keepers, lid lip cut over the pocket (top wall)
//          and notched over the hairpin / board leg (right wall). Beads:
//          right wall y -38 / -24 / 15, left -32 / -2, top x -16.
//
//  Coordinates (assembled): origin = ring centre on the phone-contact
//  face. +Y toward the top of the phone, -Y toward the bottom (USB-C,
//  clocking magnet), +X to the right seen from the back of the phone
//  (camera bump top-left). +Z away from the phone. Board coordinates
//  (pcb_holes, patch_pos, tx_pos, ufl_pos, DXF export) start at the
//  board's lower-left corner seen from the component side, USB-C edge at
//  the bottom (KiCad: board x = X - 100, board y = 78.45 - (Y - 100)).
//
//  Print: part = "print_plate", no supports. Base prints phone face down,
//  lid prints outer face down (the pocket, rails and keepers then face up).
//  Rounded shell: the base's bottom edge overhangs at most bot_ang (45 deg);
//  the lid's top edge at most top_ang (60 deg = 0.21 mm step per 0.12 layer,
//  half a 0.42 line) in its first layers, then steeper. No supports.
//  Match first_layer_h / layer_h to your slicer; lid_skin should be a whole
//  number of lid layers (0.8 = 0.2 + 5 x 0.12). PETG, not PLA/ABS/ASA;
//  drop the bed to about 60 C at the pause. No metal- or carbon-filled
//  filament, no carbon-black or pigment-heavy colours near the antennas.
//  Print the LID in light-coloured PETG (white/natural).
//
//  Assembly
//   1.-5. Magnets, inserts, board and screws: as fxp70 (no SMA, no leg cut).
//   6.  Lid, upside down: clean the pocket (IPA). Peel the FXP70 liner and
//       lay the flex adhesive side DOWN into the pocket (cable side up),
//       cable at the pocket's +X / window corner, and push it into the +X
//       and outer (+Y, top-wall) corner of the pocket. Press 10 s. Press the
//       cable into the clip rails.
//   7.  Mate the plug on J3 (straight down, cable toward -Y, i.e. toward
//       USB-C). Lay the S-jog and the board leg along the board's right
//       edge. Lower the lid straight down: the slack forms the hairpin
//       beside the patch window. Check the board leg sits under the lid
//       keepers, then press the lid on until the beads click.
//       To open: lift the lid straight up no more than ~13 mm, then unplug
//       J3 before taking the lid away (flex and cable stay in the lid).
//
//  The console ECHO lists outside size, board outline, hole positions,
//  antenna and cable geometry and clearances, and screw length.
//  part = "pcb_outline" renders the board shape, notch included, for DXF.
// =====================================================================

/* [Render] */
part    = "print_plate"; // [print_plate, base, lid, lid_under, assembly, closed, routing, section, section_patch, section_ant, section_hairpin, section_ant_x, sec2d_ant, sec2d_exit, sec2d_hairpin, sec2d_ant_x, sec2d_edge, profile2d, section_cable, section_flex, section_sma, pcb_outline]
                         //   round: closed = base + lid shut (silhouettes);
                         //   sec2d_edge = X-Z section at y = sec_y (side walls,
                         //   ring); profile2d = the side profile vs the pocket,
                         //   cavity wall, lip and magnets (fast, no CGAL)
                         //   section: x >= 0 half; section_patch: x >= feed pin
                         //   (through patch + pin pocket); routing: base,
                         //   board and antennas without the lid.
                         //   lid mode: lid_under = lid seen from below with the
                         //   flex and the lid-held cable; section_ant: keep
                         //   x <= cable exit + sec_off (pocket, flex, groove,
                         //   rails, window web, top wall); section_hairpin: keep
                         //   y >= hairpin centre + sec_off (both legs);
                         //   section_ant_x: keep y <= flex centre + sec_off.
                         //   sec2d_*: flat colour-coded cross-section drawings
                         //   (CGAL, ~2 min; use -D label=false off the ring
                         //   centre): ant = x through the flex centre, exit =
                         //   x through the cable exit, hairpin = y through the
                         //   hairpin legs, ant_x = y through the flex centre.
                         //   bay mode: section_cable: keep y <= cable centreline
                         //   + sec_off; section_flex: keep x <= flex centre +
                         //   sec_off. section_sma (legacy, use_sma): jack axis
explode = 18;            // lid lift in the assembly view, mm
sec_off = 0;             // section cut offset, mm
sec_y   = 0;             // sec2d_edge plane (ring-centre y)
sec_render = false;      // sections: CGAL-render the base and lid cuts so their cut
                         //   faces keep their colours in a preview (slower)

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
pcb_gap     = 0.6;       // general space under the board (rev_pcb 1.5). Only flat
                         //   pads are under the board; taller bottom-side items
                         //   get floor pockets below. 0.6 is the minimum the USB-C
                         //   overmold opening allows (usb_z0 >= z_floor + 0.5).
                         //   (legacy use_sma with sma_leg_cut = false: 1.3)
top_parts_h = 3.35;      // tallest general top-side part (GCT USB4105-GF-A 3.31;
                         //   L1 ASPI-4030S 3.0, SW1 B3U 2.5, U.FL mated 2.5).
                         //   The patch is handled by the window.
edge_parts_h = 1.1;      // tallest part within 1.1 mm of the board edge (under the
                         //   lid lip; L3 0402 at board x 53.8 today)
hole_inset  = 3.5;       // auto hole pattern: hole centre to board edges
pcb_hole_d  = 2.2;       // board hole, used by the DXF export
pcb_holes   = [];        // [] = 4 corner holes; else [[x, y], ...] in board coords

/* [Floor pockets (bottom-side parts that hang below pcb_gap)] */
pocket_wall   = 0.6;     // min plastic between a floor pocket that goes below the
                         //   pause height and a magnet pocket
pin_pocket    = true;    // pocket under the patch feed pin (inside the ring island)
patch_pin_off = [1.8, -1.8]; // feed pin from the patch centre, board coords
                         //   (AE1 pad 1 at board (29.3, 37.425))
pin_pocket_d  = 4.0;     // pin pad 2.0 + solder + placement tolerance
sma_pocket    = true;    // (legacy use_sma) pocket under the SMA flange and lower legs
sma_leg_below = 1.07;    // Cinch lower legs: thickness below the board bottom
sma_leg_l     = 3.81;    // legs run 0.150 in behind the flange back face
sma_leg_y     = [2.365, 3.175]; // leg inner/outer edge from the jack axis
sma_leg_cut   = true;    // the lower leg that lies over the ring magnet is cut
                         //   to sma_leg_stub before soldering (assembly 4a).
                         //   false: it rides over the cap; set pcb_gap = 1.3
sma_leg_stub  = 0.5;     // what is left of a cut leg behind the flange
sma_pocket_clr = 0.25;   // pocket clearance around the flange and legs (XY and Z)
usb_stake_pocket = true; // pockets under the USB4105 THT shell stakes
usb_stakes    = [[-4.32, 2.60], [4.32, 2.60], [-4.32, 6.78], [4.32, 6.78]];
                         //   [x from usb_x, y behind the board edge] (J1 SH pads)
usb_stake_below = 1.0;   // assumed stake + solder below the board (not in docs/;
                         //   measure, clip flush if longer)
usb_stake_pkt = [1.3, 2.6]; // pocket size per stake (pad 1.0 x 2.1 + margin)

/* [Fasteners] */
fastener      = "insert"; // [insert, selftap]
insert_d      = 3.2;     // hole for an M2 x 3 heat-set insert (OD ~3.6). Not
                         //   limiting here: needs board bottom >= 4.4, has 4.76
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
usb_open_top = true;     // opening runs up through the lid (notch), so the 6.7 mm
                         //   overmold opening does not set the lid height. false:
                         //   the lid bridges it (rev_pcb), top_clear >= 5.08

/* [Shell] */
wall_t       = 1.8;
lid_t        = 1.2;      // rev_pcb 1.6. Flat plate, >= 1.0 (PETG, assert)
lid_local_min = 0.8;     // min lid left over a local underside recess (SMA)
lip_h        = 2.6;      // lid lip depth into the base (carries the snap beads).
                         //   2.2 min for the groove-to-wall-top assert; 2.6 keeps
                         //   top_clear - lip_h = 1.25 for edge_parts_h + 0.1
lip_t        = 1.2;
lip_clr      = 0.2;
seam_gap     = 0;        // lid plate sits on the wall tops
edge_chamfer = 0.4;      // only the legacy antenna bay (fxp_mount = "bay") still uses it
label       = true;     // deboss MAGNETS DOWN / STEEL UP inside the ring

/* [Rounded shell (round revision)] */
// Side profile, given as the outward offset o(z) of the plan outline from the
// nominal outline (cavity + wall_t, corner radius corner_r), the same on all
// four sides. Bottom to top: flat phone face inset bot_inset, a bot_ang
// chamfer, an R bot_r round, the convex side (R side_r, widest at
// +bulge / Z bulge_z), an R top_r round and a top_ang chamfer to the flat
// lid face, inset top_inset. All joints tangent.
corner_r     = 0;        // outside plan corner radius at the nominal outline; 0 = auto:
                         //   the largest (0.1 steps) that keeps wall_min at the
                         //   cavity corners and the flex-pocket rim / skin (7.6
                         //   with pcb_r 3; fxp70_inlid 5.1)
wall_min     = 1.0;      // min wall anywhere round the cavity, after rounding
bulge        = 1.0;      // widest section, outward from the nominal outline
grow_max     = 1.0;      // footprint growth allowed per side (assert)
bulge_z      = 6.0;      // height of the widest section
side_r       = 25;       // convex side radius
bot_inset    = 1.5;      // flat phone face inset from the nominal outline
bot_ang      = 45;       // bottom chamfer overhang from vertical (base prints face down)
bot_r        = 4.5;      // bottom round
top_inset    = 0.75;     // flat lid face inset from the nominal outline. The flex
                         //   pocket (0.62 from the top edge, 0.8 skin) limits it
top_ang      = 60;       // lid-face chamfer overhang from vertical (lid prints face
                         //   down): layer_h * tan = 0.21 per layer <= line_w / 2
top_r        = 2.5;      // top round
line_w       = 0.42;     // extrusion width, for the first-layer overhang check
mag_side_min = 1.0;      // min plastic between a magnet pocket and the outside
face_margin  = 0.5;      // flat phone face past the ring / clocking-magnet pockets
prof_step    = 5;        // degrees per profile arc segment
corner_n     = 16;       // segments per plan corner
pcb_keep_d   = 6.0;      // board corner check: this circle round each hole must stay
pcb_keep_m   = 0.5;      //   pcb_keep_m inside the board edge (6.0 = standoff; KiCad
                         //   MountingHole_2.2mm_M2: courtyard 4.9, Cmts 4.4; head 3.8)

/* [Snap fit] */
snap_p      = 0.45;      // bead protrusion from the lip face (45 deg flanks);
                         //   interference = snap_p - lip_clr. Raise for a
                         //   firmer click, lower if it is hard to open.
snap_len    = 12;        // length of each bead / groove
snap_clr    = 0.1;       // extra groove depth over the bead
snap_side_y = [-32, -2]; // bead centres on the left wall (ring-centre y)
snap_right_y = [-38, -24, 15]; // bead centres on the right wall (lowprofile: -32, -2;
                         //   fxp70 bay: -38, -2). Lid mode: the lip is notched
                         //   over the cable hairpin / board leg (y ~-14.4 to 5.1)
snap_bay    = true;      // (bay mode) one bead on the antenna bay's inner top wall
snap_top_x  = [-16];     // bead centres on the top wall (ring-centre x; lowprofile
                         //   and bay: 0). Lid mode: the top lip is cut over the
                         //   flex pocket (x ~-7.2 to 20.9)
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
patch_tape   = 0.3;      // adhesive under the patch, nominal
patch_tape_max = 0.5;    // datasheet maximum, used for worst-case air / recess
patch_pin    = 2.8;      // feed pin length, 2.4 +/-0.4, checked against the floor
                         //   (pin pocket); protrudes <= 1.2 below the board
patch_window = true;     // open window in the lid over the patch (default).
                         //   ESD: the patch's top electrode is DC-connected to
                         //   the feed pin; a 50-100 um polyimide/PET label on the
                         //   patch top protects it with little detuning.
                         //   false = flat lid with a thin radome (total 12.26)
patch_recess_min = 0.3;  // window: worst-case patch top below the lid's outer face
patch_margin = 1.5;      // window / radome margin around the patch (>= 1.0 for a
                         //   window, since the patch stands up into it)
patch_gap    = 0.7;      // radome only: air over the patch at the nominal stack
                         //   (rev_pcb 1.0); 0.5 at patch_tape_max
patch_cover  = 0.8;      // radome only: lid left over the patch (rev_pcb 1.2)
patch_air_min = 0.5;     // radome only: min air at patch_tape_max

/* [TX antenna: Taoglas FXP70.07.0053A flex on a Hirose U.FL-R-SMT-1 (J3)] */
// Sources: Taoglas FXP70.07.0053A datasheet SPE-12-8-013 rev G (2024-09-30),
// mechanical drawing p.9; Taoglas APN-11-8-004 rev C "Flexible PCB Antenna
// with Cable"; KiCad J3 at (150.525, 112.45), rot 0.
use_fxp      = true;
fxp_mount    = "lid";    // [lid, bay] lid: flex in a lid-underside pocket, no side
                         //   extension (this revision). bay: the fxp70 side bay
                         //   (95.1 wide; set snap_right_y = [-38, -2], snap_top_x = [0])
ufl_pos      = [50.525, 66.0]; // J3 mating centre, board coords
ufl_mated_h  = 2.5;      // receptacle + plug, max (Hirose U.FL / I-PEX MHF I with
                         //   1.13 cable: 2.5 max, 2.4 nominal)
ufl_lid_clr  = 0.5;      // min air over the mated plug
ufl_plug_w   = 3.0;      // FXP70 detail A: plug 3.0 wide, 2.1 thick, 5.2 +/-0.5 long
ufl_crimp    = 3.7;      // mating centre to the end of the crimp (5.2 - ~1.5)
ufl_cable_z  = 1.9;      // cable centre above the board top where it leaves the plug
cable_d      = 1.13;     // mini-coax OD
cable_bend_r = 4.5;      // design bend radius (4 x OD). No figure in the Taoglas,
                         //   Hirose or I-PEX documents found; 1.13 FEP micro-coax
                         //   is usually rated for a static bend of about 3 x OD
cable_bend_min = 3.4;    // 3 x OD, assert floor
cable_lead   = 3.0;      // straight cable behind the crimp before the first bend
cable_len    = 53;       // drawing: 53 +/-2 from the flex's braid pad to the plug
cable_tol    = 2;
fxp_cable_pad = 5.25;    // braid pad to the flex edge (scaled from the drawing)
cable_rx_min = 5;        // min cable to RX patch footprint (APN: cables not near
                         //   the other antenna)
fxp_sz       = [24.9, 26.9]; // flex in the bay, X x Y. The 26.9 edge carries the
                         //   cable exit and faces the board (-X)
fxp_tol      = 0.2;      // +/- on each flex dimension
fxp_t        = 0.24;     // flex thickness, worst case (datasheet: 0.08 in the
                         //   table, 0.2 on the cover, "polymer 0.24t" in the BOM)
fxp_t_nom    = 0.08;
fxp_adh      = 0.06;     // 3M 467MP transfer adhesive, 0.058
fxp_c_off    = 2.25;     // cable centre from the flex corner along the exit edge
fxp_c_off_tol = 0.3;
fxp_on_flex  = 12.5;     // cable lying on the flex top, exit edge to centre pad
fxp_solder_h = 1.7;      // max solder joint height above the flex (drawing note 1)
fxp_lid_air  = 0.2;      // min air between the worst solder joint and the lid
fxp_clr      = 0.25;     // pocket clearance per side
fxp_slide    = 2;        // pocket is this much longer at each Y end, so the
                         //   flex is placed where the 53 +/-2 cable reaches
ant_gnd_gap  = 10;       // flex pocket inner edge to the board's right edge.
                         //   Taoglas APN-11-8-004: >= 4 from metal, 20 best.
                         //   Each mm adds 1 mm to the outside width
ant_gnd_min  = 4;
ant_rx_min   = 20;       // min RX patch footprint to flex pocket (edge to edge)
shelf_t      = 1.6;      // PETG plate under the flex (Taoglas tunes on 2 mm ABS)
shelf_rim    = 0.6;      // shelf left round the pocket
shelf_rib_w  = 0.8;      // ribs under the shelf, along X
shelf_rib_pitch = 7;
bay_r        = 1.0;      // bay inner corner radius
fxp_holddown = true;     // lid pins over the flex corners (keep it flat if the
                         //   adhesive lets go; also carry the lid wing)
holddown_d   = 2.4;
holddown_gap = 0.2;      // pin end above the shelf top
keeper_y     = [4, -9];  // lid-side cable keepers over the board run (ring-centre y)
keeper_sz    = [4, 3];   // keeper footprint, X x Y
keeper_clr   = 0.3;      // keeper end above the cable top
phone_w      = [71.6, 77.8]; // phone widths for the overhang echo (ring centred)

/* [TX antenna in the lid (fxp_mount = "lid")] */
// The flex lies flat in the top band, 26.9 along X x 24.9 along Y (fxp_sz
// swapped), cable exit edge toward the patch window. Seen from outside the
// lid (adhesive side), the cable is at the +X end of that edge (datasheet
// "Bottom" view), so the cable exit sets the flex's +X edge.
lid_skin     = 0.8;      // PETG left over the flex (0.2 + 5 x 0.12 lid layers)
lid_skin_min = 0.6;
win_web      = 1.0;      // lid between the patch window and the pocket (full 1.2)
win_web_min  = 0.8;
pk_rim_min   = 0.5;      // lid left between the pocket and the outer edge
lid_fxp_clr  = 0.2;      // pocket clearance per side; the flex is pushed into the
                         //   pocket's +X / +Y corner at assembly
top_band_h   = 1.1;      // tallest part under the flex except J3 (KiCad: only
                         //   0402/0603 passives, VQFN-40 U8 / VQFN-16 U7 <= 1.0,
                         //   TG2520 Y2 0.8 in board y > 53)
lid_rx_min   = 2.5;      // min flex to RX patch footprint, edge to edge (this
                         //   layout cannot give more than ~3.1, see FXP70_INLID.md)
leg_wall_clr = 0.3;      // board-leg cable edge to the cavity wall
clip_off     = 3.0;      // flex edge to the first clip: the free cable takes up
                         //   the +/-0.4 exit position tolerance there (S-bend
                         //   radius ~4.7 >= cable_bend_r 4.5, asserted)
groove_clr   = 0.1;      // cable groove at the flex exit, extra per side
rail_t       = 0.8;      // clip rails on the lid underside, either side of the cable
rail_clr     = 0.08;     // cable to rail, per side
clip_p       = 0.15;     // clip ridge at the rail tips (snap the cable in)
rail_end_m   = 0.5;      // rails end this far above the hairpin (shortest cable)
lk_len       = 3.0;      // lid keepers over the board leg / S-jog, length along Y
lk_w         = 2.6;      // keeper width (X) over the board leg
lip_cut_m    = 0.3;      // lid lip cut past the pocket / notch, each end
strip_y      = [21.8, 63.0]; // board y range of the part-free strip right of the
                         //   patch: top side, board x >= strip_x0 (KiCad
                         //   courtyards: R14 to y 21.17, AE1 to x 40.75, C38 to
                         //   x 40.11, J3 from y 63.5, C43 from y 64.11)
strip_x0     = 41.0;
fxp_freq     = 2.45;     // GHz, for the image-theory estimate in the ECHO

/* [Legacy TX: Taoglas GW.26.0111 on a Cinch 142-0711-821 end-launch SMA(F) jack] */
use_sma      = false;    // true (with use_fxp = false and snap_right_y = [-32, -2])
                         //   rebuilds the lowprofile SMA geometry: wall U-slot, lid
                         //   tongue, flange recess, flange/leg pockets, leg cut
board_notch  = true;     // the routed board keeps its 1.5 x 7.1 notch at the old
                         //   jack (DXF unchanged); independent of use_sma
tx_side     = "right";   // [right, left, top, bottom] board notch / legacy jack edge
tx_pos      = 66;        // notch / jack centre along that board edge, board coords
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
sma_lid_clr = 0.5;       // lid underside over the flange top (+3.575); a local
                         //   recess provides it where top_clear is lower
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
                         //   and >= vent_keep from the TX jack / U.FL and cable)
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
function snap_dn(z) = first_layer_h + floor((z - first_layer_h) / layer_h + 1e-6) * layer_h;
function r2(x) = round(x * 100) / 100;
function rect_dist(p, a, b) =
    norm([max(a[0] - p[0], 0, p[0] - b[0]), max(a[1] - p[1], 0, p[1] - b[1])]);
function rects_hit(a0, a1, b0, b1, m) = a0[0] < b1[0] + m && b0[0] < a1[0] + m
                                     && a0[1] < b1[1] + m && b0[1] < a1[1] + m;
// side s: 0 top, 1 right, 2 bottom, 3 left. side_pt/side_ang give a local
// frame on the inner wall face: x along the wall, y = 0 at the face, +y out.
// side 4: inner face of the antenna bay's top wall (faces -Y, like side 0).
function side_pt(s, p) = s == 0 ? [p, cav_y1] : s == 1 ? [cav_x, p]
                       : s == 2 ? [p, cav_y0] : s == 3 ? [-cav_x, p] : [p, bay_cy1];
function side_ang(s)   = [0, -90, 180, 90, 0][s];
function side_run(s)   = s == 4 ? [bay_cx0 + bay_r, bay_cx1 - bay_r]
                       : (s == 0 || s == 2) ? [-cav_x + cav_r, cav_x - cav_r]
                                            : [cav_y0 + cav_r, cav_y1 - cav_r];
// local wall frame -> enclosure coords (axis-aligned rectangles stay so)
function rotv(a, v)       = [v[0] * cos(a) - v[1] * sin(a), v[0] * sin(a) + v[1] * cos(a)];
function loc2glob(s, p, v) = side_pt(s, p) + rotv(side_ang(s), v);
function grect(s, p, r)   = let(u = loc2glob(s, p, r[0]), w = loc2glob(s, p, r[1]))
    [[min(u[0], w[0]), min(u[1], w[1])], [max(u[0], w[0]), max(u[1], w[1])]];
function rect_far(p, a, b) =
    norm([max(abs(p[0] - a[0]), abs(p[0] - b[0])), max(abs(p[1] - a[1]), abs(p[1] - b[1]))]);
function rr_dist(a0, a1, b0, b1) =
    norm([max(b0[0] - a1[0], 0, a0[0] - b1[0]), max(b0[1] - a1[1], 0, a0[1] - b1[1])]);
// true if rectangle r keeps m of plastic to the ring pocket (outside it or
// inside the island)
function off_ring(r, m) = rect_dist([0, 0], r[0], r[1]) >= ring_ro + m - 1e-6
                       || rect_far([0, 0], r[0], r[1]) <= ring_ri - m + 1e-6;
// SMA lower leg i (-1 / +1 across the axis), length l behind the flange, grown by c
function leg_loc(i, l, c) = [[i > 0 ? sma_leg_y[0] - c : -sma_leg_y[1] - c, -tx_jt - l - c],
                             [i > 0 ? sma_leg_y[1] + c : -sma_leg_y[0] + c, -tx_jt]];

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
// out_r (plan corner radius) is set with the rounded profile, below

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
sma_top    = sma_axis_z + sma_body[2] / 2;       // flange top above the board top
patch_top_max = patch_h + patch_tape_max;        // worst-case patch top above the board
// lid underside above the board top. Each term only where it still applies:
//  general parts + 0.5; USB overmold opening if the lid bridges it; patch:
//  window -> patch top patch_recess_min below the outer face, radome ->
//  patch_gap of air under the recessed radome; SMA flange via a local recess
//  that leaves lid_local_min (legacy); mated U.FL + ufl_lid_clr.
top_clear  = max(top_parts_h + 0.5,
                 use_fxp ? ufl_mated_h + ufl_lid_clr : 0,
                 usb_open_top ? 0 : usb_zc + usb_open_h / 2 - z_pcb_top,
                 !use_patch ? 0 : patch_window ? patch_top_max + patch_recess_min - lid_t
                                               : patch_stack + patch_gap - (lid_t - patch_cover),
                 use_sma ? sma_top + sma_lid_clr - (lid_t - lid_local_min) : 0);
z_seam     = z_pcb_top + top_clear;              // lid underside
z_wall     = z_seam - seam_gap;                  // base wall top
z_top      = z_seam + lid_t;
sma_recess = use_sma ? max(0, sma_top + sma_lid_clr - top_clear) : 0;   // lid underside recess over the flange
lip_band   = lip_clr + lip_t - pcb_clr;          // lid lip overlap onto the board edge

// ---- rounded shell profile (round revision) ----
// The profile lives in a section plane: o = outward offset from the nominal
// outline, z = height. A plan point at inset u from the nominal outline sits
// at o = -u, and for a convex outline its 3D distance to the shell surface is
// the 2D distance from [-u, z] to the profile.
pf_Cs   = [bulge - side_r, bulge_z];                 // side arc centre
function pf_ang(C) = atan2(C[1] - pf_Cs[1], C[0] - pf_Cs[0]);
// centres C on the line n.C = k at distance D from pf_Cs
function pf_cand(k, n, p, D) = let(w = k * n - pf_Cs, wp = w * p, disc = wp * wp - w * w + D * D)
    disc < 0 ? [] : [k * n + (-wp - sqrt(disc)) * p, k * n + (-wp + sqrt(disc)) * p];
// bottom round: tangent to the bot_ang chamfer through [-bot_inset, 0] and
// inside the side arc
pf_nb   = [cos(bot_ang), -sin(bot_ang)];
pf_cb   = [for (C = pf_cand(pf_nb * [-bot_inset, 0] - bot_r, pf_nb, [sin(bot_ang), cos(bot_ang)], side_r - bot_r))
             if (pf_ang(C) > -bot_ang && pf_ang(C) < 90) C];
pf_ok_b = len(pf_cb) > 0;
pf_Cb   = !pf_ok_b ? [0, 0] : len(pf_cb) == 1 ? pf_cb[0] : pf_ang(pf_cb[0]) < pf_ang(pf_cb[1]) ? pf_cb[0] : pf_cb[1];
pf_thb  = pf_ang(pf_Cb);
// top round: tangent to the top_ang chamfer through [-top_inset, z_top]
pf_nt   = [cos(top_ang), sin(top_ang)];
pf_ct   = [for (C = pf_cand(pf_nt * [-top_inset, z_top] - top_r, pf_nt, [-sin(top_ang), cos(top_ang)], side_r - top_r))
             if (pf_ang(C) > pf_thb && pf_ang(C) < top_ang) C];
pf_ok_t = len(pf_ct) > 0;
pf_Ct   = !pf_ok_t ? [0, z_top] : len(pf_ct) == 1 ? pf_ct[0] : pf_ang(pf_ct[0]) > pf_ang(pf_ct[1]) ? pf_ct[0] : pf_ct[1];
pf_tht  = pf_ang(pf_Ct);
function pf_arc(C, r, a0, a1) = let(n = max(1, ceil(abs(a1 - a0) / prof_step - 1e-6)))
    [for (i = [0 : n]) C + r * [cos(a0 + (a1 - a0) * i / n), sin(a0 + (a1 - a0) * i / n)]];
pf_side = pf_arc(pf_Cs, side_r, pf_thb, pf_tht);
pf_raw  = concat([[-bot_inset, 0]], pf_arc(pf_Cb, bot_r, -bot_ang, pf_thb),
                 [for (i = [1 : len(pf_side) - 2]) pf_side[i]],
                 pf_arc(pf_Ct, top_r, pf_tht, top_ang), [[-top_inset, z_top]]);
prof    = [for (i = [0 : len(pf_raw) - 1]) if (i == 0 || pf_raw[i][1] > pf_raw[i - 1][1] + 1e-3) pf_raw[i]];
pf_lut  = [for (p = prof) [p[1], p[0]]];
function o_at(z) = lookup(z, pf_lut);               // outline offset at height z
function seg_d(q, a, b) = let(d = b - a, L = d * d, t = L > 0 ? max(0, min(1, (q - a) * d / L)) : 0)
    norm(q - a - t * d);
// signed distance (+ inside the shell) from a point at inset u, height z
function prof_sd(u, z) = let(d = min([for (i = [1 : len(prof) - 1]) seg_d([-u, z], prof[i - 1], prof[i])]))
    -u <= o_at(z) ? d : -d;
// min plastic from a vertical line at inset u, z0..z1, to the outside
function wall_at(u, z0, z1, n = 24) = min([for (i = [0 : n]) prof_sd(u, z0 + (z1 - z0) * i / n)]);
// overhangs: base (z <= z_wall) outward growth going up, lid inward growth
pf_ovh_base = max([for (i = [1 : len(prof) - 1]) if (prof[i][1] <= z_wall + 1e-6)
                     atan2(prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1])]);
pf_ovh_lid  = max([for (i = [1 : len(prof) - 1]) if (prof[i - 1][1] >= z_seam - 1e-6)
                     atan2(prof[i - 1][0] - prof[i][0], prof[i][1] - prof[i - 1][1])]);
pf_omax = max([for (p = prof) p[0]]);
pf_omin_cav = min([for (i = [0 : 24]) o_at(z_floor + (z_wall - z_floor) * i / 24)]);
pf_seam_ang = atan2(o_at(z_seam - 0.05) - o_at(z_seam + 0.05), 0.1);   // inward lean at the seam
// plan corners. Nominal corner wall (cavity corner radius cav_r, outside R)
// along the diagonal; auto R = largest 0.1 step with wall_min everywhere
function wc(R) = R >= cav_r + wall_t ? R - sqrt(2) * (R - cav_r - wall_t) - cav_r : wall_t;
// (out_r itself is set after the lid flex pocket, which also limits it)
// rounded-rectangle signed inset (+ inside) of plan point p
function rr_in(p, a, b, r) = let(c = (a + b) / 2, h = (b - a) / 2 - [r, r],
                                 q = [abs(p[0] - c[0]) - h[0], abs(p[1] - c[1]) - h[1]])
    r - (norm([max(q[0], 0), max(q[1], 0)]) + min(max(q[0], q[1]), 0));
function out_in(p) = rr_in(p, [-out_x, out_y0], [out_x, out_y1], out_r);   // inset from the nominal outline
// board corner check: hole centre to the board edge (board coords)
function bd_in(h) = rr_in(h, [0, 0], [pcb_W, pcb_L], pcb_r);
function pcb_r_max(k) = let(i = min([for (h = holes_pcb) min(h[0], h[1], pcb_W - h[0], pcb_L - h[1])]))
    k > i + 1e-6 ? 0 : (sqrt(2) * i - k) / (sqrt(2) - 1);   // symmetric corner holes at inset i
// widest outline and faces
out_w   = 2 * (out_x + pf_omax);
out_l   = out_y1 - out_y0 + 2 * pf_omax;

// floor pockets
pin_xy      = patch_xy + patch_pin_off;
pin_below   = patch_pin - pcb_t;                 // conservative protrusion (ignores the tape)
z_pin_floor = use_patch && pin_pocket ? min(z_floor, snap_dn(z_pcb_bot - pin_below - 0.3)) : z_floor;
flange_loc  = [[-tx_jw - sma_pocket_clr, -tx_jt - sma_pocket_clr], [tx_jw + sma_pocket_clr, 0]];
leg_ok      = [for (i = [-1, 1]) off_ring(grect(tx_s, tx_along, leg_loc(i, sma_leg_l, sma_pocket_clr)), pocket_wall)];
leg_cut     = [for (k = [0, 1]) use_sma && !leg_ok[k] && sma_leg_cut];
leg_len     = [for (k = [0, 1]) leg_cut[k] ? sma_leg_stub : sma_leg_l];
leg_pkt     = [for (k = [0, 1]) use_sma && sma_pocket && (leg_ok[k] || leg_cut[k])];
z_sma_floor = use_sma && sma_pocket
    ? min(z_floor, snap_dn(min(sma_z - sma_body[2] / 2, z_pcb_bot - sma_leg_below) - sma_pocket_clr))
    : z_floor;
stake_xy    = [for (s = usb_stakes) [usb_x + s[0], pcb_y0 - usb_overhang + s[1]]];
z_usb_floor = usb_stake_pocket ? min(z_floor, max(z_pause, snap_dn(z_pcb_bot - usb_stake_below - 0.2)))
                               : z_floor;

// PCB screws: longest stock length (under the head) through the board
// whose tip stops 0.3 mm above the bottom of the insert / pilot hole
tip_z       = z_hole_bot + 0.3;
fits        = [for (l = screw_lengths) if (l <= z_pcb_top - tip_z) l];
screw_L     = len(fits) > 0 ? max(fits) : 0;
engage      = screw_L - pcb_t;                   // thread below the board

// snap fit: beads on the lid lip, grooves in the base walls
snap_z  = z_seam - lip_h + 0.4 + snap_p;         // bead centre height
snap_gd = snap_p - lip_clr + snap_clr;           // groove depth into the wall

// ---- TX: FXP70 flex antenna, U.FL (J3) and cable ----
fxp_bay   = use_fxp && fxp_mount == "bay";          // fxp70 side bay
fxp_lid   = use_fxp && fxp_mount == "lid";          // this revision: flex in the lid
ufl_xy    = [pcb_x0 + ufl_pos[0], pcb_y0 + ufl_pos[1]];
pcb_xr    = pcb_x0 + pcb_W;                        // board right edge
lip_in    = cav_x - lip_clr - lip_t;               // inner face of the lid lip, right wall
x_run     = ufl_xy[0];                             // cable run over the board (plug axis)
y_crimp   = ufl_xy[1] - ufl_crimp;                 // cable leaves the crimp heading -Y
z_plug_c  = z_pcb_top + ufl_cable_z;
z_lie     = z_pcb_top + cable_d / 2;               // cable centre lying on the board
// flex pocket on the shelf
pk_d      = layer_h * ceil((fxp_t + fxp_adh) / layer_h - 1e-6);   // whole layers
z_shelf   = snap_dn(z_seam - fxp_lid_air - fxp_solder_h - (fxp_t + fxp_adh - pk_d));
z_pk      = z_shelf - pk_d;                        // pocket floor
z_flex_nom = z_pk + fxp_adh + fxp_t_nom;           // flex top, nominal
z_flex_max = z_pk + fxp_adh + fxp_t;               // flex top, worst case
z_cab_flex = z_flex_nom + cable_d / 2;
pk_x0     = pcb_xr + ant_gnd_gap;                  // pocket inner edge
fx0       = pk_x0 + fxp_clr;                       // flex cable-exit edge, nominal
pk_x1     = pk_x0 + fxp_sz[0] + fxp_tol + 2 * fxp_clr;
// cable path: crimp -> end of the straight lead (now on the board) -> start
// of the bend -> end of the bend (heading +X) -> flex edge. Only the run
// along -Y depends on the exit height y_c; solve it for the nominal free
// length. The pocket lets the flex move fxp_slide either way in Y.
cable_free = cable_len - fxp_cable_pad;
cab_p0    = [x_run, y_crimp, z_plug_c];
cab_p1    = [x_run, y_crimp - cable_lead, z_lie];
cab_l01   = norm(cab_p1 - cab_p0);
cab_arc   = PI * cable_bend_r / 2;
cab_x3    = x_run + cable_bend_r;                  // end of the bend
cab_l34   = norm([fx0 - cab_x3, z_cab_flex - z_lie]);
y_c       = y_crimp - cable_lead - cable_bend_r + cab_l01 + cab_arc + cab_l34 - cable_free;
y_c_lo    = y_c - fxp_slide;                       // cable_len + tol: flex lower
y_c_hi    = y_c + fxp_slide;                       // cable_len - tol: flex higher
cab_run   = y_crimp - cable_lead - cable_bend_r - y_c_hi;   // shortest straight run along -Y
function cab_pts(yc) = concat([cab_p0, cab_p1],
    [for (i = [0 : 8]) let(a = 90 * i / 8)
        [x_run + cable_bend_r * (1 - cos(a)), yc + cable_bend_r * (1 - sin(a)), z_lie]],
    [[fx0, yc, z_cab_flex], [fx0 + fxp_on_flex, yc, z_cab_flex]]);
function pl_len(p, n) = n < 1 ? 0 : norm(p[n] - p[n - 1]) + pl_len(p, n - 1);
cab_len_chk = pl_len(cab_pts(y_c), len(cab_pts(y_c)) - 2);  // crimp to flex edge (chorded arc)
function z_cab_bot(x) = z_pcb_top + max(0, min(1, (x - cab_x3) / (fx0 - cab_x3))) * (z_flex_nom - z_pcb_top);
slot_hw   = cable_d / 2 + 0.25;                    // cable slot / trough half-width at one position
slot_y0   = y_c_lo - slot_hw;
slot_y1   = y_c_hi + slot_hw;
slot_c    = (slot_y0 + slot_y1) / 2;
// pocket in Y: the cable sits fxp_c_off below the flex's top (+Y) edge
pk_y1     = y_c_hi + fxp_c_off + fxp_c_off_tol + fxp_clr;
pk_y0     = y_c_lo - (fxp_sz[1] + fxp_tol - fxp_c_off + fxp_c_off_tol) - fxp_clr;
// antenna bay: shares the main right wall; bottom wall flush with the main one
bay_lip_w = lip_clr + lip_t + 0.2;                 // room for the lid lip on the bay's top wall
bay_cx0   = out_x;
bay_cx1   = pk_x1 + shelf_rim;
bay_cy0   = cav_y0;
shelf_y1  = pk_y1 + shelf_rim;
bay_cy1   = shelf_y1 + (snap_bay ? bay_lip_w : 0);
bay_ox1   = bay_cx1 + wall_t;
bay_oy1   = bay_cy1 + wall_t;
z_bay_floor = snap_up(floor_web);
bay_snap_x = (bay_cx0 + bay_cx1) / 2;
out_x1    = fxp_bay ? bay_ox1 : out_x;             // outside right edge
// flex area covered for every slide position and tolerance
flex_sure = [[pk_x1 - (fxp_sz[0] - fxp_tol), y_c_hi + fxp_c_off + fxp_c_off_tol - (fxp_sz[1] - fxp_tol)],
             [pk_x0 + fxp_sz[0] - fxp_tol, y_c_lo + fxp_c_off - fxp_c_off_tol]];
hd_in     = holddown_d / 2 + 0.3;
hd_pts    = [[flex_sure[1][0] - hd_in, flex_sure[0][1] + hd_in], [flex_sure[1][0] - hd_in, flex_sure[1][1] - hd_in],
             [flex_sure[0][0] + hd_in, flex_sure[0][1] + hd_in]];
// lid-side cable keepers: [x0, y0, x1, y1, end height]
trough_xm = (bay_cx0 + pk_x0) / 2;
keepers   = concat([for (y = keeper_y) [x_run - keeper_sz[0] / 2, y - keeper_sz[1] / 2,
                                        x_run + keeper_sz[0] / 2, y + keeper_sz[1] / 2,
                                        z_pcb_top + cable_d + keeper_clr]],
                   [[trough_xm - 1.5, slot_y0 - 0.5, trough_xm + 1.5, slot_y1 + 0.5,
                     z_cab_bot(trough_xm) + cable_d + keeper_clr]]);
// distances reported and checked
patch_a   = patch_xy - [patch_fp, patch_fp] / 2;
patch_b   = patch_xy + [patch_fp, patch_fp] / 2;
fxp_rx_d  = rr_dist(patch_a, patch_b, [pk_x0, pk_y0], [pk_x1, pk_y1]);
fxp_c     = [(pk_x0 + pk_x1) / 2, (pk_y0 + pk_y1) / 2];
cab_rx_d  = x_run - cable_d / 2 - patch_b[0];

// ---- TX in the lid (fxp_mount = "lid") ----
// Flex 26.9 (X) x 24.9 (Y), adhesive up against the pocket ceiling, cable side
// down. Its exit edge faces the patch window; the cable leaves it toward -Y at
// fxp_c_off from the flex's +X edge. The flex is pushed into the pocket's +X /
// +Y corner, so the cable X follows the pocket and the flex keeps the most
// distance from the window that the pocket allows.
// Cable: on the flex -> groove -> lid leg in clip rails (-Y, against the lid
// underside) -> tilted 180 deg hairpin of radius hp_r (lid level, inner, to
// board level, outer) -> board leg (+Y, lying on the board at its right edge)
// -> S-jog (two hp_r arcs) to the plug axis -> straight lead into the crimp
// (plug cable toward -Y, as fxp70). The hairpin floats: it takes up the
// 53 +/-2 cable tolerance by moving +/-1 in Y.
fl_x      = fxp_sz[1];                             // 26.9, carries the cable exit
fl_y      = fxp_sz[0];                             // 24.9
win_y1    = patch_xy[1] + radome_w / 2;            // patch window edge toward the top band
win_x1    = patch_xy[0] + radome_w / 2;            // window edge toward the right wall
z_lpk     = z_top - lid_skin;                      // pocket ceiling
lpk_d     = z_lpk - z_seam;                        // pocket depth into the lid underside
z_fl_lo_nom = z_lpk - fxp_adh - fxp_t_nom;         // flex cable-side face, nominal (highest)
z_fl_lo_max = z_lpk - fxp_adh - fxp_t;             // worst (thickest) flex: lowest face
z_fl_mid  = z_lpk - fxp_adh - fxp_t_nom / 2;       // copper, nominal
z_cab_on  = z_fl_lo_nom - cable_d / 2;             // cable centre lying on the flex
z_ll      = z_seam - cable_d / 2;                  // lid leg: cable against the lid underside
z_bl      = z_lie;                                 // board leg: cable lying on the board
hp_r      = cable_bend_r;
hp_dz     = z_ll - z_bl;
hp_s      = sqrt(max(0, 4 * hp_r * hp_r - hp_dz * hp_dz));   // hairpin leg spacing in X
x_bl      = min(cav_x - leg_wall_clr, pcb_xr) - cable_d / 2; // board leg, on the board's right edge
x_ll      = x_bl - hp_s;                           // lid leg = cable exit X
x_ex_tol  = fxp_c_off_tol + 0.1;                   // exit X tolerance (offset + pushing)
lpk_x1    = x_ll + fxp_c_off;                      // pocket +X edge = flex +X edge
lpk_x0    = lpk_x1 - (fl_x + fxp_tol + 2 * lid_fxp_clr);
lpk_y0    = win_y1 + win_web;
lpk_y1    = lpk_y0 + fl_y + fxp_tol + 2 * lid_fxp_clr;
fl_y0     = lpk_y1 - fl_y;                         // flex exit edge, nominal flex
fl_y0_lo  = lpk_y1 - (fl_y + fxp_tol);             // largest flex (closest to the window)
fl_y0_hi  = lpk_y1 - (fl_y - fxp_tol);
fl_c      = [lpk_x1 - fl_x / 2, lpk_y1 - fl_y / 2];  // flex centre, nominal
y_clip0   = fl_y0 - clip_off;                      // first clip (fixed in the lid)
// S-jog from the board leg (x_bl) to the plug axis (x_run), then the lead
jog_h     = x_bl - x_run;
jog_th    = acos(max(-1, min(1, 1 - jog_h / (2 * hp_r))));   // degrees
jog_run   = 2 * hp_r * sin(jog_th);
jog_arc   = 2 * hp_r * jog_th * PI / 180;
y_j1      = y_crimp - cable_lead;                  // end of the jog = start of the lead
y_j0      = y_j1 - jog_run;                        // start of the jog = end of the board leg
lead_l    = norm([0, cable_lead, z_plug_c - z_bl]);
// free length L from the flex edge yf to the crimp:
//   drop to the first clip + lid leg + pi hp_r + board leg + jog + lead
function y_hp(L, yf) = (norm([0, yf - y_clip0, z_cab_on - z_ll]) + y_clip0 + PI * hp_r
                        + y_j0 + jog_arc + lead_l - L) / 2;
y_u       = y_hp(cable_free, fl_y0);               // hairpin ends (both legs), nominal
y_u_lo    = y_hp(cable_free + cable_tol, fl_y0_lo); // longest cable: hairpin lowest
y_u_hi    = y_hp(cable_free - cable_tol, fl_y0_hi); // shortest cable: hairpin highest
// hairpin: a 3D semicircle of radius hp_r from the board leg (ph 0) to the lid leg (ph 180)
function hp_pt(yu, ph) = [(x_ll + x_bl) / 2 + hp_s / 2 * cos(ph), yu - hp_r * sin(ph),
                          (z_ll + z_bl) / 2 + (z_bl - z_ll) / 2 * cos(ph)];
function lcab_pts(yu) = concat(
    [[x_ll, fl_y0 + fxp_on_flex, z_cab_on], [x_ll, fl_y0, z_cab_on], [x_ll, y_clip0, z_ll]],
    [for (i = [0 : 16]) hp_pt(yu, 180 - 180 * i / 16)],
    [for (i = [0 : 8]) let(a = jog_th * i / 8) [x_bl - hp_r * (1 - cos(a)), y_j0 + hp_r * sin(a), z_bl]],
    [for (i = [1 : 8]) let(b = jog_th * (8 - i) / 8) [x_run + hp_r * (1 - cos(b)), y_j1 - hp_r * sin(b), z_bl]],
    [[x_run, y_crimp, z_plug_c]]);
lcab      = lcab_pts(y_u);
lcab_chk  = pl_len(lcab, len(lcab) - 1) - norm(lcab[1] - lcab[0]);   // flex edge to crimp
// lid features
rail_lo   = y_u_hi + rail_end_m;                   // rails end above the highest hairpin
rail_hw   = cable_d / 2 + rail_clr;                // half gap between the rails
z_cab_bot_ll = z_ll - cable_d / 2;
z_rail_bot = z_cab_bot_ll - 0.4;                   // rails reach 0.4 below the cable
groove_hw = cable_d / 2 + x_ex_tol + groove_clr;
top_cut   = [lpk_x0 - lip_cut_m, lpk_x1 + lip_cut_m];    // top-wall lid lip removed
notch_need = x_bl + cable_d / 2 > lip_in - 0.3;
// lid keepers [x0, y0, x1, y1, end height]: board leg straight, S-jog midpoint
lk_bl_y   = (y_u_hi + y_j0) / 2;
jm        = [(x_bl + x_run) / 2, y_j0 + jog_run / 2];      // jog midpoint (inflection)
lk_len_j  = 2.0;                                           // jog keeper length (Y)
jm_dx     = lk_len_j / 2 * tan(jog_th);                    // cable X change over the keeper
notch_y   = [y_u_lo - hp_r - lip_cut_m, jm[1] + lk_len_j / 2 + lip_cut_m];   // right-wall lip notch
lkeepers  = [[x_bl - lk_w / 2, lk_bl_y - lk_len / 2, min(x_bl + lk_w / 2, cav_x - lip_clr), lk_bl_y + lk_len / 2,
              z_pcb_top + cable_d + keeper_clr],
             [jm[0] - jm_dx - lk_w / 2, jm[1] - lk_len_j / 2, min(jm[0] + jm_dx + lk_w / 2, cav_x - lip_clr), jm[1] + lk_len_j / 2,
              z_pcb_top + cable_d + keeper_clr]];
// distances reported and checked
l_gnd     = z_fl_mid - z_pcb_top;                  // flex copper over the board-top GND pour
l_gnd2    = l_gnd + 0.035 + 0.2104;                // ... over the solid L2 GND (stackup)
l_rx      = fl_y0_lo - patch_b[1];                 // flex to patch footprint, worst (largest flex)
l_rx_nom  = fl_y0 - (patch_xy[1] + patch_sz / 2);  // nominal flex to nominal patch
l_win     = fl_y0_lo - win_y1;                     // flex to the window edge, worst
// lid leg to the patch footprint: the free cable from the flex edge (x_ll +/-
// x_ex_tol) to the first clip (x_ll), then the rails and the hairpin (x >= x_ll)
l_cab_rx  = min([for (t = [0 : 0.1 : 1]) rect_dist([x_ll - x_ex_tol * (1 - t), fl_y0 - t * (fl_y0 - y_clip0)],
                                                   patch_a, patch_b) - cable_d / 2]);
l_ufl_xy  = ufl_xy[0] - ufl_plug_w / 2 - lpk_x1;   // flex +X edge to the plug body, in plane
l_ufl_z   = z_fl_lo_nom - (z_pcb_top + ufl_mated_h);
l_ufl     = norm([max(0, l_ufl_xy), max(0, l_ufl_z)]);
fl_route  = [[x_ll - x_ex_tol - cable_d / 2 - 0.3, y_u_lo - hp_r - cable_d / 2 - 0.3],
             [x_bl + cable_d / 2 + 0.3, y_crimp]];   // hairpin + board leg + jog + lead
// image theory: horizontal current at height h over a ground plane; radiated
// power (radiation resistance) relative to free space for the same current
function img_ratio(h) = let(x = 2 * (2 * PI * fxp_freq / 299.792458) * h, d = 180 / PI)
    2 * (1 - 1.5 * (sin(x * d) / x + cos(x * d) / (x * x) - sin(x * d) / (x * x * x)));
// true if point p lies inside the outer outline shrunk by m
function in_outer(p, m) = let(cx = min(max(p[0], -out_x + out_r), out_x - out_r),
                              cy = min(max(p[1], out_y0 + out_r), out_y1 - out_r))
    abs(p[0]) <= out_x - m && p[1] >= out_y0 + m && p[1] <= out_y1 - m
    && norm([p[0] - cx, p[1] - cy]) <= out_r - m + 1e-6;
// flex pocket outline samples (rim / skin checks against the rounded edge)
lpk_ring = [for (i = [0 : 10]) each [[lpk_x0 + (lpk_x1 - lpk_x0) * i / 10, lpk_y0], [lpk_x0 + (lpk_x1 - lpk_x0) * i / 10, lpk_y1],
                                    [lpk_x0, lpk_y0 + (lpk_y1 - lpk_y0) * i / 10], [lpk_x1, lpk_y0 + (lpk_y1 - lpk_y0) * i / 10]]];
// plan corner radius: largest 0.1 step with wall_min at the cavity corners
// and, in lid mode, the flex pocket rim / skin kept at the rounded corners
function pk_ok(R) = !fxp_lid || min([for (p = lpk_ring) let(u = rr_in(p, [-out_x, out_y0], [out_x, out_y1], R))
                                      min(prof_sd(u, z_seam) - pk_rim_min, prof_sd(u, z_lpk) - lid_skin_min)]) >= -1e-6;
pf_R_auto = [for (R = [floor((cav_r + wall_t + 8) * 10) / 10 : -0.1 : cav_r + wall_t - 1e-6])
               if (wall_at(wc(R), z_floor, z_wall) >= wall_min - 1e-6 && pk_ok(R)) R];
out_r   = corner_r > 0 ? corner_r : len(pf_R_auto) > 0 ? pf_R_auto[0] : cav_r + wall_t;
// snap beads (after the bay, which carries one)
snaps   = concat([for (y = snap_right_y) [1, y]], [for (y = snap_side_y) [3, y]],
                 [for (x = snap_top_x) [0, x]], [for (x = snap_bot_x) [2, x]],
                 fxp_bay && snap_bay ? [[4, bay_snap_x]] : []);

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
    assert(!use_sma || s[0] != tx_s || abs(s[1] - tx_along) >= snap_len / 2 + max(tx_jw, sma_hole / 2) + 1,
        str("Snap bead ", s, " runs into the TX slot"));
    assert(s[0] != 2 || abs(s[1] - usb_x) >= snap_len / 2 + usb_open_w / 2 + 1,
        str("Snap bead ", s, " runs into the USB-C opening"));
    assert(!pry_notch || s[0] != 2 || abs(s[1] - pry_x) >= snap_len / 2 + pry_w / 2 + 1,
        str("Snap bead ", s, " runs into the pry notch"));
}
assert(!pry_notch || (abs(pry_x - usb_x) >= usb_open_w / 2 + pry_w / 2 + 1
                   && pry_x - pry_w / 2 >= side_run(2)[0] && pry_x + pry_w / 2 <= side_run(2)[1]
                   && (!use_sma || tx_s != 2 || abs(pry_x - tx_along) >= pry_w / 2 + sma_hole / 2 + 1)),
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
    assert(!use_sma || rect_dist(holes[i], jack_a, jack_b) >= max(standoff_d, screw_head_d) / 2 + 0.3,
        str("Board hole ", holes_pcb[i], " collides with the TX jack; move tx_pos"));
}
assert(!use_patch || (patch_c[0] - patch_fp / 2 >= 1 && patch_c[0] + patch_fp / 2 <= pcb_W - 1
                   && patch_c[1] - patch_fp / 2 >= 1 && patch_c[1] + patch_fp / 2 <= pcb_L - 1),
    "RX patch footprint runs off the board; move patch_pos");
// (rev_pcb checked z_floor; here the floor under the pin is the pin pocket's)
assert(!use_patch || z_pcb_bot - z_pin_floor >= patch_pin - pcb_t + 0.3 - 1e-6,
    "RX patch feed pin and solder reach the floor; enable pin_pocket, raise pcb_gap or trim the pin");
assert(patch_cover > 0 && patch_cover <= lid_t, "patch_cover must be in (0, lid_t]");
assert(!use_sma || (tx_along - max(tx_jw, sma_hole / 2) - 0.5 >= side_run(tx_s)[0]
                && tx_along + max(tx_jw, sma_hole / 2) + 0.5 <= side_run(tx_s)[1]),
    "TX jack runs onto a corner radius; move tx_pos");
assert(!use_sma || (tx_gap >= -1e-6 && tx_notch > 0),
    "Board edge on the TX side must sit within the jack body thickness of the wall");
assert(!use_sma || (tx_notch + tx_gap >= tx_jt + 0.1 - 1e-6 && tx_nw >= tx_jw + 0.2 - 1e-6),
    str("Board notch ", r2(tx_notch), " x ", r2(2 * tx_nw), " mm is too small for the ",
        sma_body[0], " x ", tx_jt, " mm jack flange; enlarge tx_notch_d / tx_notch_w"));
// the slot, its lower arc and the tongue's arc are all concentric with the
// barrel at sma_hole, so the radial clearance is (sma_hole - sma_thread) / 2
assert(!use_sma || sma_hole - sma_thread >= 0.2 - 1e-6,
    "SMA slot/tongue leave under 0.1 mm radial on the 1/4-36 barrel; raise sma_clr");
assert(!vent_slots || (vent_n >= 1 && vent_pitch > vent_w + 0.8),
    "Vent slots need vent_n >= 1 and at least 0.8 mm of lid between slots");
assert(!vent_slots || (vent_a[0] >= -cav_x + lip_clr + lip_t + 1 && vent_b[0] <= cav_x - lip_clr - lip_t - 1
                    && vent_a[1] >= cav_y0 + lip_clr + lip_t + 1 && vent_b[1] <= cav_y1 - lip_clr - lip_t - 1),
    "Vent slots run onto the lid lip; move vent_c or shorten them");
assert(!vent_slots || !use_patch || !rects_hit(vent_a, vent_b, patch_xy - [radome_w, radome_w] / 2,
                                               patch_xy + [radome_w, radome_w] / 2, 3),
    "Vent slots within 3 mm of the RX patch radome; move vent_c");
assert(!vent_slots || !use_sma || !rects_hit(vent_a, vent_b, jack_a, jack_b, vent_keep),
    str("Vent slots within ", vent_keep, " mm of the TX jack; move vent_c"));
// (rev_pcb checked z_floor; here the floor under the jack is the SMA pocket's)
assert(!use_sma || sma_z - sma_body[2] / 2 >= z_sma_floor + 0.2 - 1e-6,
    "TX jack body hits the floor; enable sma_pocket, raise pcb_gap or sma_axis_z");
assert(!use_sma || sma_z - sma_hole / 2 >= skin_t + 0.6, "TX jack hole reaches the skin");
assert(!use_sma || sma_barrel - wall_t >= 4.0,
    "Too little SMA thread outside the wall for the antenna to seat; use a longer-barrel jack");
assert(!use_sma || tx_s != 2 || abs(tx_along - usb_x) >= max(tx_jw, sma_hole / 2) + usb_open_w / 2 + 1,
    "TX jack and USB-C opening overlap on the bottom wall");
assert(!(use_sma && use_patch) || !rects_hit(patch_xy - [patch_fp, patch_fp] / 2,
                                           patch_xy + [patch_fp, patch_fp] / 2, jack_a, jack_b, 1),
    "RX patch runs into the TX jack");

// ---- low-profile checks ----
assert(lid_t >= 1.0 - 1e-6, "lid_t below 1.0 mm: too thin for a PETG snap lid");
assert(pcb_gap >= 0.3 - 1e-6, "pcb_gap below 0.3 mm (flat pads, board bow, cap pillowing)");
assert(z_seam - lip_h - z_pcb_top >= edge_parts_h + 0.1 - 1e-6,
    str("Only ", r2(z_seam - lip_h - z_pcb_top), " mm under the lid lip for ", edge_parts_h,
        " mm edge parts; reduce lip_h (>= 2.2) or raise top_clear"));
for (i = [0 : len(holes) - 1]) let(h = holes_pcb[i])
    assert(min(h[0], h[1], pcb_W - h[0], pcb_L - h[1]) - screw_head_d / 2 >= lip_band + 0.3 - 1e-6
           || z_pcb_top + screw_head_h + 0.3 <= z_seam - lip_h,
        str("Screw head at board hole ", h, " runs under the lid lip"));
assert(sma_recess <= lid_t - lid_local_min + 1e-6,
    str("SMA lid recess leaves under ", lid_local_min, " mm of lid"));
assert(!use_patch || patch_tape <= patch_tape_max + 1e-6, "patch_tape above patch_tape_max");
assert(!use_patch || !patch_window
       || (patch_margin >= 1.0 - 1e-6 && z_top - (z_pcb_top + patch_top_max) >= patch_recess_min - 1e-6),
    "Patch window: keep patch_margin >= 1.0 and the worst-case patch top patch_recess_min below the lid face");
assert(!use_patch || patch_window
       || z_top - patch_cover - (z_pcb_top + patch_top_max) >= patch_air_min - 1e-6,
    str("Radome: under ", patch_air_min, " mm of air over the patch at patch_tape_max; raise patch_gap"));
assert(usb_open_top || usb_z0 + usb_open_h <= z_seam + 1e-6,
    "USB-C overmold opening is taller than the base wall; set usb_open_top or raise top_clear");
// patch feed pin pocket
assert(!use_patch || !pin_pocket
       || norm(pin_xy) + pin_pocket_d / 2 <= ring_ri - pocket_wall
       || norm(pin_xy) - pin_pocket_d / 2 >= ring_ro + pocket_wall,
    "Feed pin pocket runs into the ring pocket");
assert(!use_patch || !pin_pocket || !use_clock
       || rect_dist(pin_xy, [clk_x0, clk_y0], [clk_x1, clk_y1]) >= pin_pocket_d / 2 + pocket_wall,
    "Feed pin pocket runs into the clocking-magnet pocket");
assert(!use_patch || !pin_pocket || !label || abs(pin_xy[1]) - pin_pocket_d / 2 >= 5,
    "Feed pin pocket runs into the MAGNETS DOWN / STEEL UP label");
assert(z_pin_floor >= floor_web - 1e-6 && z_sma_floor >= floor_web - 1e-6 && z_usb_floor >= floor_web - 1e-6,
    "A floor pocket comes within floor_web of the phone face");
// SMA flange / leg pocket
assert(!use_sma || !sma_pocket || off_ring(grect(tx_s, tx_along, flange_loc), pocket_wall),
    "SMA flange pocket runs into the ring pocket");
for (k = [0, 1]) {
    assert(!leg_pkt[k] || off_ring(grect(tx_s, tx_along, leg_loc(2 * k - 1, leg_len[k], sma_pocket_clr)), pocket_wall),
        str("SMA leg ", k, " pocket (", r2(leg_len[k]), " mm leg) runs into the ring pocket; shorten sma_leg_stub"));
    assert(!use_sma || !leg_pkt[k] || z_pcb_bot - sma_leg_below - z_sma_floor >= 0.2 - 1e-6,
        str("SMA lower leg ", k, " hits its pocket floor"));
    assert(!use_sma || leg_pkt[k] || z_pcb_bot - sma_leg_below - z_floor >= 0.2 - 1e-6,
        str("SMA lower leg ", k, " lies over the ring and hits the cap: set sma_leg_cut = true (cut it) or pcb_gap = 1.3"));
}
// USB-C shell stakes
for (p = stake_xy) {
    assert(z_pcb_bot - usb_stake_below - z_usb_floor >= 0.2 - 1e-6,
        "USB-C shell stakes reach the floor; clip them or enable usb_stake_pocket");
    assert(!usb_stake_pocket || !use_clock
           || rr_dist(p - usb_stake_pkt / 2, p + usb_stake_pkt / 2, [clk_x0, clk_y0], [clk_x1, clk_y1])
              >= (z_usb_floor >= z_pause - 1e-6 ? 0.5 : pocket_wall) - 1e-6,
        "USB-C stake pocket too close to the clocking-magnet pocket");
    assert(!usb_stake_pocket || !use_clock
           || min([for (x = [clk_x0, clk_x1], y = [clk_y0, clk_y1])
                   rect_dist([x, y], p - usb_stake_pkt / 2, p + usb_stake_pkt / 2)]) >= 0.4 + 0.5,
        "USB-C stake pocket too close to a clocking-pocket corner relief");
    assert(!usb_stake_pocket || off_ring([p - usb_stake_pkt / 2, p + usb_stake_pkt / 2], pocket_wall),
        "USB-C stake pocket runs into the ring pocket");
}

// ---- FXP70 checks ----
assert(!(use_fxp && use_sma), "use_fxp and use_sma both on: the board has one TX output (J3)");
if (use_fxp) {
    // U.FL
    assert(ufl_pos[0] - ufl_plug_w / 2 >= 0.5 && ufl_pos[0] + ufl_plug_w / 2 <= pcb_W - 0.5
           && ufl_pos[1] - ufl_crimp >= 0.5 && ufl_pos[1] + ufl_plug_w / 2 <= pcb_L - 0.5,
        "U.FL plug runs off the board; check ufl_pos");
    assert(z_pcb_top + ufl_mated_h + ufl_lid_clr <= z_seam + 1e-6,
        str("Mated U.FL (", ufl_mated_h, " max) leaves under ", ufl_lid_clr, " mm to the lid"));
    assert(ufl_xy[0] + ufl_plug_w / 2 <= lip_in - 0.3 || z_pcb_top + ufl_mated_h + 0.3 <= z_seam - lip_h,
        "U.FL plug runs under the lid lip");
    assert(cable_bend_r >= cable_bend_min - 1e-6, str("Cable bend radius below ", cable_bend_min, " mm"));
    assert(fxp_mount == "lid" || fxp_mount == "bay", "fxp_mount must be \"lid\" or \"bay\"");
}
if (fxp_bay) {
    assert(!vent_slots || !rects_hit(vent_a, vent_b, [x_run - ufl_plug_w / 2, y_c_lo],
                                     [bay_ox1, ufl_xy[1] + ufl_plug_w / 2], vent_keep),
        str("Vent slots within ", vent_keep, " mm of the U.FL / TX cable; move vent_c"));
    // cable
    assert(cable_bend_r >= cable_bend_min - 1e-6, str("Cable bend radius below ", cable_bend_min, " mm"));
    assert(cable_lead >= 2 - 1e-6 && cab_run >= 0, str("Cable path too short for the ", cable_len,
        " mm cable: no straight run left before the bend (", r2(cab_run), "); raise ant_gnd_gap or cable_bend_r"));
    assert(fxp_slide >= cable_tol - 1e-6, "fxp_slide must cover the cable length tolerance");
    assert(abs(cab_len_chk - cable_free) <= 0.15, str("Cable path ", r2(cab_len_chk), " != free length ", cable_free));
    assert(cab_x3 <= cav_x - 0.2, "Cable bend runs into the right wall; the cable must cross it square");
    assert(x_run + cable_d / 2 + 0.3 <= lip_in, "Cable run over the board lies under the lid lip");
    // where the bend enters the lip band (x > lip_in - 0.3) the lip notch must cover it
    assert(sqrt(max(0, pow(cable_bend_r, 2) - pow(cab_x3 - (lip_in - 0.3), 2))) >= cable_bend_r - (slot_hw - cable_d / 2 + 0.3) - 1e-6
           || cab_x3 <= lip_in - 0.3,
        "Cable bend enters the lid lip band outside the lip notch; reduce cable_bend_r");
    assert(cab_rx_d >= cable_rx_min - 1e-6,
        str("TX cable only ", r2(cab_rx_d), " mm from the RX patch (min ", cable_rx_min, ")"));
    for (i = [0 : len(holes) - 1]) let(h = holes[i])
        assert(rect_dist(h, [x_run, y_c_lo], [cav_x, y_crimp]) >= screw_head_d / 2 + cable_d / 2 + 0.3
               || (rect_dist(h, [x_run, y_c_lo + cable_bend_r], [x_run, y_crimp]) >= screw_head_d / 2 + cable_d / 2 + 0.3
                   && rect_dist(h, [x_run, y_c_lo], [cav_x, y_c_hi + cable_bend_r]) >= screw_head_d / 2 + cable_d / 2 + 0.3),
            str("TX cable runs over the screw head at board hole ", holes_pcb[i]));
    for (s = snaps) if (s[0] == 1)
        assert(abs(s[1] - slot_c) >= snap_len / 2 + (slot_y1 - slot_y0) / 2 + 1,
            str("Right-wall snap bead at y ", s[1], " runs into the cable slot; edit snap_right_y"));
    assert(slot_y0 - 0.5 >= side_run(1)[0] && slot_y1 + 0.5 <= side_run(1)[1], "Cable slot runs onto a corner radius");
    assert(slot_y0 >= bay_cy0 + bay_r + 0.5 && slot_y1 <= shelf_y1 - 0.5, "Cable slot misses the antenna bay");
    for (k = keepers) {
        assert(k[4] < z_seam - 0.5, "Cable keeper shorter than 0.5 mm");
        assert(!use_patch || k[0] >= patch_xy[0] + radome_w / 2 + 1, "Cable keeper runs into the patch window");
        assert(k[2] <= lip_in - 0.3 || k[0] >= cav_x, "Cable keeper runs into the lid lip");
    }
    for (y = keeper_y)
        assert(y - keeper_sz[1] / 2 >= y_c_hi + cable_bend_r && y + keeper_sz[1] / 2 <= y_crimp - cable_lead,
            str("Cable keeper at y ", y, " is off the straight run"));
    // flex and its pocket
    assert(pk_x0 - pcb_xr >= ant_gnd_min - 1e-6,
        str("Flex pocket only ", r2(pk_x0 - pcb_xr), " mm from the board ground (Taoglas min ", ant_gnd_min, ")"));
    assert(pk_x0 >= out_x + 1, "Flex pocket must sit in the bay, outside the main wall");
    assert(fxp_rx_d >= ant_rx_min - 1e-6,
        str("Flex pocket only ", r2(fxp_rx_d), " mm from the RX patch (min ", ant_rx_min, ")"));
    assert(rect_dist([0, 0], [pk_x0, pk_y0], [pk_x1, pk_y1]) >= ring_od / 2 + 4,
        "Flex within 4 mm of the ring magnet");
    assert(pk_d >= fxp_t + fxp_adh - 1e-6 && pk_d <= fxp_t + fxp_adh + layer_h + 1e-6,
        "Flex pocket depth must hold flex + adhesive (within one layer)");
    assert(z_seam - (z_flex_max + fxp_solder_h) >= fxp_lid_air - 1e-6,
        "Worst-case flex solder joint hits the lid; lower z_shelf");
    assert(shelf_t - pk_d >= 0.8 - 1e-6, "Shelf under the flex pocket thinner than 0.8 mm");
    assert(z_shelf - shelf_t - z_bay_floor >= 1.0, "No room for the shelf ribs");
    assert(z_bay_floor >= floor_web - 1e-6, "Bay floor thinner than floor_web");
    assert(pk_y0 - bay_cy0 >= max(0.4, 0.3 * bay_r) - 1e-6 && bay_cx1 - pk_x1 >= max(0.4, 0.3 * bay_r) - 1e-6,
        str("Flex pocket leaves under 0.4 mm of shelf to the bay wall (", r2(pk_y0 - bay_cy0), ")"));
    assert(bay_oy1 <= out_y1 - out_r && bay_cy0 >= cav_y0 - 1e-6,
        "Antenna bay must stay within the main body's length");
    assert(z_cab_bot(bay_cx0) >= z_pcb_top - 1e-6, "Cable dips below the wall slot floor");
    assert(!fxp_holddown || z_shelf + holddown_gap - z_flex_max >= 0.1 - 1e-6,
        "Hold-down pins press on the worst-case flex");
    for (p = hd_pts)
        assert(!fxp_holddown || (p[0] - holddown_d / 2 >= flex_sure[0][0] && p[0] + holddown_d / 2 <= flex_sure[1][0]
                                && p[1] - holddown_d / 2 >= flex_sure[0][1] && p[1] + holddown_d / 2 <= flex_sure[1][1]
                                && (p[0] - holddown_d / 2 >= fx0 + fxp_on_flex + 1 || abs(p[1] - y_c) >= fxp_slide + holddown_d / 2 + cable_d)),
            str("Hold-down pin at ", p, " is off the flex or on its cable"));
}
// ---- FXP70 in the lid ----
if (fxp_lid) {
    // pocket and lid
    assert(lid_skin >= lid_skin_min - 1e-6, str("lid_skin over the flex below ", lid_skin_min, " mm"));
    assert(lpk_d >= fxp_t + fxp_adh + 0.05 - 1e-6,
        str("Flex pocket ", r2(lpk_d), " deep: worst-case flex + adhesive (", fxp_t + fxp_adh,
            ") must sit inside it; reduce lid_skin"));
    assert(z_fl_lo_max >= z_seam + 0.05 - 1e-6, "Worst-case flex hangs below the lid underside (wall top would press it)");
    assert(!use_patch || lpk_y0 - win_y1 >= win_web_min - 1e-6,
        str("Only ", r2(lpk_y0 - win_y1), " mm of lid between the patch window and the flex pocket (min ", win_web_min, ")"));
    assert(!use_patch || !rects_hit([lpk_x0, lpk_y0], [lpk_x1, lpk_y1], patch_xy - [radome_w, radome_w] / 2,
                                    patch_xy + [radome_w, radome_w] / 2, win_web_min - 1e-6),
        "Flex pocket covers or touches the patch window");
    // (fxp70_inlid checked the pocket corners against the flat outline; here
    // the rim and the skin are checked against the rounded edge, all round)
    for (p = lpk_ring) {
        assert(prof_sd(out_in(p), z_seam) >= pk_rim_min - 1e-6,
            str("Flex pocket edge at ", [r2(p[0]), r2(p[1])], " leaves ", r2(prof_sd(out_in(p), z_seam)),
                " mm to the rounded outer edge (min pk_rim_min ", pk_rim_min, "); reduce top_r / top_inset or bulge less"));
        assert(prof_sd(out_in(p), z_lpk) >= lid_skin_min - 1e-6,
            str("Rounded lid edge leaves ", r2(prof_sd(out_in(p), z_lpk)), " mm over the flex pocket edge at ",
                [r2(p[0]), r2(p[1])], " (min lid_skin_min ", lid_skin_min, "); reduce top_inset or top_r"));
    }
    assert(!usb_open_top || lpk_y0 > cav_y0 + 1, "Flex pocket runs into the USB-C lid notch");
    assert(!use_patch || l_rx >= lid_rx_min - 1e-6,
        str("Flex only ", r2(l_rx), " mm from the RX patch footprint (min lid_rx_min ", lid_rx_min, ")"));
    assert(l_gnd >= ant_gnd_min - 1e-6,
        str("Flex only ", r2(l_gnd), " mm above the board GND (Taoglas min ", ant_gnd_min, " from metal)"));
    assert(z_fl_lo_max - fxp_solder_h - (z_pcb_top + top_band_h) >= 0.3 - 1e-6,
        "Worst flex solder joint comes within 0.3 mm of the top_band_h parts under the flex");
    // flex-borne cable and solder joints clear of the mated plug (XY or Z)
    assert(ufl_xy[0] - ufl_plug_w / 2 - (x_ll + x_ex_tol + 1.25) >= 0.3
           || z_fl_lo_max - fxp_solder_h - (z_pcb_top + ufl_mated_h) >= 0.3,
        "Flex solder joints / cable on the flex run onto the mated U.FL plug");
    assert(lpk_x1 + 0.3 <= ufl_xy[0] - ufl_plug_w / 2 || l_ufl_z >= ufl_lid_clr - 1e-6,
        "Flex pocket lies over the mated U.FL with under ufl_lid_clr of air");
    // lid lip and beads
    for (s = snaps) {
        assert(s[0] != 0 || s[1] + snap_len / 2 + 1 <= top_cut[0] || s[1] - snap_len / 2 - 1 >= top_cut[1],
            str("Top-wall snap bead at x ", s[1], " is in the lid-lip cut over the flex pocket (x ",
                r2(top_cut[0]), " to ", r2(top_cut[1]), "); edit snap_top_x"));
        assert(s[0] != 1 || !notch_need || s[1] + snap_len / 2 + 1 <= notch_y[0] || s[1] - snap_len / 2 - 1 >= notch_y[1],
            str("Right-wall snap bead at y ", s[1], " is in the lid-lip notch over the cable (y ",
                r2(notch_y[0]), " to ", r2(notch_y[1]), "); edit snap_right_y"));
    }
    assert(len([for (s = snaps) if (s[0] == 0) 1]) >= 1 && len([for (s = snaps) if (s[0] == 1) 1]) >= 2,
        "Keep at least one top-wall and two right-wall snap beads");
    // cable route
    assert(hp_dz < 2 * hp_r - 0.5, "Hairpin legs are further apart in Z than the bend diameter");
    assert(l_cab_rx >= cable_rx_min - 1e-6,
        str("Lid-leg cable only ", r2(l_cab_rx), " mm from the RX patch (min ", cable_rx_min, ")"));
    assert(!use_patch || x_ll - x_ex_tol - rail_hw - rail_t >= win_x1 + 1.0 - 1e-6,
        "Clip rails come within 1 mm of the patch window");
    assert(x_bl + cable_d / 2 <= pcb_xr + 1e-6 && x_bl + cable_d / 2 <= cav_x - leg_wall_clr + 1e-6,
        "Board leg is off the board or against the wall");
    assert(jog_h > 0 && jog_h <= 2 * hp_r - 1e-6, "S-jog offset must be in (0, 2 hp_r]");
    assert(cable_lead >= 2 - 1e-6, "Straight lead behind the crimp under 2 mm");
    assert(clip_off >= 3 - 1e-6 && y_clip0 <= lpk_y0 - 0.5, "First clip within 3 mm of the flex edge or inside the pocket");
    assert(pow(clip_off, 2) / (4 * norm([x_ex_tol, z_cab_on - z_ll])) >= cable_bend_r - 1e-6,
        str("Free cable between the flex and the first clip bends tighter than ", cable_bend_r,
            " to take up the exit tolerance; raise clip_off"));
    assert(y_clip0 - rail_lo >= 3 - 1e-6,
        str("Clip rails only ", r2(y_clip0 - rail_lo), " mm long: cable too short for the hairpin (raise clip_off?)"));
    assert(y_j0 - y_u_hi >= lk_len + 1 - 1e-6,
        str("Board leg straight only ", r2(y_j0 - y_u_hi), " mm at the shortest cable"));
    assert(lkeepers[0][1] >= y_u_hi + 0.3 && lkeepers[0][3] <= y_j0 - 0.3, "Board-leg keeper is off the straight");
    for (k = lkeepers) {
        assert(k[4] < z_seam - 0.5, "Cable keeper shorter than 0.5 mm");
        assert(k[2] <= cav_x - 0.1, "Cable keeper runs into the right wall");
        assert(!use_patch || k[0] >= win_x1 + 1, "Cable keeper runs into the patch window");
        assert(k[2] <= lip_in - 0.3 || (notch_need && k[1] >= notch_y[0] && k[3] <= notch_y[1]),
            "Cable keeper runs into the lid lip");
    }
    assert(abs(lcab_chk - cable_free) <= 0.15, str("Cable path ", r2(lcab_chk), " != free length ", cable_free));
    assert(y_u_lo - hp_r - cable_d / 2 >= pcb_y0 + strip_y[0] + 0.3
           && fl_route[0][0] >= pcb_x0 + strip_x0 && y_crimp <= pcb_y0 + strip_y[1],
        str("Cable hairpin / board leg leave the part-free strip (board x >= ", strip_x0, ", y ", strip_y, ")"));
    assert(!notch_need || (notch_y[0] >= side_run(1)[0] && notch_y[1] <= side_run(1)[1]),
        "Right-wall lip notch runs onto a corner radius");
    assert(!notch_need || notch_y[1] <= y_j0 + jog_run && notch_y[0] <= y_u_lo - hp_r,
        "Right-wall lip notch does not cover the board leg / hairpin");
    for (i = [0 : len(holes) - 1])
        assert(rect_dist(holes[i], fl_route[0], fl_route[1]) >= screw_head_d / 2 + 0.3,
            str("TX cable runs over the screw head at board hole ", holes_pcb[i]));
    assert(!vent_slots || !rects_hit(vent_a, vent_b, [lpk_x0, lpk_y0], [lpk_x1, lpk_y1], 1),
        "Vent slots cut into the lid flex pocket; move vent_c (the default [22, 65] lies under the flex)");
    assert(!vent_slots || !rects_hit(vent_a, vent_b, fl_route[0], [x_bl, ufl_xy[1] + ufl_plug_w / 2], vent_keep),
        str("Vent slots within ", vent_keep, " mm of the U.FL / TX cable; move vent_c"));
}

// ---- rounded shell checks (round revision) ----
pf_dz_min = min([for (i = [1 : len(pf_raw) - 1]) pf_raw[i][1] - pf_raw[i - 1][1]]);
pf_bot45  = pf_Cb + bot_r * [cos(-bot_ang), sin(-bot_ang)];   // end of the bottom chamfer
pf_top60  = pf_Ct + top_r * [cos(top_ang), sin(top_ang)];     // start of the lid-face chamfer
assert(pf_ok_b && pf_ok_t && pf_dz_min >= -1e-6 && pf_bot45[1] >= -1e-6 && pf_top60[1] <= z_top + 1e-6,
    str("Rounded profile has no tangent solution (bottom ", pf_ok_b, ", top ", pf_ok_t,
        "); change bulge / bulge_z / side_r / bot_* / top_*"));
assert(corner_r > 0 || len(pf_R_auto) > 0,
    str("No outside corner radius from ", r2(cav_r + wall_t), " up keeps wall_min (", wall_min, ") at the cavity corners and the flex-pocket rim / skin. Lower wall_min or bot/top insets; or pcb_r ",
        pcb_r, " is too large for the lid flex pocket at the top corners (the outside radius saturates at ~9.7; pcb_r <= ~7.6)"));
assert(bulge_z > z_floor && bulge_z < z_seam, "bulge_z must lie between the floor and the seam");
assert(bot_ang <= 45 + 1e-6 && pf_ovh_base <= 45 + 0.05,
    str("Base overhang ", r2(pf_ovh_base), " deg (prints phone face down; max 45). Keep bot_ang <= 45"));
assert(layer_h * tan(top_ang) <= line_w / 2 + 0.005 && pf_ovh_lid <= top_ang + 0.05,
    str("Lid edge overhang ", r2(pf_ovh_lid), " deg: ", r2(layer_h * tan(top_ang)), " mm per layer is over half the ",
        line_w, " line (prints face down); lower top_ang"));
assert(pf_omax <= grow_max + 1e-6, str("Bulge grows the footprint ", r2(pf_omax), " mm per side (max grow_max ", grow_max, ")"));
assert(out_r - max(bot_inset, top_inset) >= 1.0, "Plan corner radius goes below 1 mm at the phone / lid face");
assert(out_r >= cav_r + wall_t - 1e-6, "corner_r below the concentric radius cav_r + wall_t");
assert(wall_at(wall_t, z_floor, z_wall) >= wall_min - 1e-6,
    str("Side wall only ", r2(wall_at(wall_t, z_floor, z_wall)), " mm after rounding (min wall_min ", wall_min, ")"));
assert(wall_at(wc(out_r), z_floor, z_wall) >= wall_min - 1e-6,
    str("Corner wall only ", r2(wall_at(wc(out_r), z_floor, z_wall)), " mm with corner_r ", out_r,
        " (min wall_min ", wall_min, "); reduce corner_r or set 0 (auto)"));
for (s = snaps) if (s[0] < 4) for (e = [-1, 1])
    let(p = loc2glob(s[0], s[1], [e * (snap_len / 2 + snap_clr + 0.5), snap_gd]))
        assert(prof_sd(out_in(p), snap_z) >= wall_min - 1e-6,
            str("Snap groove ", s, " leaves ", r2(prof_sd(out_in(p), snap_z)), " mm of rounded wall (min ", wall_min, ")"));
mag_u = min(concat([for (a = [0 : 5 : 355]) out_in(ring_ro * [cos(a), sin(a)])],
                   use_clock ? [for (x = [clk_x0, clk_x1], y = [clk_y0, clk_y1]) out_in([x, y])] : []));
assert(mag_u >= bot_inset + face_margin - 1e-6,
    str("Flat phone face ends ", r2(mag_u - bot_inset), " mm past the magnet pockets (min face_margin ", face_margin, "); reduce bot_inset"));
assert(wall_at(mag_u, skin_t, z_pause) >= mag_side_min - 1e-6,
    str("Only ", r2(wall_at(mag_u, skin_t, z_pause)), " mm of plastic beside a magnet pocket (min mag_side_min ",
        mag_side_min, "); reduce bot_inset or raise bot_r"));
for (h = holes) {
    assert(wall_at(out_in(h) - hole_d / 2, z_hole_bot, z_pcb_bot) >= wall_min - 1e-6,
        str("Insert / pilot hole at ", h, " comes within ", r2(wall_at(out_in(h) - hole_d / 2, z_hole_bot, z_pcb_bot)),
            " mm of the rounded outside"));
    assert(wall_at(out_in(h) - standoff_d / 2, z_floor, z_pcb_bot) >= 0, str("Standoff at ", h, " pokes out of the rounded shell"));
}
assert(top_inset <= min(wall_t, wc(out_r)) + lip_clr - 1e-6,
    "Lid-face round reaches over the lid lip: the plate must keep full lid_t over the lip; reduce top_inset");
assert(pf_seam_ang <= 45 + 1e-6,
    str("Shell leans in ", r2(pf_seam_ang), " deg at the seam: the lid edge becomes a knife edge (max 45); raise bulge_z or top_r"));
assert(pf_tht >= 0 && pf_thb <= 0, "Top round starts below the widest section, or the bottom round above it");
pf_top_z0 = pf_Ct[1] + top_r * sin(pf_tht);          // top round: lower tangent point
assert(z_top - pf_top_z0 <= lid_t + (z_seam - bulge_z) / 2,
    str("Top round ", r2(z_top - pf_top_z0), " tall: more than lid_t + half the side above the bulge; reduce top_r"));
// board corner radius (pcb_r)
for (i = [0 : len(holes_pcb) - 1])
    assert(bd_in(holes_pcb[i]) >= pcb_keep_d / 2 + pcb_keep_m - 1e-6,
        str("Board corner r ", pcb_r, " comes within ", r2(bd_in(holes_pcb[i]) - pcb_keep_d / 2), " mm of the ", pcb_keep_d,
            " mm keep circle at hole ", holes_pcb[i], " (min pcb_keep_m ", pcb_keep_m, "): max pcb_r ",
            r2(pcb_r_max(pcb_keep_d / 2 + pcb_keep_m)), " for this keep circle"));
assert(!board_notch || (tx_pos - tx_nw >= pcb_r + 0.5 && tx_pos + tx_nw <= ((tx_s % 2 == 1) ? pcb_L : pcb_W) - pcb_r - 0.5),
    "Board notch at the old TX jack runs onto a board corner radius");
assert(!use_fxp || min([for (dx = [-1.5, 1.5], dy = [-1.3, 1.3]) bd_in(ufl_pos + [dx, dy])]) >= 0.5,
    "J3 U.FL runs onto a board corner radius");

echo(str("=== BEACON MagSafe enclosure, ", ring_t, " mm ring, LOW PROFILE, FXP70 TX ",
         fxp_lid ? "IN THE LID ===" : fxp_bay ? "IN A SIDE BAY ===" : "==="));
echo(str("ROUND shell: plan corner r ", r2(out_r), corner_r > 0 ? " (set)" : " (auto, max for wall_min)",
         " at the nominal outline, ", r2(out_r + pf_omax), " at the widest; fxp70_inlid 5.1 (0.4 chamfers). Phone face flat ",
         r2(2 * (out_x - bot_inset)), " x ", r2(out_y1 - out_y0 - 2 * bot_inset), " r ", r2(out_r - bot_inset),
         "; lid face flat ", r2(2 * (out_x - top_inset)), " x ", r2(out_y1 - out_y0 - 2 * top_inset), " r ", r2(out_r - top_inset)));
echo(str("ROUND profile (offset o from the nominal outline vs Z): face o ", -bot_inset, ", ", bot_ang, " deg chamfer to Z ",
         r2(pf_bot45[1]), ", R ", bot_r, " round to Z ", r2(pf_Cb[1] + bot_r * sin(pf_thb)), ", convex side R ", side_r,
         " widest o +", r2(pf_omax), " at Z ", r2(bulge_z), ", R ", top_r, " round from Z ", r2(pf_top_z0), " to Z ", r2(pf_top60[1]),
         ", ", top_ang, " deg chamfer to the lid face o ", -top_inset, ". At the seam (Z ", r2(z_seam), ") o ", r2(o_at(z_seam)),
         ", leaning in ", r2(pf_seam_ang), " deg; ", len(prof), " profile rows"));
echo(str("ROUND walls (min plastic to the outside): side ", r2(wall_at(wall_t, z_floor, z_wall)), ", cavity corners ",
         r2(wall_at(wc(out_r), z_floor, z_wall)), " (nominal ", r2(wc(out_r)), "), snap grooves ",
         r2(min([for (s = snaps) if (s[0] < 4) for (e = [-1, 1]) prof_sd(out_in(loc2glob(s[0], s[1], [e * (snap_len / 2 + snap_clr + 0.5), snap_gd])), snap_z)])),
         ", inserts ", r2(min([for (h = holes) wall_at(out_in(h) - hole_d / 2, z_hole_bot, z_pcb_bot)])),
         ", magnet pockets ", r2(wall_at(mag_u, skin_t, z_pause)), " (flat face ", r2(mag_u - bot_inset), " past them); min wall_min ", wall_min));
if (fxp_lid)
    echo(str("ROUND lid: flex pocket rim ", r2(min([for (p = lpk_ring) prof_sd(out_in(p), z_seam)])), " (min ", pk_rim_min,
             "), skin at the pocket edge ", r2(min([for (p = lpk_ring) prof_sd(out_in(p), z_lpk)])), " (min ", lid_skin_min,
             "); full ", lid_t, " plate over the lip (lid face inset ", top_inset, " <= ", r2(min(wall_t, wc(out_r)) + lip_clr), ")"));
echo(str("ROUND print: base max overhang ", r2(pf_ovh_base), " deg (phone face down), lid max overhang ", r2(pf_ovh_lid),
         " deg = ", r2(layer_h * tan(pf_ovh_lid)), " mm per ", layer_h, " layer (outer face down); no supports"));
echo(str("ROUND board corner: pcb_r ", pcb_r, ", hole to board edge ", r2(min([for (h = holes_pcb) bd_in(h)])),
         " (keep ", pcb_keep_d, " + ", pcb_keep_m, "). Max pcb_r with the holes at ", hole_inset, ": standoff 6.0 ",
         r2(pcb_r_max(3.0 + pcb_keep_m)), ", KiCad courtyard 4.9 ", r2(pcb_r_max(2.45 + pcb_keep_m)), ", KiCad Cmts 4.4 ",
         r2(pcb_r_max(2.2 + pcb_keep_m)), ", screw head ", screw_head_d, " ", r2(pcb_r_max(screw_head_d / 2 + pcb_keep_m)),
         ", hole ", pcb_hole_d, " ", r2(pcb_r_max(pcb_hole_d / 2 + pcb_keep_m)), " mm"));
echo(str("Skin over magnets: ", r2(skin_t), " mm (", skin_layers, " layers); pocket depth ",
         r2(z_pause - skin_t), " mm, ", r2(z_pause - skin_t - mag_t), " mm headroom; cap ",
         cap_layers, " layers to ", r2(z_floor), " mm"));
echo(str("PAUSE: after layer ", pause_layer, " (top at Z = ", r2(z_pause),
         " mm), i.e. before the layer that ends at Z = ", r2(z_pause + layer_h),
         " mm. Insert magnets, then resume."));
echo(str("Outside: ", r2(out_x + out_x1 + 2 * pf_omax), " x ", r2(out_l), " x ", r2(z_top),
         " mm at the widest section (Z ", r2(bulge_z), "; nominal outline ", r2(out_x + out_x1), " x ", r2(out_y1 - out_y0),
         "); ring centre ", r2(out_y1 + pf_omax), " mm below the top edge, ", r2(out_x + pf_omax), " mm from the left edge",
         fxp_bay ? str("; main body ", r2(2 * out_x), " wide + antenna bay ", r2(out_x1 - out_x), " x ",
                       r2(bay_oy1 - out_y0), " on the right (Y ", r2(out_y0), " to ", r2(bay_oy1), ")") : ""));
echo(str("PCB: ", r2(pcb_W), " x ", r2(pcb_L), " x ", pcb_t, " mm, corner r ", pcb_r,
         ", underside ", r2(z_pcb_bot), " mm above the phone"));
echo(str("Ring centre in board coords: ", [r2(-pcb_x0), r2(-pcb_y0)]));
echo(str("Mounting holes in board coords: ", [for (h = holes_pcb) [r2(h[0]), r2(h[1])]],
         "; keep 6 mm pads clear on both sides"));
echo(str("Z stack: floor ", r2(z_floor), ", board ", r2(z_pcb_bot), " / ", r2(z_pcb_top),
         ", lid underside ", r2(z_seam), ", top ", r2(z_top), " mm (rev_pcb 4.16, 5.72 / 7.32, 12.72, 14.32)"));
echo(str("Part height: under board ", r2(z_pcb_bot - z_floor), " mm, over board ", r2(top_clear),
         " mm (", r2(z_seam - lip_h - z_pcb_top), " mm within ", r2(lip_band),
         " mm of the board edge, under the lid lip)"));
echo(str("Floor pockets: feed pin ", pin_pocket && use_patch ? str("d ", pin_pocket_d, " at board ",
             [r2(pin_xy[0] - pcb_x0), r2(pin_xy[1] - pcb_y0)], " to Z ", r2(z_pin_floor), " (",
             r2(z_pcb_bot - z_pin_floor), " below the board)") : "off",
         use_sma ? str("; SMA flange + legs to Z ", r2(z_sma_floor), " (", r2(z_pcb_bot - z_sma_floor),
                       " below the board)") : "; no SMA pockets",
         "; USB-C stakes to Z ", r2(z_usb_floor), " (", r2(z_pcb_bot - z_usb_floor), " below)"));
for (k = [0, 1]) if (use_sma && !leg_ok[k]) {
    lg = grect(tx_s, tx_along, leg_loc(2 * k - 1, sma_leg_l, 0));
    echo(str(leg_cut[k] ? "ASSEMBLY: CUT " : "NOTE: uncut ", "SMA lower leg at board x ",
             r2(lg[0][0] - pcb_x0), "-", r2(lg[1][0] - pcb_x0), ", y ", r2(lg[0][1] - pcb_y0), "-", r2(lg[1][1] - pcb_y0),
             leg_cut[k] ? str(" (over the ring magnet) to a ", sma_leg_stub, " mm stub behind the flange BEFORE soldering J3")
                        : str(" rides ", r2(z_pcb_bot - sma_leg_below - z_floor), " mm over the ring cap")));
}
echo(str("Lid: plate ", lid_t, " mm, outer face flat at Z ", r2(z_top), "; ",
         usb_open_top ? str("USB-C opening open through the lid, overmold top ",
                            r2(usb_zc + 3.25 - z_top), " mm from the lid face")
                      : "USB-C opening bridged by the lid",
         use_sma ? str("; SMA flange recess ", r2(sma_recess), " mm (", r2(lid_t - sma_recess), " mm lid left)")
                 : "; no SMA recess or tongue"));
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
             patch_window ? str("open window ", r2(radome_w), " sq, patch top ",
                                r2(z_top - z_pcb_top - patch_stack), " (worst ",
                                r2(z_top - z_pcb_top - patch_top_max), ") mm below the lid face")
                          : str(r2(z_seam + lid_t - patch_cover - z_pcb_top - patch_stack),
                                " mm air (worst ", r2(z_top - patch_cover - z_pcb_top - patch_top_max),
                                ") under a ", patch_cover, " mm radome")));
if (use_sma)
    echo(str("TX jack: ", tx_side, " board edge at ", tx_pos, " mm; board notch ", r2(tx_notch),
             " x ", r2(2 * tx_nw), " mm; axis ", r2(sma_z), " mm above the phone face, ",
             r2(sma_barrel - wall_t), " mm of barrel outside the wall; slot ", r2(sma_hole),
             " mm (", r2((sma_hole - sma_thread) / 2), " mm radial on the thread)"));
if (use_fxp) {
    echo(str("TX U.FL J3: board ", ufl_pos, " = ", [r2(ufl_xy[0]), r2(ufl_xy[1])], " from the ring centre; mated top Z ",
             r2(z_pcb_top + ufl_mated_h), " (", r2(z_seam - z_pcb_top - ufl_mated_h), " under the lid); plug cable toward -Y"));
}
if (fxp_bay) {
    echo(str("TX cable: ", cable_len, " +/-", cable_tol, " mm, ", r2(cable_free), " free; lead ", cable_lead,
             ", run along -Y at x ", r2(x_run), " (board x ", r2(x_run - pcb_x0), ") from y ", r2(y_crimp),
             ", bend R ", cable_bend_r, " (", r2(cable_bend_r / cable_d), " x OD) to +X at y ", r2(y_c),
             " (board y ", r2(y_c - pcb_y0), "; ", r2(y_c_lo), " to ", r2(y_c_hi), " over the slide), wall slot y ",
             r2(slot_y0), " to ", r2(slot_y1), ", trough to the flex edge; path check ", r2(cab_len_chk)));
    echo(str("TX cable clearances: RX patch ", r2(cab_rx_d), " mm, lid lip ", r2(lip_in - x_run - cable_d / 2),
             " mm; keepers at y ", keeper_y, " + trough, ", keeper_clr, " over the cable"));
    echo(str("TX flex FXP70: pocket X ", r2(pk_x0), " to ", r2(pk_x1), ", Y ", r2(pk_y0), " to ", r2(pk_y1),
             " (", r2(pk_x1 - pk_x0), " x ", r2(pk_y1 - pk_y0), ", ", r2(pk_d), " deep), floor Z ", r2(z_pk),
             ", shelf top Z ", r2(z_shelf), " (", shelf_t, " PETG on ribs), flex top Z ", r2(z_flex_nom),
             " nominal / ", r2(z_flex_max), " max, solder joints ", r2(z_seam - z_flex_max - fxp_solder_h),
             " under the lid, lid ", lid_t, " over ", r2(z_seam - z_flex_nom), " air"));
    echo(str("TX flex clearances: board ground edge ", r2(pk_x0 - pcb_xr), " in plane (", r2(z_flex_nom - z_pcb_top),
             " higher), ring magnet ", r2(pk_x0 - ring_od / 2), ", RX patch ", r2(fxp_rx_d), " edge to edge, ",
             r2(norm(fxp_c - patch_xy)), " centre to centre; phone face ", r2(z_pk), " below the flex"));
    for (w = phone_w)
        echo(str("TX flex vs a ", w, " mm phone (ring centred): flex inner edge ",
                 r2(pk_x0 - w / 2), pk_x0 >= w / 2 ? " mm past the phone edge" : " mm (over the phone)",
                 "; enclosure ", r2(out_x1 - w / 2), " mm past the edge"));
    echo(str("TX bay: inside X ", r2(bay_cx0), " to ", r2(bay_cx1), ", Y ", r2(bay_cy0), " to ", r2(bay_cy1),
             ", floor Z ", r2(z_bay_floor), "; snap beads right wall ", snap_right_y,
             snap_bay ? str(", bay top wall x ", r2(bay_snap_x)) : ""));
}
if (fxp_lid) {
    echo(str("TX flex FXP70 IN THE LID: pocket X ", r2(lpk_x0), " to ", r2(lpk_x1), ", Y ", r2(lpk_y0), " to ", r2(lpk_y1),
             " (", r2(lpk_x1 - lpk_x0), " x ", r2(lpk_y1 - lpk_y0), ", ", r2(lpk_d), " deep into the lid underside), ceiling Z ",
             r2(z_lpk), ", ", lid_skin, " PETG over the flex; flex (pushed +X/+Y) X ", r2(lpk_x1 - fl_x), " to ", r2(lpk_x1),
             ", Y ", r2(fl_y0), " to ", r2(lpk_y1), " (board x ", r2(lpk_x1 - fl_x - pcb_x0), "-", r2(lpk_x1 - pcb_x0),
             ", y ", r2(fl_y0 - pcb_y0), "-", r2(lpk_y1 - pcb_y0), "), centre ", [r2(fl_c[0]), r2(fl_c[1])],
             ", cable-side face Z ", r2(z_fl_lo_max), "-", r2(z_fl_lo_nom)));
    echo(str("TX flex clearances: board-top GND pour ", r2(l_gnd), " below the flex copper (L2 GND ", r2(l_gnd2),
             "; Taoglas: >= ", ant_gnd_min, ", 20 best); parts under it <= ", top_band_h, " (", r2(l_gnd - top_band_h),
             " to their tops); solder joints ", r2(z_fl_lo_max - fxp_solder_h - z_pcb_top - top_band_h),
             " over them; mated U.FL ", r2(l_ufl_xy), " in plane / ", r2(l_ufl_z), " below the flex (", r2(l_ufl), " 3D)"));
    echo(str("TX flex vs RX patch: window edge ", r2(l_win), " (nominal ", r2(fl_y0 - win_y1), "), patch footprint ",
             r2(l_rx), " worst / ", r2(l_rx_nom), " nominal edge to edge, ", r2(norm(fl_c - patch_xy)),
             " centre to centre; flex copper ", r2(z_fl_mid - (z_pcb_top + patch_tape + patch_h)), " vs the patch top"));
    echo(str("TX flex over the ring magnet: ", r2(z_fl_mid - skin_t - ring_t), " above its top; phone face ",
             r2(z_fl_mid), " below the flex"));
    echo(str("TX flex image-theory estimate (", fxp_freq, " GHz, horizontal current ", r2(l_gnd), " over GND): radiated power x ",
             r2(img_ratio(l_gnd)), " (", r2(10 * log(img_ratio(l_gnd))), " dB) vs free space; +1 mm local rise: x ",
             r2(img_ratio(l_gnd + 1)), " (", r2(10 * log(img_ratio(l_gnd + 1) / img_ratio(l_gnd))), " dB better); +2 mm: ",
             r2(10 * log(img_ratio(l_gnd + 2) / img_ratio(l_gnd))), " dB better"));
    echo(str("TX cable: ", cable_len, " +/-", cable_tol, " mm, ", r2(cable_free), " free; on the flex at x ", r2(x_ll),
             " (board x ", r2(x_ll - pcb_x0), ", +/-", x_ex_tol, "), exit y ", r2(fl_y0), ", groove to the clips at y ",
             r2(y_clip0), ", lid leg Z ", r2(z_ll), " in clip rails to y ", r2(rail_lo),
             "; hairpin R ", hp_r, " (", r2(hp_r / cable_d), " x OD) tilted ", r2(atan2(hp_dz, hp_s)), " deg, legs ",
             r2(hp_s), " apart in X / ", r2(hp_dz), " in Z, at y ", r2(y_u), " (", r2(y_u_lo), " to ", r2(y_u_hi),
             " over the tolerances), lowest y ", r2(y_u_lo - hp_r)));
    echo(str("TX cable (cont.): board leg x ", r2(x_bl), " (board x ", r2(x_bl - pcb_x0), ") Z ", r2(z_bl), " from the hairpin to y ",
             r2(y_j0), ", S-jog ", r2(jog_h), " over ", r2(jog_run), " (2 x ", r2(jog_th), " deg, R ", hp_r,
             ") to the plug axis x ", r2(x_run), ", lead ", cable_lead, " to the crimp at y ", r2(y_crimp),
             "; path check ", r2(lcab_chk)));
    echo(str("TX cable clearances: lid leg to RX patch ", r2(l_cab_rx), " mm (worst), rails to window ",
             r2(x_ll - x_ex_tol - rail_hw - rail_t - win_x1), ", board leg to wall ",
             r2(cav_x - x_bl - cable_d / 2), "; keepers ", [for (k = lkeepers) [r2(k[0]), r2(k[1]), r2(k[2]), r2(k[3])]],
             ", ", keeper_clr, " over the cable; lid can lift ~",
             r2(sqrt(pow((rail_lo - y_u_hi) + (lkeepers[0][1] - y_u_hi) + PI * hp_r, 2)
                     - pow(rail_lo - lkeepers[0][1], 2) - pow(hp_s, 2)) - hp_dz),
             " mm (shortest cable) with J3 still mated"));
    echo(str("Lid lip: cut over the flex pocket on the top wall x ", r2(top_cut[0]), " to ", r2(top_cut[1]),
             notch_need ? str("; notched on the right wall y ", r2(notch_y[0]), " to ", r2(notch_y[1]), " (hairpin / board leg)") : "",
             "; beads right ", snap_right_y, ", left ", snap_side_y, ", top ", snap_top_x));
}
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
// rounded shell: plan outline at offset o, corner_n segments per corner, CCW
function rr_pts(o) = let(r = out_r + o, x0 = -out_x - o, x1 = out_x + o, y0 = out_y0 - o, y1 = out_y1 + o,
                         cs = [[x1 - r, y0 + r, -90], [x1 - r, y1 - r, 0], [x0 + r, y1 - r, 90], [x0 + r, y0 + r, 180]])
    [for (c = cs, j = [0 : corner_n]) [c[0] + r * cos(c[2] + 90 * j / corner_n), c[1] + r * sin(c[2] + 90 * j / corner_n)]];
// the shell solid between z0 and z1: one polyhedron lofted through the profile rows
module prof_solid(z0, z1) {
    rows = concat([[o_at(z0), z0]], [for (p = prof) if (p[1] > z0 + 1e-3 && p[1] < z1 - 1e-3) p], [[o_at(z1), z1]]);
    m    = 4 * (corner_n + 1);
    nr   = len(rows);
    pts  = [for (rw = rows) for (q = rr_pts(rw[0])) [q[0], q[1], rw[1]]];
    sides = [for (i = [0 : nr - 2], j = [0 : m - 1])
                 let(a = i * m + j, b = i * m + (j + 1) % m, c = (i + 1) * m + (j + 1) % m, d = (i + 1) * m + j)
                 each [[a, c, b], [a, d, c]]];
    polyhedron(points = pts, faces = concat([[for (j = [0 : m - 1]) j]],
                                            [[for (j = [m - 1 : -1 : 0]) (nr - 1) * m + j]], sides), convexity = 2);
}
module cavity2d(inset = 0) rrect(-cav_x + inset, cav_y0 + inset, cav_x - inset, cav_y1 - inset, cav_r - inset);
// antenna bay: its outer shape starts inside the main body, so the union is
// an L with a straight bottom edge; inner corners bay_r
module bay_outer2d(inset = 0) rrect(inset, out_y0 + inset, bay_ox1 - inset, bay_oy1 - inset, bay_r + wall_t - inset);
module bay2d() rrect(bay_cx0, bay_cy0, bay_cx1, bay_cy1, bay_r);
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
    if (board_notch) {                                 // notch at the old TX jack (still routed)
        if (tx_s == 0) translate([tx_pos - tx_nw, pcb_L - tx_notch]) square([2 * tx_nw, tx_notch + 1]);
        if (tx_s == 1) translate([pcb_W - tx_notch, tx_pos - tx_nw]) square([tx_notch + 1, 2 * tx_nw]);
        if (tx_s == 2) translate([tx_pos - tx_nw, -1]) square([2 * tx_nw, tx_notch + 1]);
        if (tx_s == 3) translate([-1, tx_pos - tx_nw]) square([tx_notch + 1, 2 * tx_nw]);
    }
}
// 3D polyline of spheres (cable preview)
module polyline3(p, d) for (i = [1 : len(p) - 1]) hull() {
    translate(p[i - 1]) sphere(d = d, $fn = 12);
    translate(p[i]) sphere(d = d, $fn = 12);
}

// ---------------------------------------------------------------------
// Base (phone side), modelled as printed
// ---------------------------------------------------------------------
module bay_shelf() {                               // shelf plate on ribs along X
    span = shelf_y1 - bay_cy0 - shelf_rib_w;
    n    = max(1, ceil(span / shelf_rib_pitch - 1e-6));
    translate([bay_cx0 - eps, bay_cy0 - eps, z_shelf - shelf_t])
        cube([bay_cx1 - bay_cx0 + 2 * eps, shelf_y1 - bay_cy0 + eps, shelf_t]);
    for (i = [0 : n]) translate([bay_cx0 - eps, bay_cy0 + i * span / n, z_bay_floor - eps])
        cube([bay_cx1 - bay_cx0 + 2 * eps, shelf_rib_w, z_shelf - shelf_t - z_bay_floor + 2 * eps]);
}
module base() {
    difference() {
        union() {
            difference() {
                union() {
                    prof_solid(0, z_wall);                 // rounded shell (round revision)
                    if (fxp_bay) hull() {                  // antenna bay
                        linear_extrude(eps) bay_outer2d(edge_chamfer);
                        translate([0, 0, edge_chamfer]) linear_extrude(z_wall - edge_chamfer) bay_outer2d();
                    }
                }
                translate([0, 0, z_floor]) linear_extrude(z_wall) cavity2d();
                if (fxp_bay) translate([0, 0, z_bay_floor]) linear_extrude(z_wall) bay2d();
            }
            for (h = holes)                                // PCB standoffs
                translate([h[0], h[1], z_floor - eps])
                    cylinder(d = standoff_d, h = z_pcb_bot - z_floor + eps);
            if (fxp_bay) bay_shelf();
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
            linear_extrude(wall_t + 1.5 + max(0, pf_omax)) u_slot(usb_open_w, usb_z0, z_top + 1, usb_open_r);
        // snap grooves in the inner wall faces (45 degree flanks, print upright)
        for (s = snaps) at_side(s[0], s[1])
            rotate([90, 0, 90]) linear_extrude(snap_len + 2 * snap_clr + 1, center = true)
                polygon([[-1, snap_z - snap_gd - 1], [snap_gd, snap_z], [-1, snap_z + snap_gd + 1]]);
        // lever notch in the outer half of the bottom wall, at the seam
        if (pry_notch) at_side(2, pry_x)
            translate([-pry_w / 2, wall_t / 2, z_wall - 1.2]) cube([pry_w, wall_t + max(0, pf_omax) + 1, 2]);
        // legacy TX jack: barrel hole + U-slot up through the wall top (lid tongue closes it)
        if (use_sma) at_side(tx_s, tx_along) {
            through_wall(sma_hole, sma_z);
            translate([-sma_hole / 2, -1, sma_z]) cube([sma_hole, wall_t + 2, z_top]);
        }
        // floor pockets for the bottom-side parts that hang below pcb_gap
        if (use_patch && pin_pocket)                       // patch feed pin (ring island)
            translate([pin_xy[0], pin_xy[1], z_pin_floor])
                cylinder(d = pin_pocket_d, h = z_floor - z_pin_floor + 1);
        if (use_sma && sma_pocket) at_side(tx_s, tx_along) // SMA flange + pocketable lower legs
            translate([0, 0, z_sma_floor]) linear_extrude(z_floor - z_sma_floor + 1) {
                translate(flange_loc[0]) square(flange_loc[1] - flange_loc[0]);
                for (k = [0, 1]) if (leg_pkt[k])
                    let(r = leg_loc(2 * k - 1, leg_len[k], sma_pocket_clr))
                        translate(r[0]) square(r[1] - r[0]);
            }
        if (usb_stake_pocket) for (p = stake_xy)           // USB-C shell stakes
            translate([p[0] - usb_stake_pkt[0] / 2, p[1] - usb_stake_pkt[1] / 2, z_usb_floor])
                cube([usb_stake_pkt[0], usb_stake_pkt[1], z_floor - z_usb_floor + 1]);
        if (label) translate([0, 0, z_pause - 0.4]) linear_extrude(0.4 + eps) {   // read at the pause
            translate([0,  2.8]) text("MAGNETS DOWN", size = 3.5, halign = "center", valign = "center");
            translate([0, -2.8]) text("STEEL UP",     size = 3.5, halign = "center", valign = "center");
        }
        if (fxp_bay) {
            // flex pocket (flex + adhesive), long in Y by fxp_slide each way
            translate([pk_x0, pk_y0, z_pk]) cube([pk_x1 - pk_x0, pk_y1 - pk_y0, z_top]);
            // cable slot through the right wall, open at the top, floor at the board top
            translate([cav_x - 1, slot_y0, z_pcb_top]) cube([wall_t + 2, slot_y1 - slot_y0, z_top]);
            // cable trough in the shelf, floor following the cable up to the pocket
            hull() {
                translate([bay_cx0 - 1, slot_y0, z_cab_bot(bay_cx0) - 0.15]) cube([1, slot_y1 - slot_y0, z_top]);
                translate([pk_x0, slot_y0, z_pk]) cube([eps, slot_y1 - slot_y0, z_top]);
            }
        }
    }
}

// ---------------------------------------------------------------------
// Lid (back cover), modelled in assembled position
// ---------------------------------------------------------------------
// clip rails under the lid along the lid leg: two rails either side of the
// cable, with a 45 degree ridge at each tip below the cable (snap it in)
module lid_rails() {
    xf = rail_hw;
    translate([x_ll, y_clip0, 0]) rotate([90, 0, 0]) linear_extrude(y_clip0 - rail_lo)
        for (m = [0, 1]) mirror([m, 0]) polygon([
            [xf, z_seam + eps], [xf + rail_t, z_seam + eps], [xf + rail_t, z_rail_bot],
            [xf, z_rail_bot], [xf - clip_p, z_rail_bot + 0.2], [xf, z_cab_bot_ll]]);
}
module lid() {
    difference() {
        union() {
            prof_solid(z_seam, z_top);                     // plate, rounded outer edge
            if (fxp_bay) hull() {                          // plate over the antenna bay
                translate([0, 0, z_seam]) linear_extrude(lid_t - edge_chamfer) bay_outer2d();
                translate([0, 0, z_top - eps]) linear_extrude(eps) bay_outer2d(edge_chamfer);
            }
            difference() {                                 // locating lip, notched at USB-C and TX
                translate([0, 0, z_seam - lip_h]) linear_extrude(lip_h + eps)
                    difference() { cavity2d(lip_clr); cavity2d(lip_clr + lip_t); }
                translate([usb_x - usb_open_w / 2 - 0.3, cav_y0 - 1, z_seam - lip_h - 1])
                    cube([usb_open_w + 0.6, lip_clr + lip_t + 1.5, lip_h + 2]);
                if (use_sma) at_side(tx_s, tx_along)
                    translate([-(tx_jw + 0.5), -(lip_clr + lip_t + 0.5), z_seam - lip_h - 1])
                        cube([2 * (tx_jw + 0.5), lip_clr + lip_t + 1.5, lip_h + 2]);
                if (fxp_bay)                               // TX cable crossing
                    translate([lip_in - 0.5, slot_y0 - 0.3, z_seam - lip_h - 1])
                        cube([cav_x - lip_in + 1.5, slot_y1 - slot_y0 + 0.6, lip_h + 2]);
                if (fxp_lid) {                             // lid-mode: top wall over the flex pocket
                    translate([top_cut[0], cav_y1 - lip_clr - lip_t - 0.5, z_seam - lip_h - 1])
                        cube([top_cut[1] - top_cut[0], lip_clr + lip_t + 1.5, lip_h + 2]);
                    if (notch_need)                        // right wall over the hairpin / board leg
                        translate([lip_in - 0.5, notch_y[0], z_seam - lip_h - 1])
                            cube([cav_x - lip_in + 1.5, notch_y[1] - notch_y[0], lip_h + 2]);
                }
            }
            if (fxp_bay && snap_bay) at_side(4, bay_snap_x)    // short lip on the bay top wall
                translate([-(snap_len / 2 + 2), -(lip_clr + lip_t), z_seam - lip_h])
                    cube([snap_len + 4, lip_t, lip_h + eps]);
            for (s = snaps) at_side(s[0], s[1])            // snap beads on the lip face
                rotate([90, 0, 90]) linear_extrude(snap_len, center = true)
                    polygon([[-lip_clr - 0.3, snap_z - snap_p - 0.3], [-lip_clr + snap_p, snap_z],
                             [-lip_clr - 0.3, snap_z + snap_p + 0.3]]);
            if (use_sma) at_side(tx_s, tx_along)           // tongue closing the TX slot
                difference() {
                    translate([-(sma_hole / 2 - tongue_clr), 0, sma_z])
                        cube([sma_hole - 2 * tongue_clr, wall_t, z_seam - sma_z + eps]);
                    through_wall(sma_hole, sma_z);
                }
            if (fxp_bay) {
                for (k = keepers)                          // cable keepers
                    translate([k[0], k[1], k[4]]) cube([k[2] - k[0], k[3] - k[1], z_seam - k[4] + eps]);
                if (fxp_holddown) for (p = hd_pts)         // flex hold-down pins
                    translate([p[0], p[1], z_shelf + holddown_gap])
                        cylinder(d = holddown_d, h = z_seam - z_shelf - holddown_gap + eps);
            }
            if (fxp_lid) {
                lid_rails();
                for (k = lkeepers)                         // keepers over the board leg / S-jog
                    translate([k[0], k[1], k[4]]) cube([k[2] - k[0], k[3] - k[1], z_seam - k[4] + eps]);
            }
        }
        if (use_patch) translate([patch_xy[0], patch_xy[1], 0]) {   // RX window / radome
            if (patch_window)       // patch stands up into it: patch_margin all round
                translate([0, 0, z_seam - 1]) linear_extrude(lid_t + 2)
                    rrect(-radome_w / 2, -radome_w / 2, radome_w / 2, radome_w / 2, 1.0);
            else if (patch_cover < lid_t)
                translate([0, 0, z_seam - 1]) linear_extrude(1 + lid_t - patch_cover)
                    square(radome_w, center = true);
        }
        if (usb_open_top)          // USB-C overmold opening continues through the lid
            translate([usb_x - usb_open_w / 2, out_y0 - 1 - max(0, pf_omax), z_seam - 1])
                cube([usb_open_w, cav_y0 + 0.5 - out_y0 + 1 + max(0, pf_omax), lid_t + 2]);
        if (use_sma && sma_recess > 0) at_side(tx_s, tx_along)     // clearance over the SMA flange
            translate([-(tx_jw + 0.5), -(tx_jt + 0.5), z_seam - 1])
                cube([2 * (tx_jw + 0.5), tx_jt + 0.5, 1 + sma_recess]);
        if (fxp_lid) {
            // flex pocket in the lid underside (flex + adhesive, lid_skin left)
            translate([lpk_x0, lpk_y0, z_seam - 1]) cube([lpk_x1 - lpk_x0, lpk_y1 - lpk_y0, z_lpk - z_seam + 1]);
            // cable groove from the pocket edge to the first clip, ceiling falling
            // from the pocket ceiling to the lid underside
            hull() {
                translate([x_ll - groove_hw, lpk_y0 - eps, z_seam - eps]) cube([2 * groove_hw, 2 * eps, z_lpk - z_seam + eps]);
                translate([x_ll - groove_hw, y_clip0, z_seam - eps]) cube([2 * groove_hw, eps, 2 * eps]);
            }
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
    color("lightgrey") for (p = stake_xy)                  // USB-C shell stakes
        translate([p[0] - 0.25, p[1] - 0.6, z_pcb_bot - usb_stake_below]) cube([0.5, 1.2, usb_stake_below + pcb_t]);
}
// lid mode: flex (nominal, pushed +X/+Y), its solder joints (1.0 drawn, 1.7 max)
module fxp_lid_ghost() {
    color("chocolate") translate([lpk_x1 - fl_x, fl_y0, z_fl_lo_nom]) cube([fl_x, fl_y, fxp_t_nom]);
    color("khaki") translate([lpk_x1 - fl_x, fl_y0, z_fl_lo_nom + fxp_t_nom]) cube([fl_x, fl_y, fxp_adh]);
    color("silver") for (y = [fxp_cable_pad, fxp_on_flex - 2])
        translate([x_ll - 1, fl_y0 + y, z_fl_lo_nom - 1.0]) cube([2, 2, 1.0]);
}
// the part of the cable that stays with the lid (flex pads to the rail end)
module lid_cable_ghost() color("dimgray")
    polyline3([lcab[0], lcab[1], lcab[2], [x_ll, rail_lo, z_ll]], cable_d);
module antennas_ghost() {
    if (use_patch) color("wheat")
        translate([patch_xy[0], patch_xy[1], z_pcb_top + patch_tape])
            linear_extrude(patch_h - 0.1) offset(r = 1.5) square(patch_sz - 3, center = true);
    if (use_patch) color("goldenrod")                      // feed pin, worst-case length
        translate([pin_xy[0], pin_xy[1], z_pcb_bot - pin_below]) cylinder(d = 0.9, h = pin_below + pcb_t + patch_tape);
    if (use_fxp) {
        color("gold")                                      // U.FL receptacle
            translate([ufl_xy[0] - 1.5, ufl_xy[1] - 1.3, z_pcb_top]) cube([3.0, 2.6, 1.25]);
        color("silver") {                                  // mated plug, cable toward -Y
            translate([ufl_xy[0], ufl_xy[1], z_pcb_top + 1.0]) cylinder(d = 2.8, h = ufl_mated_h - 1.0);
            translate([ufl_xy[0] - ufl_plug_w / 2 + 0.5, y_crimp, z_pcb_top + ufl_mated_h - 1.4])
                cube([ufl_plug_w - 1.0, ufl_xy[1] - y_crimp, 1.4]);
        }
        if (fxp_bay) color("dimgray") polyline3(cab_pts(y_c), cable_d); // cable at the nominal length
        if (fxp_lid) color("dimgray") polyline3(lcab, cable_d);
        if (fxp_bay) color("chocolate")                    // FXP70 flex, nominal position
            translate([fx0, y_c + fxp_c_off - fxp_sz[1], z_pk + fxp_adh]) cube([fxp_sz[0], fxp_sz[1], fxp_t_nom]);
        if (fxp_lid) fxp_lid_ghost();
    }
    if (use_sma) at_side(tx_s, tx_along) {
        color("gold") {
            translate([-tx_jw, -tx_jt, sma_z - sma_body[2] / 2]) cube([2 * tx_jw, tx_jt, sma_body[2]]);
            for (k = [0, 1]) {                             // legs: lower (cut length) and upper
                lo = leg_loc(2 * k - 1, leg_len[k], 0);
                up = leg_loc(2 * k - 1, sma_leg_l, 0);
                translate([lo[0][0], lo[0][1], z_pcb_bot - sma_leg_below])
                    cube([lo[1][0] - lo[0][0], lo[1][1] - lo[0][1], sma_leg_below]);
                translate([up[0][0], up[0][1], z_pcb_top]) cube([up[1][0] - up[0][0], up[1][1] - up[0][1], 1.02]);
            }
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
module cut(ax, v, lo = false) intersection() {          // keep x (or y) >= v, or <= v if lo
    children();
    if (ax == "x") translate([lo ? v - 500 : v, -500, -1]) cube([500, 1000, 100]);
    else           translate([-500, lo ? v - 1000 : v, -1]) cube([1000, 1000, 100]);
}
module section_at(ax, v, lo = false) {                  // preview draws cut faces in one colour
    if (sec_render) {                                   // ... unless rendered first
        color("gainsboro") render() cut(ax, v, lo) base();
        color("lightsteelblue") render() cut(ax, v, lo) lid();
    } else {
        color("gainsboro") cut(ax, v, lo) base();
        color("lightsteelblue") cut(ax, v, lo) lid();
    }
    cut(ax, v, lo) magnets_ghost();
    cut(ax, v, lo) pcb_ghost();
    cut(ax, v, lo) antennas_ghost();
    cut(ax, v, lo) screws_ghost();
}
// 2D cross-section drawings (projection cut, one colour per part, labels).
// ax "x": plane x = v, drawn as (y, z); ax "y": plane y = v, drawn as (x, z).
function sec_m(ax, v) = ax == "x" ? [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, -v], [0, 0, 0, 1]]
                                  : [[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, v], [0, 0, 0, 1]];
module sec_lay(ax, v, c, z) color(c) translate([0, 0, z]) linear_extrude(0.01)
    projection(cut = true) multmatrix(sec_m(ax, v)) children();
module sec_label(p, t, sz = 0.55) color("black") translate([p[0], p[1], 1]) text(t, size = sz, valign = "center");
// true if the plane (ax = v) crosses the XY box a..b (skips empty projections)
function sec_hit(ax, v, a, b) = ax == "x" ? v > a[0] && v < b[0] : v > a[1] && v < b[1];
module section2d(ax, v) {
    sec_lay(ax, v, "gainsboro", 0) base();
    sec_lay(ax, v, "lightsteelblue", 0.02) lid();
    sec_lay(ax, v, "firebrick", 0.04) magnets_ghost();
    sec_lay(ax, v, "darkgreen", 0.04) translate([pcb_x0, pcb_y0, z_pcb_bot]) linear_extrude(pcb_t) pcb2d();
    if (sec_hit(ax, v, [usb_x - usb_body[0] / 2, pcb_y0], [usb_x + usb_body[0] / 2, pcb_y0 + usb_body[1]]))
        sec_lay(ax, v, "lightgrey", 0.05) translate([usb_x - usb_body[0] / 2, pcb_y0 - usb_overhang, z_pcb_top]) cube(usb_body);
    if (use_patch && sec_hit(ax, v, patch_xy - [patch_sz, patch_sz] / 2, patch_xy + [patch_sz, patch_sz] / 2))
        sec_lay(ax, v, "wheat", 0.06) translate([patch_xy[0], patch_xy[1], z_pcb_top + patch_tape])
            linear_extrude(patch_h - 0.1) offset(r = 1.5) square(patch_sz - 3, center = true);
    for (h = holes) if (sec_hit(ax, v, h - [2, 2], h + [2, 2])) sec_lay(ax, v, "dimgray", 0.06) screws_ghost();
    if (fxp_lid) {
        if (sec_hit(ax, v, [lpk_x1 - fl_x, fl_y0], [lpk_x1, lpk_y1])) {
        sec_lay(ax, v, "chocolate", 0.08) translate([lpk_x1 - fl_x, fl_y0, z_fl_lo_nom]) cube([fl_x, fl_y, fxp_t_nom]);
        sec_lay(ax, v, "orange", 0.08) translate([lpk_x1 - fl_x, fl_y0, z_fl_lo_nom + fxp_t_nom]) cube([fl_x, fl_y, fxp_adh]);
        }
        if (sec_hit(ax, v, [x_ll - 1, fl_y0 + fxp_cable_pad], [x_ll + 1, fl_y0 + fxp_on_flex]))
            sec_lay(ax, v, "silver", 0.09) for (y = [fxp_cable_pad, fxp_on_flex - 2])
                translate([x_ll - 1, fl_y0 + y, z_fl_lo_nom - 1.0]) cube([2, 2, 1.0]);
        if (sec_hit(ax, v, [x_ll - 1, y_u_lo - hp_r - 1], [x_bl + 1, fl_y0 + fxp_on_flex + 1]))
            sec_lay(ax, v, "black", 0.1) polyline3(lcab, cable_d);
        if (sec_hit(ax, v, [ufl_xy[0] - 1.5, y_crimp], [ufl_xy[0] + 1.5, ufl_xy[1] + 1.4]))
            sec_lay(ax, v, "gold", 0.1) {
            translate([ufl_xy[0] - 1.5, ufl_xy[1] - 1.3, z_pcb_top]) cube([3.0, 2.6, 1.25]);
            translate([ufl_xy[0], ufl_xy[1], z_pcb_top + 1.0]) cylinder(d = 2.8, h = ufl_mated_h - 1.0);
            translate([ufl_xy[0] - ufl_plug_w / 2 + 0.5, y_crimp, z_pcb_top + ufl_mated_h - 1.4])
                cube([ufl_plug_w - 1.0, ufl_xy[1] - y_crimp, 1.4]);
        }
    }
}
module pf_lay(z) translate([0, 0, z]) linear_extrude(0.01) children();   // profile2d layers
module print_plate() {
    base();
    translate([out_x1 + 8 + out_x + 2 * max(0, pf_omax), out_y0 + out_y1, 0]) lid_print();
}

// ---------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------
if (part == "base") base();
else if (part == "lid") lid_print();
else if (part == "lid_under") rotate([180, 0, 0]) translate([0, 0, -z_top]) {   // lid from below + what it holds
    color("lightsteelblue") lid();
    if (fxp_lid) { fxp_lid_ghost(); lid_cable_ghost(); }
}
else if (part == "assembly") assembly(explode);
else if (part == "closed") { color("gainsboro") base(); color("lightsteelblue") lid(); }
else if (part == "sec2d_edge") {                   // X-Z section through both side walls
    section2d("y", sec_y);
    sec_label([-30, z_top + 1.6], str("Section y = ", r2(sec_y), ", seen from -y: X to the right, Z up. Rounded shell: ",
              bot_ang, " deg + R ", bot_r, " bottom, convex R ", side_r, " side (+", r2(pf_omax), " at Z ", bulge_z,
              "), R ", top_r, " + ", top_ang, " deg top"), 0.6);
    sec_label([-30, z_top + 0.7], str("wall ", wall_t, " nominal, min ", r2(wall_at(wall_t, z_floor, z_wall)),
              " after rounding; phone face flat to ", r2(out_x - bot_inset), ", ring pocket to ", r2(ring_ro)), 0.6);
}
else if (part == "profile2d") {                    // the side profile in its section plane (x = o, y = Z)
    rim = out_y1 - lpk_y1;
    color("lightsteelblue") pf_lay(0) polygon(concat(prof, [[-5, z_top], [-5, 0]]));   // shell (o, z)
    color("white") pf_lay(0.02) translate([-5, z_floor]) square([5 - wall_t, z_wall - z_floor]);   // cavity (flats)
    color("orange") pf_lay(0.04) translate([-5, z_seam]) square([5 - rim, z_lpk - z_seam]);         // flex pocket (top wall)
    color("firebrick") pf_lay(0.04) translate([-5, skin_t]) square([5 - (out_x - ring_ro), z_pause - skin_t]);  // ring pocket (X sides)
    color("black") pf_lay(0.06) translate([-5, z_seam - 0.01]) square([5 + bulge + 0.6, 0.02]);    // seam
    color("dimgray") pf_lay(0.06) translate([-wc(out_r) - 0.015, z_floor]) square([0.03, z_wall - z_floor]);   // cavity at the corner diagonal
    color("red") pf_lay(0.08) difference() {                                                 // fxp70_inlid outline (0.4 chamfers)
        polygon([[-5, 0], [-edge_chamfer, 0], [0, edge_chamfer], [0, z_top - edge_chamfer], [-edge_chamfer, z_top], [-5, z_top]]);
        offset(delta = -0.03) polygon([[-5, 0], [-edge_chamfer, 0], [0, edge_chamfer], [0, z_top - edge_chamfer], [-edge_chamfer, z_top], [-5, z_top]]);
    }
    color("black") {
        sec_label([1.4, 11.0], str("lid face inset ", top_inset, ", ", top_ang, " deg"), 0.28);
        sec_label([1.4, 10.2], str("R ", top_r, " top round, seam o +", r2(o_at(z_seam))), 0.28);
        sec_label([1.4, 6.0], str("widest +", r2(pf_omax), " at Z ", bulge_z, ", side R ", side_r), 0.28);
        sec_label([1.4, 2.6], str("R ", bot_r, " bottom round"), 0.28);
        sec_label([1.4, 0.4], str("phone face inset ", bot_inset, ", ", bot_ang, " deg"), 0.28);
        sec_label([-4.9, 10.85], str("flex pocket, rim ", r2(rim)), 0.25);
        sec_label([-4.9, 7.0], str("cavity (wall ", wall_t, ")"), 0.25);
        sec_label([-4.9, 2.1], "ring pocket", 0.25);
        sec_label([-4.9, 12.0], str("Side profile, offset o from the nominal outline (x) vs Z (y), 1:1. Red: fxp70_inlid (0.4 chamfers)"), 0.25);
        sec_label([-4.9, 11.65], str("grey line: cavity at the plan-corner diagonal (corner r ", r2(out_r), ")"), 0.25);
    }
}
else if (part == "routing") {
    color("gainsboro") base();
    magnets_ghost();
    pcb_ghost();
    antennas_ghost();
    screws_ghost();
}
else if (part == "section") {
    color("gainsboro") half() base();
    half() magnets_ghost();
    half() pcb_ghost();
    half() antennas_ghost();
    color("lightsteelblue") half() lid();
    half() screws_ghost();
}
else if (part == "section_patch") section_at("x", pin_xy[0]);
else if (part == "section_cable") section_at("y", y_c + sec_off, true);
else if (part == "section_flex") section_at("x", fxp_c[0] + sec_off, true);
else if (part == "section_ant") section_at("x", x_ll + sec_off, true);
else if (part == "section_hairpin") section_at("y", y_u + sec_off);
else if (part == "section_ant_x") section_at("y", fl_c[1] + sec_off, true);
else if (part == "sec2d_ant") {                    // Y-Z section through the flex centre
    section2d("x", fl_c[0] + sec_off);
    sec_label([-24, z_top + 1.6], str("Section x = ", r2(fl_c[0] + sec_off), " (flex centre, board x ",
              r2(fl_c[0] + sec_off - pcb_x0), "), seen from +x: Y to the right, Z up. Lid skin ", lid_skin,
              ", pocket ", r2(lpk_d), " deep; flex copper ", r2(l_gnd), " over the board top, ", r2(l_gnd2), " over L2 GND"), 0.6);
    sec_label([-24, z_top + 0.7], str("Flex edge ", r2(fl_y0 - win_y1), " from the window (", r2(l_win), " worst), ",
              r2(l_rx_nom), " from the patch (", r2(l_rx), " worst footprint); window web ", win_web,
              "; flex runs over the top wall, lid lip cut there"), 0.6);
    sec_label([-8, z_seam - 1.0], "RX patch in the open window");
    sec_label([fl_c[1] - 3, z_seam - 1.0], "FXP70 flex in the lid pocket");
}
else if (part == "sec2d_exit") {                   // Y-Z section on the cable exit (x = x_ll)
    section2d("x", x_ll + sec_off);
    sec_label([-8, z_top + 1.6], str("Section x = ", r2(x_ll + sec_off), " (cable exit / lid leg, board x ",
              r2(x_ll + sec_off - pcb_x0), "), seen from +x: Y to the right, Z up"), 0.5);
    sec_label([-8, z_top + 0.7], str("cable on the flex, groove to the first clip at y ", r2(y_clip0),
              ", lid leg against the lid underside (rails either side, out of this plane), hairpin from y ", r2(y_u)), 0.5);
}
else if (part == "sec2d_hairpin") {                // X-Z section across both legs, through the clip rails
    section2d("y", rail_lo + 1 + sec_off);
    sec_label([0, z_top + 1.6], str("Section y = ", r2(rail_lo + 1 + sec_off), " (both cable legs, 1 mm above the rail ends),",
              " seen from -y: X to the right, Z up"), 0.45);
    sec_label([0, z_top + 0.7], str("lid leg x ", r2(x_ll), " in the clip rails; board leg x ", r2(x_bl),
              " on the board GND; ", r2(hp_s), " / ", r2(hp_dz), " apart (hairpin R ", hp_r, " below y ", r2(y_u), ")"), 0.45);
    sec_label([0.5, z_pcb_top + 2.2], "RX patch");
    sec_label([x_bl - 5.2, z_seam - 0.9], "lip notched");
}
else if (part == "sec2d_ant_x") {                  // X-Z section across the flex centre
    section2d("y", fl_c[1] + sec_off);
    sec_label([-28, z_top + 1.6], str("Section y = ", r2(fl_c[1] + sec_off), " (flex centre, board y ",
              r2(fl_c[1] + sec_off - pcb_y0), "), seen from -y: X to the right, Z up"), 0.6);
    sec_label([-28, z_top + 0.7], str("flex X ", r2(lpk_x1 - fl_x), " to ", r2(lpk_x1), "; mated U.FL J3 at x ",
              r2(ufl_xy[0]), ", ", r2(l_ufl), " from the flex"), 0.6);
}
else if (part == "section_sma") section_at(tx_s % 2 == 1 ? "y" : "x", tx_along + sec_off);
else if (part == "pcb_outline") pcb2d();
else print_plate();
