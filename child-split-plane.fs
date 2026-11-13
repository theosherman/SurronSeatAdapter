
annotation { "Feature Type Name" : "Adapter split plane" }
export const adapterSplitPlane = defineFeature(function(context is Context, id is Id, definition is map)
precondition {}
{ opPlane(context, id + "plane", { "plane" : plane(vector(0, -0.09288539833894989, 0.06305711325274752) * meter, vector(0, 0.9799247046208681, -0.19936793441700865), vector(1, 0, 0)) }); });

