#203: resolve the relative-normal warning before a visual test

202restdata passes semantic/region bounds. The oldhelper calls14faces bad because
their normals turn >87degrees; area ratios remain.367..2.441, no nearcollapse.
Relative normalrotation is not a general inversiontest: a rigid180degree rotation
is a valid counterexample. Added thatnegativecontrol and propertrianglecrossing/
disjoint controls (2tests pass).

Actualreadonlyreview undercanonicalheavyjob examines2152affectedskinfaces against
wholeconnectedskin:0old/0newpropernonadjacentcrossings,0introducedpairs. All14
flaggedfaces haveoutsidepositive andinside-negative .5mmnormalprobes. The normals
remainoutward, notinside-out. Preserveoriginalhelperwarning/report; do not silently
changeitshistory. This closes thatparticularrestwarning for eligibilitytoconduct
nativeviews, NOT artisticacceptance/fullcollision/posequalification. Sharedvertex,
coplanarcontact andproductionconsumer remain outside thisnumericalclaim.

203actualclosedpectoralhandler must verifyliveoriginalrig/actions/relativekeys,
exactdistals/non-skin/outside, <=.06mprox/.18mregion andactual283333339rig/world/
outsidecagebefore/after. Thenactualneutralfront/side first, posedmatrixonlyif
positive. Anyvisiblecrease/web/bulb stillfailsregardlessofthesenumbers.
