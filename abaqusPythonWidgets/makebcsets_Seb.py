from abaqus import *
from abaqusConstants import *
from mesh import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from load import *
from job import *
from sketch import*
from interaction import *
from connectorBehavior import *
import regionToolset
import displayGroupMdbToolset as dgm
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
import sys

def find_normal(first, second, third):
    u1 = second[0] - first[0]
    u2 = second[1] - first[1]
    u3 = second[2] - first[2]
    v1 = third[0] - first[0]
    v2 = third[1] - first[1]
    v3 = third[2] - first[2]
    x_coeff = ((u2 * v3) - (u3 * v2))
    y_coeff = -1 * ((u1 * v3) - (u3 * v1))
    z_coeff = ((u1 * v2) - (u2 * v1))
    return x_coeff, y_coeff, z_coeff
 


def makebcsets(modelname, partname):
    
    print 'Identifying top and bottom nodes'
    nodes = mdb.models[modelname].parts[partname].nodes
    elements = mdb.models[modelname].parts[partname].elements
    zcoords = []
    znodelabel = []
    zcoordmax = 0
    zcoordmin = 0
    # Search through the models' nodes and write the z-coordinate for each into zcoords[]
    # and write the corresponding label into znodelabel[]. Find the minimum and maximum
    # z-coordinate and write them to zcoordmax and min.
    for x in nodes:
        zcoords.append(x.coordinates[2])
        znodelabel.append(x.label)
    
    zcoordmax = max(zcoords)
    zcoordmin = min(zcoords)
    # Search through zcoords[] for node z-coordinates within 0.1 of the maximum or minimum values
    # and write the corresponding node labels to topsetlabel[] and bottomsetlabel[].
    topsetlabel = []
    bottomsetlabel = []
    for x in range(0, (len(nodes))):
        if zcoords[x] >= (zcoordmax-0.1):
           topsetlabel.append(znodelabel[x])
        if zcoords[x] <= (zcoordmin+0.1):
           bottomsetlabel.append(znodelabel[x])
    # Search through all of the models' elements. For each, search through the elements'
    # connectivity, and for each connected node, search the list topsetlabel[] for a match.
    # If a match is found, increment a temporary counter by 1. Once all of the elements'
    # nodes has been checked against the contents of topsetlist[], if the temporary counter
    # is >= 4, add the element label to the list element_hitlist[].
    # The result of this, is that any elements within the model which share 4 or more nodes
    # with those identified as being on the top surface will be added to the list.
    
    print 'Identifying top surface elements'
    tet_hitlist=[]
    hex_hitlist=[]
    for i, elementrota in enumerate(elements):
        temp_count = 0
        connect_points = elementrota.connectivity
        for check_connect_points in connect_points:
            for check_topsetlabel in topsetlabel:
                if (check_connect_points+1) == check_topsetlabel:
                   temp_count += 1
                   break
        element_type = elementrota.type
        if element_type == C3D4:
           if temp_count == 3:
              tet_hitlist.append(i)
        if element_type == C3D8:
           if temp_count == 4:
              hex_hitlist.append(i)
    #
    # Now, cycle through tet_hitlist, and for each element, interrogate the faces.
    #
    
    face_one_hitlist = []
    face_two_hitlist = []
    face_three_hitlist = []
    face_four_hitlist = []
    face_five_hitlist = []
    face_six_hitlist = []
    neg_limit = -0.1
    pos_limit = 0.1
    
    print 'Identifying corresponding tet element faces and calculating normals'
    for i, check_tet in enumerate(tet_hitlist):
        print 'element ' , ( i + 1 ) , '/' , len(tet_hitlist)
        #
        # First, get the coordinates of the tet nodes
        #
        tet_node_zero = nodes[elements[check_tet].connectivity[0]].coordinates
        tet_node_one = nodes[elements[check_tet].connectivity[1]].coordinates
        tet_node_two = nodes[elements[check_tet].connectivity[2]].coordinates
        tet_node_three = nodes[elements[check_tet].connectivity[3]].coordinates
        #
        # Now, find the normals of each face. The order of the coordinates passed to the find_normal() function
        # determines the perpendicular direction in which we will get the normal. To make sure we get a face normal
        # which points 'out' of the element, the node coordinates need to be passed in the following order for each face:
        #
        # Face 1 - nodes [0], [2], [1]
        # Face 2 - nodes [0], [1], [3]
        # Face 3 - nodes [1], [2], [3]
        # Face 4 - nodes [0], [3], [2]
        #
        face_one_normal = find_normal(tet_node_zero, tet_node_two, tet_node_one)
        face_two_normal = find_normal(tet_node_zero, tet_node_one, tet_node_three)
        face_three_normal = find_normal(tet_node_one, tet_node_two, tet_node_three)
        face_four_normal = find_normal(tet_node_zero, tet_node_three, tet_node_two)
        if ( face_one_normal[0] > neg_limit ) and ( face_one_normal[0] < pos_limit ) and ( face_one_normal[1] > neg_limit ) and ( face_one_normal[1] < pos_limit ) and face_one_normal[2] > 0:
           face_one_hitlist.append(elements[check_tet].label)
        if ( face_two_normal[0] > neg_limit ) and ( face_two_normal[0] < pos_limit ) and ( face_two_normal[1] > neg_limit ) and ( face_two_normal[1] < pos_limit ) and face_two_normal[2] > 0:
           face_two_hitlist.append(elements[check_tet].label)
        if ( face_three_normal[0] > neg_limit ) and ( face_three_normal[0] < pos_limit ) and ( face_three_normal[1] > neg_limit ) and ( face_three_normal[1] < pos_limit ) and face_three_normal[2] > 0:
           face_three_hitlist.append(elements[check_tet].label)
        if ( face_four_normal[0] > neg_limit ) and ( face_four_normal[0] < pos_limit ) and ( face_four_normal[1] > neg_limit ) and ( face_four_normal[1] < pos_limit ) and face_four_normal[2] > 0:
           face_four_hitlist.append(elements[check_tet].label)
    
    print 'Identifying corresponding hex element faces and calculating normals'
    for j, check_hex in enumerate(hex_hitlist):
        print 'element ' , ( j + 1 ) , '/' , len(hex_hitlist)
        hex_node_zero = nodes[elements[check_hex].connectivity[0]].coordinates
        hex_node_one = nodes[elements[check_hex].connectivity[1]].coordinates
        hex_node_two = nodes[elements[check_hex].connectivity[2]].coordinates
        hex_node_three = nodes[elements[check_hex].connectivity[3]].coordinates
        hex_node_four = nodes[elements[check_hex].connectivity[4]].coordinates
        hex_node_five = nodes[elements[check_hex].connectivity[5]].coordinates
        hex_node_six = nodes[elements[check_hex].connectivity[6]].coordinates
        hex_node_seven = nodes[elements[check_hex].connectivity[7]].coordinates
        face_one_normal = find_normal(hex_node_zero, hex_node_three, hex_node_two)
        face_two_normal = find_normal(hex_node_four, hex_node_five, hex_node_six)
        face_three_normal = find_normal(hex_node_zero, hex_node_one, hex_node_five)
        face_four_normal = find_normal(hex_node_one, hex_node_two, hex_node_six)
        face_five_normal = find_normal(hex_node_two, hex_node_three, hex_node_seven)
        face_six_normal = find_normal(hex_node_zero, hex_node_four, hex_node_seven)
        if ( face_one_normal[0] > neg_limit ) and ( face_one_normal[0] < pos_limit ) and ( face_one_normal[1] > neg_limit ) and ( face_one_normal[1] < pos_limit ) and face_one_normal[2] > 0:
           face_one_hitlist.append(elements[check_hex].label)
        if ( face_two_normal[0] > neg_limit ) and ( face_two_normal[0] < pos_limit ) and ( face_two_normal[1] > neg_limit ) and ( face_two_normal[1] < pos_limit ) and face_two_normal[2] > 0:
           face_two_hitlist.append(elements[check_hex].label)
        if ( face_three_normal[0] > neg_limit ) and ( face_three_normal[0] < pos_limit ) and ( face_three_normal[1] > neg_limit ) and ( face_three_normal[1] < pos_limit ) and face_three_normal[2] > 0:
           face_three_hitlist.append(elements[check_hex].label)
        if ( face_four_normal[0] > neg_limit ) and ( face_four_normal[0] < pos_limit ) and ( face_four_normal[1] > neg_limit ) and ( face_four_normal[1] < pos_limit ) and face_four_normal[2] > 0:
           face_four_hitlist.append(elements[check_hex].label)
        if ( face_five_normal[0] > neg_limit ) and ( face_five_normal[0] < pos_limit ) and ( face_five_normal[1] > neg_limit ) and ( face_five_normal[1] < pos_limit ) and face_five_normal[2] > 0:
           face_five_hitlist.append(elements[check_hex].label)
        if ( face_six_normal[0] > neg_limit ) and ( face_six_normal[0] < pos_limit ) and ( face_six_normal[1] > neg_limit ) and ( face_six_normal[1] < pos_limit ) and face_six_normal[2] > 0:
           face_six_hitlist.append(elements[check_hex].label)
    
    face_one = elements.sequenceFromLabels(face_one_hitlist)
    face_two = elements.sequenceFromLabels(face_two_hitlist)
    face_three = elements.sequenceFromLabels(face_three_hitlist)
    face_four = elements.sequenceFromLabels(face_four_hitlist)
    face_five = elements.sequenceFromLabels(face_five_hitlist)
    face_six = elements.sequenceFromLabels(face_six_hitlist)
    print 'Generating surface'
    mdb.models[modelname].parts[partname].Surface(face1Elements=face_one, face2Elements=face_two, face3Elements=face_three, face4Elements=face_four, face5Elements=face_five, face6Elements=face_six, name='top_face')
    
    print 'Generating node sets'
    topset_nodes = nodes.sequenceFromLabels(topsetlabel)
    mdb.models[modelname].parts[partname].Set(nodes=topset_nodes, name='top_nodes')
    
    bottomset_nodes = nodes.sequenceFromLabels(bottomsetlabel)
    mdb.models[modelname].parts[partname].Set(nodes=bottomset_nodes, name='bottom_nodes')
