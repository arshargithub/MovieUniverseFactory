"""Reviewed costume-only functional tailoring/boot construction helpers."""
import math


def boot_section(z):
    """Coherent adult riding-boot last: ankle, instep, toe and flat sole."""
    sections=[(-11.24,.15,.44,.42),(-11.33,.15,.435,.415),(-11.70,.15,.365,.33),
              (-12.05,.14,.33,.32),(-12.35,.09,.345,.40),(-12.62,-.02,.38,.58),
              (-12.82,-.28,.435,.85),(-13.10,-.36,.44,.94),(-13.28,-.36,.445,.95),
              (-13.36,-.36,.45,.96)]
    return min(sections,key=lambda p:abs(p[0]-z))


def boot_flex(z,a):
    envelope=math.exp(-((z+12.3)/.30)**2)*(.35+.65*max(0.,math.cos(a))**2)
    return .035*envelope*math.sin(32*z+1.1*math.sin(3*a))


def finishing(mats, *, boots_only=False):
    import bpy
    from mathutils import Vector
    from wardrobe_studio import panel,line,smoothstep
    rig=bpy.data.objects['MF_body156_fit_rig'];world=rig.matrix_world
    from mathutils.bvhtree import BVHTree
    from wardrobe_balance import outer_ray_radius
    from wardrobe_footbed import footprint,center as footprint_center,radius as footprint_radius
    body=bpy.data.objects['MF_studio_adult_body']
    rest=[body.matrix_world@v.co for v in body.data.vertices]
    for source in bpy.context.scene.objects:
        if source.name in ('MF_fit_boots_173_visible','MF_fit_closed_boot_L_173_visible','MF_fit_closed_boot_R_173_visible'):
            source.hide_render=True
    for side,sign in (('L',1),('R',-1)):
        hull=footprint([(p.x,p.y) for p in rest if p.x*sign>0 and p.z<-12.72])
        bed_center=footprint_center(hull)
        skin=BVHTree.FromPolygons(rest,[tuple(f.vertices) for f in body.data.polygons if all(rest[i].x*sign>0 and rest[i].z<-10.8 for i in f.vertices)])
        matrices={name:world@rig.pose.bones[name+'.'+side].matrix@rig.data.bones[name+'.'+side].matrix_local.inverted()@world.inverted() for name in ('shin','foot')}
        def pose(p):
            w=smoothstep((-12.05-p.z)/.65)
            return (matrices['shin']@p)*(1-w)+(matrices['foot']@p)*w
        points=[];faces=[];n=64
        heights=[-11.24,-11.33,-11.70,-12.05,-12.12,-12.22,-12.32,-12.42,-12.52,-12.62,-12.82,-13.10,-13.43,-13.47]
        for j,z in enumerate(heights):
            _,cy,rx,ry=boot_section(z)
            probe=max(z,-13.18)
            sample=[p for p in rest if p.x*sign>0 and abs(p.z-probe)<.15]
            if sample:
                cx=(min(p.x for p in sample)+max(p.x for p in sample))/2
                cy=(min(p.y for p in sample)+max(p.y for p in sample))/2
            else:cx=sign*.95
            if z<-12.92:cx,cy=bed_center
            center=Vector((cx,cy,z));radii=[]
            for i in range(n):
                a=math.tau*i/n;direction=Vector((math.sin(a),-math.cos(a),0))
                query=Vector((cx,cy,probe))
                r=footprint_radius(hull,bed_center,(direction.x,direction.y)) if z<-12.92 else outer_ray_radius(skin,query,direction,1.9)
                radii.append(r+.11 if r is not None else 1./math.sqrt((direction.x/(rx+.10))**2+(direction.y/(ry+.10))**2))
            # Bridge toe separations and small anatomical hollows like a last.
            radii=[max(radii[(i+k)%n] for k in (-2,-1,0,1,2)) for i in range(n)]
            for i in range(n):
                a=math.tau*i/n
                crease=boot_flex(z,a)
                p=center+Vector(((radii[i]+crease)*math.sin(a),-(radii[i]+crease)*math.cos(a),0))
                points.append(tuple(pose(p)))
        for j in range(len(heights)-1):
            for i in range(n):k=j*n+i;l=j*n+(i+1)%n;faces.append((k,k+n,l+n,l))
        faces.append(tuple(reversed(range((len(heights)-1)*n,len(heights)*n))))
        boot=panel('MF_173_work_boot_'+side,points,faces,mats['boot'],.018,1)
        support=Vector((bed_center[0],min(p[1] for p in hull)+.35,-13.46))
        boot['static_footbed_support_world']=tuple(pose(support))
        boot['static_footbed_normal_world']=tuple((matrices['foot'].to_3x3()@Vector((0,0,1))).normalized())
        wear=boot.data.attributes.get('MF_173_contact_wear') or boot.data.attributes.new('MF_173_contact_wear','FLOAT','POINT')
        for index,item in enumerate(wear.data):
            j,i=divmod(index,n);a=math.tau*i/n
            item.value=.22*(math.exp(-((heights[j]+13.1)/.20)**2)*max(0,math.cos(a))+.45*math.exp(-((heights[j]+11.33)/.12)**2))
        boot.data.materials.append(mats['sole'])
        for f in boot.data.polygons:
            if f.index>=(len(heights)-2)*n:f.material_index=1
        for j in (0,1,len(heights)-2):
            coords=points[j*n:(j+1)*n];line('MF_173_boot_welt_'+side+'_'+str(j),coords+[coords[0]],mats['thread'],.008)
        # A shaft seam and small practical cuff fastening, not shiny jewellery.
        line('MF_173_boot_shaft_seam_'+side,[points[j*n+n//2] for j in range(6)],mats['thread'],.008)
        k=16 if sign==1 else 48
        cuff=Vector(points[n+k]);around=(Vector(points[n+(k+1)%n])-Vector(points[n+(k-1)%n])).normalized()
        down=(Vector(points[2*n+k])-cuff).normalized()
        fastening=[tuple(cuff+around*a+down*b) for a,b in [(-.075,.025),(.075,.025),(.075,.17),(-.075,.17),(-.075,.025)]]
        line('MF_173_boot_cuff_fastening_'+side,fastening,mats['metal'],.012)
        # Join the vamp to its upper on the evaluated boot, not floating raw
        # authoring rings that subdivision will subsequently move.
        from wardrobe_refinement import tree_for
        tree=tree_for(boot);vamp=[];j=heights.index(-12.82)
        for i in range(-n//4,n//4+1):
            a=math.tau*i/n;radial=matrices['foot'].to_3x3()@Vector((math.sin(a),-math.cos(a),0))
            hit,normal,_,_=tree.find_nearest(Vector(points[j*n+i%n])+radial*.06)
            vamp.append(tuple(hit+normal*.007))
        line('MF_173_boot_vamp_join_'+side,vamp,mats['thread'],.006)
        # A modest working heel below the existing footbed; body and contact
        # controls remain unchanged. This is not a new footwear animation rig.
        heel_y=max(p[1] for p in hull)
        heel_points=[tuple(matrices['foot']@Vector((bed_center[0]+x,heel_y+y,z)))
                     for z in (-13.43,-13.53) for y in (-.46,.025) for x in (-.32,.32)]
        heel=panel('MF_173_boot_working_heel_'+side,heel_points,
                   [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],mats['sole'],0,0)
        if not heel.modifiers:
            bevel=heel.modifiers.new('Soft worn heel edges','BEVEL');bevel.width=.035;bevel.segments=3

    if boots_only:
        return
    pants=bpy.data.objects['MF_fit_trousers_173_visible']
    from wardrobe_refinement import tree_for
    tree=tree_for(pants)
    rest_coords=pants.data.attributes['MF_173_material_coords'].data
    for side,sign in (('L',1),('R',-1)):
        seam=[]
        for j in range(48):
            z=-6.45-j/47*4.72
            sample=[i for i,item in enumerate(rest_coords) if item.vector.x*sign>0 and abs(item.vector.z-z)<.065]
            if not sample:continue
            i=max(sample,key=lambda idx:rest_coords[idx].vector.x*sign)
            v=pants.data.vertices[i];seam.append(v.co+v.normal*.050)
        for _ in range(3):seam=[p if i in (0,len(seam)-1) else seam[i-1]*.2+p*.6+seam[i+1]*.2 for i,p in enumerate(seam)]
        attached=[]
        for p in seam:
            hit,normal,_,_=tree.find_nearest(p);attached.append(tuple(hit+normal*.004))
        if len(attached)>8:line('MF_173_trouser_outseam_'+side,attached,mats['panel'],.006)

    # Under the scarf, a few functional cloth fastenings identify construction.
    from wardrobe_studio import torso_point
    from wardrobe_refinement import tree_for
    tunic=tree_for(bpy.data.objects['MF_fit_tunic_173_visible'])
    for i,z in enumerate((-3.92,-4.22,-4.52)):
        p=Vector((.10,-1.21,z));q=Vector((-.10,-1.21,z))
        positions=[]
        for point in (q,p):
            worldpoint=torso_point(point);hit,normal,_,_=tunic.find_nearest(worldpoint)
            positions.append(tuple(hit+normal*.027))
        line('MF_173_tunic_toggle_'+str(i),positions,mats['thread'],.023)
    bpy.context.view_layer.update()
