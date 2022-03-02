# import pyprind
import util
from example import Example
import pyprind

def Make_feature_file(parse_dict, nonExplicitRelations, feature_function_list, to_file, add_dimension=False):
    example_list = []
    dimension = 0

    process_bar = pyprind.ProgPercent(len(nonExplicitRelations))
    for nonExplicitRelation in nonExplicitRelations:
        process_bar.update()
        relation_dict = {}

        relation_dict["ID"] = nonExplicitRelation.ID
        relation_dict["DocID"] = nonExplicitRelation.DocID
        relation_dict["Arg1"] = {}
        relation_dict["Arg2"] = {}
        relation_dict["Arg1"]["TokenList"] = nonExplicitRelation.Arg1_TokenList
        relation_dict["Arg2"]["TokenList"] = nonExplicitRelation.Arg2_TokenList
        relation_dict["Sense"] = nonExplicitRelation.Sense
        relation_dict["SenseLabel"] = nonExplicitRelation.SenseLabel

        features = [feature_function(relation_dict, parse_dict) for feature_function in feature_function_list]
        #合并特征
        feature = util.mergeFeatures(features)
        dimension = feature.dimension
        #特征target
        target = nonExplicitRelation.SenseLabel
        if target is None:
                target = "-1"
        #example
        example = Example(target, feature)
        # comment
        example.comment = "%s" % \
                          (nonExplicitRelation.ID)

        example_list.append(example)

    if add_dimension:
        util.write_example_list_to_file(example_list, "%s_%d" % (to_file, dimension))
    else:
        util.write_example_list_to_file(example_list, to_file)