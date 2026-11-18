FeatureScript 3112;
// Includes the original Fusion split plane for use only in the derived child Part Studio.
import(path : "onshape/std/common.fs", version : "3112.0");

annotation { "Feature Type Name" : "BottomSketch plane" }
export const sourcePlane0 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(0, 0, 1), vector(1, 0, 0)) }); });

annotation { "Feature Type Name" : "SideSketch plane" }
export const sourcePlane1 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(1, 0, 0), vector(0, 1, 0)) }); });

annotation { "Feature Type Name" : "RearSketch plane" }
export const sourcePlane2 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, -0.263445982162752, 0) * meter, vector(0, 1, 0), vector(1, 0, 0)) }); });

annotation { "Feature Type Name" : "TrunkDovetailSketch plane" }
export const sourcePlane3 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, -0.12477082228630328, 0.07410298570063958) * meter, vector(0, -0.8597932986246306, 0.5106422266520627), vector(1, 0, 0)) }); });

annotation { "Feature Type Name" : "BoltHolesSketch plane" }
export const sourcePlane4 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0.008627219333715026, 0.04240413776674599) * meter, vector(0, 0.1993679344170023, 0.9799247046208692), vector(-1, 0, 0)) }); });

annotation { "Feature Type Name" : "SeatHangerSketch plane" }
export const sourcePlane5 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0.008627219333715033, 0.042404137766746015) * meter, vector(0, 0.1993679344170023, 0.9799247046208692), vector(-1, 0, 0)) }); });

annotation { "Feature Type Name" : "SeatCutoutSketch plane" }
export const sourcePlane6 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0.020734457960456677, 0.03255893705824783, 0.03153629206339344) * meter, vector(0.41597736869348517, 0.6532015927677732, 0.6326851570413905), vector(-0.734548958762177, 0.6515051038369168, -0.18968111887019787)) }); });

annotation { "Feature Type Name" : "HandleMountSketch plane" }
export const sourcePlane7 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(1, 0, 0), vector(0, 1, 0)) }); });

annotation { "Feature Type Name" : "FrontCutSketch plane" }
export const sourcePlane8 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(0, 0, 1), vector(1, 0, 0)) }); });

annotation { "Feature Type Name" : "RearSeatNotchSketch plane" }
export const sourcePlane9 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0.008945337453041248, 0.03132749600074048) * meter, vector(0, 0.27456857573274995, 0.9615675208845652), vector(-0.9999999999999999, 0, 0)) }); });

annotation { "Feature Type Name" : "FrontDovetailSketch plane" }
export const sourcePlane10 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(1, 0, 0), vector(0, 1, 0)) }); });

annotation { "Feature Type Name" : "HingeTrajectorySketch plane" }
export const sourcePlane11 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(1, 0, 0), vector(0, 1, 0)) }); });

annotation { "Feature Type Name" : "RearCutSketch plane" }
export const sourcePlane12 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, -0.04732528017370813, 0.06758750454859343) * meter, vector(0, 0.5735764363510457, -0.819152044288992), vector(1, 0, 0)) }); });

annotation { "Feature Type Name" : "BodyCutSketch plane" }
export const sourcePlane13 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0.008627219333715026, 0.04240413776674599) * meter, vector(0, 0.1993679344170023, 0.9799247046208692), vector(1, 0, 0)) }); });

annotation { "Feature Type Name" : "AirtagCutSketch plane" }
export const sourcePlane14 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0.008627219333715023, 0.04240413776674597) * meter, vector(0, 0.1993679344170023, 0.9799247046208692), vector(-1, 0, 0)) }); });

annotation { "Feature Type Name" : "SplitBodySketch plane" }
export const sourcePlane15 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0, 0) * meter, vector(1, 0, 0), vector(0, 1, 0)) }); });

annotation { "Feature Type Name" : "TopJointSketch plane" }
export const sourcePlane16 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, 0.008627219333715032, 0.042404137766746015) * meter, vector(0, 0.1993679344170023, 0.9799247046208692), vector(-1, 0, 0)) }); });

annotation { "Feature Type Name" : "SideJointSketch plane" }
export const sourcePlane17 = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0.04018209231707785, 0.0021465465393884944, 0.010550613315607795) * meter, vector(-0.9659258262890683, -0.051600218409869884, -0.2536231763223432), vector(0.05334441550751669, -0.998576173025454, 0)) }); });

