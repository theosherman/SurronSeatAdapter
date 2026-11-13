
annotation { "Feature Type Name" : "Five connector cutouts" }
export const connectorCutouts = defineFeature(function(context is Context, id is Id, definition is map)
precondition
{
    annotation { "Name" : "Cutout depth" }
    isLength(definition.depth, LENGTH_BOUNDS);
}
{
    var targets = qUnion(evaluateQuery(context, qBodyType(qEverything(EntityType.BODY), BodyType.SOLID)));
    var tools = [];
    var sk0 = newSketchOnPlane(context, id + "profile0", { "sketchPlane" : plane(vector(0, 0.008627219333715026, 0.04240413776674599) * meter, vector(0, 0.1993679344170023, 0.9799247046208692), vector(-1, 0, 0)) });
    skLineSegment(sk0, "line0", { "start" : vector(-0.02654700538379263, 0.08359226295038652) * meter, "end" : vector(0, 0.08359226295038652) * meter });
    skLineSegment(sk0, "line1", { "start" : vector(0.02654700538379263, 0.08359226295038652) * meter, "end" : vector(0, 0.08359226295038652) * meter });
    skLineSegment(sk0, "line2", { "start" : vector(0.015, 0.10359226295038652) * meter, "end" : vector(0.02654700538379263, 0.08359226295038652) * meter });
    skLineSegment(sk0, "line3", { "start" : vector(-0.015, 0.10359226295038652) * meter, "end" : vector(0.015, 0.10359226295038652) * meter });
    skLineSegment(sk0, "line4", { "start" : vector(-0.015, 0.10359226295038652) * meter, "end" : vector(-0.02654700538379263, 0.08359226295038652) * meter });
    skLineSegment(sk0, "line5", { "start" : vector(0.015, 0.10359226295038652) * meter, "end" : vector(0.02654700538379263, 0.12359226295038653) * meter });
    skLineSegment(sk0, "line6", { "start" : vector(0.02654700538379263, 0.12359226295038653) * meter, "end" : vector(0, 0.12359226295038653) * meter });
    skLineSegment(sk0, "line7", { "start" : vector(-0.02654700538379263, 0.12359226295038653) * meter, "end" : vector(0, 0.12359226295038653) * meter });
    skLineSegment(sk0, "line8", { "start" : vector(-0.015, 0.10359226295038652) * meter, "end" : vector(-0.02654700538379263, 0.12359226295038653) * meter });
    skSolve(sk0);
    opExtrude(context, id + "tool0", { "entities" : qSketchRegion(id + "profile0"), "direction" : vector(0, -0.1993679344170023, -0.9799247046208692), "endBound" : BoundingType.BLIND, "endDepth" : definition.depth });
    tools = append(tools, qCreatedBy(id + "tool0", EntityType.BODY));
    var sk1 = newSketchOnPlane(context, id + "profile1", { "sketchPlane" : plane(vector(0.04018209231707784, 0.002146546539388494, 0.010550613315607794) * meter, vector(-0.9659258262890683, -0.051600218409869884, -0.2536231763223432), vector(0.05334441550751669, -0.998576173025454, 0)) });
    skLineSegment(sk1, "line0", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.1039526102189825, -0.01613036553308185) * meter });
    skLineSegment(sk1, "line1", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10841887746696757, -0.012123813790051991) * meter });
    skLineSegment(sk1, "line2", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10065489830685405, -0.00047389415078744057) * meter });
    skLineSegment(sk1, "line3", { "start" : vector(0.10065489830685405, -0.00047389415078744057) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk1, "line4", { "start" : vector(0.1039526102189825, -0.01613036553308185) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk1, "line5", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.11412178668200079, -0.013988438815382451) * meter });
    skLineSegment(sk1, "line6", { "start" : vector(0.11412178668200079, -0.013988438815382451) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk1, "line7", { "start" : vector(0.11082407476987234, 0.0016680325669119437) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk1, "line8", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.11082407476987234, 0.0016680325669119435) * meter });
    skSolve(sk1);
    opExtrude(context, id + "tool1", { "entities" : qSketchRegion(id + "profile1"), "direction" : vector(0.9659258262890683, 0.051600218409869884, 0.2536231763223432), "endBound" : BoundingType.BLIND, "endDepth" : definition.depth });
    tools = append(tools, qCreatedBy(id + "tool1", EntityType.BODY));
    var sk2 = newSketchOnPlane(context, id + "profile2", { "sketchPlane" : plane(vector(0.045984503669784654, -0.002170744942370053, -0.010669552266162237) * meter, vector(0.9659258262890681, 0.05160021840986997, 0.2536231763223436), vector(-0.053344415507521975, -0.9191942138120434, 0.39017479496838386)) });
    skLineSegment(sk2, "line0", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.1039526102189825, -0.01613036553308185) * meter });
    skLineSegment(sk2, "line1", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10841887746696757, -0.012123813790051991) * meter });
    skLineSegment(sk2, "line2", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10065489830685405, -0.00047389415078744057) * meter });
    skLineSegment(sk2, "line3", { "start" : vector(0.10065489830685405, -0.00047389415078744057) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk2, "line4", { "start" : vector(0.1039526102189825, -0.01613036553308185) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk2, "line5", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.11412178668200079, -0.013988438815382451) * meter });
    skLineSegment(sk2, "line6", { "start" : vector(0.11412178668200079, -0.013988438815382451) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk2, "line7", { "start" : vector(0.11082407476987234, 0.0016680325669119437) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk2, "line8", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.11082407476987234, 0.0016680325669119435) * meter });
    skSolve(sk2);
    opExtrude(context, id + "tool2", { "entities" : qSketchRegion(id + "profile2"), "direction" : vector(0.9659258262890682, 0.05160021840986998, 0.2536231763223437), "endBound" : BoundingType.BLIND, "endDepth" : definition.depth });
    tools = append(tools, qCreatedBy(id + "tool2", EntityType.BODY));
    var sk3 = newSketchOnPlane(context, id + "profile3", { "sketchPlane" : plane(vector(-0.04018209231707784, 0.002146546539388494, 0.010550613315607794) * meter, vector(-0.9659258262890683, 0.051600218409869884, 0.2536231763223432), vector(-0.05334441550751669, -0.998576173025454, 0)) });
    skLineSegment(sk3, "line0", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.1039526102189825, -0.01613036553308185) * meter });
    skLineSegment(sk3, "line1", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10841887746696757, -0.012123813790051991) * meter });
    skLineSegment(sk3, "line2", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10065489830685405, -0.00047389415078744057) * meter });
    skLineSegment(sk3, "line3", { "start" : vector(0.10065489830685405, -0.00047389415078744057) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk3, "line4", { "start" : vector(0.1039526102189825, -0.01613036553308185) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk3, "line5", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.11412178668200079, -0.013988438815382451) * meter });
    skLineSegment(sk3, "line6", { "start" : vector(0.11412178668200079, -0.013988438815382451) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk3, "line7", { "start" : vector(0.11082407476987234, 0.0016680325669119437) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk3, "line8", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.11082407476987234, 0.0016680325669119435) * meter });
    skSolve(sk3);
    opExtrude(context, id + "tool3", { "entities" : qSketchRegion(id + "profile3"), "direction" : vector(-0.9659258262890683, 0.051600218409869884, 0.2536231763223432), "endBound" : BoundingType.BLIND, "endDepth" : definition.depth });
    tools = append(tools, qCreatedBy(id + "tool3", EntityType.BODY));
    var sk4 = newSketchOnPlane(context, id + "profile4", { "sketchPlane" : plane(vector(-0.045984503669784654, -0.002170744942370053, -0.010669552266162237) * meter, vector(0.9659258262890681, -0.05160021840986997, -0.2536231763223436), vector(0.053344415507521975, -0.9191942138120434, 0.39017479496838386)) });
    skLineSegment(sk4, "line0", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.1039526102189825, -0.01613036553308185) * meter });
    skLineSegment(sk4, "line1", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10841887746696757, -0.012123813790051991) * meter });
    skLineSegment(sk4, "line2", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.10065489830685405, -0.00047389415078744057) * meter });
    skLineSegment(sk4, "line3", { "start" : vector(0.10065489830685405, -0.00047389415078744057) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk4, "line4", { "start" : vector(0.1039526102189825, -0.01613036553308185) * meter, "end" : vector(0.1023037542629183, -0.00830212984193465) * meter });
    skLineSegment(sk4, "line5", { "start" : vector(0.10841887746696757, -0.012123813790051991) * meter, "end" : vector(0.11412178668200079, -0.013988438815382451) * meter });
    skLineSegment(sk4, "line6", { "start" : vector(0.11412178668200079, -0.013988438815382451) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk4, "line7", { "start" : vector(0.11082407476987234, 0.0016680325669119437) * meter, "end" : vector(0.11247293072593655, -0.006160203124235268) * meter });
    skLineSegment(sk4, "line8", { "start" : vector(0.10635780752188725, -0.0023385191761179413) * meter, "end" : vector(0.11082407476987234, 0.0016680325669119435) * meter });
    skSolve(sk4);
    opExtrude(context, id + "tool4", { "entities" : qSketchRegion(id + "profile4"), "direction" : vector(-0.9659258262890682, 0.05160021840986998, 0.2536231763223437), "endBound" : BoundingType.BLIND, "endDepth" : definition.depth });
    tools = append(tools, qCreatedBy(id + "tool4", EntityType.BODY));
    opBoolean(context, id + "cut", { "tools" : qUnion(tools), "targets" : targets, "operationType" : BooleanOperationType.SUBTRACTION });
});

