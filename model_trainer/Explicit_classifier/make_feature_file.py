import pyprind
import util
from example import Example

def Make_feature_file(parse_dict, explicitRelations, feature_function_list, to_file, add_dimension=False):
    example_list = []
    dimension = 0

    process_bar = pyprind.ProgPercent(len(explicitRelations))
    for explicitRelation in explicitRelations:
        process_bar.update()

        features = [feature_function(parse_dict, explicitRelation.connective) for feature_function in feature_function_list]
        #合并特征
        feature = util.mergeFeatures(features)
        dimension = feature.dimension
        #特征target
        target = explicitRelation.SenseLabel
        if target is None:
            target = "-1"
        #example
        example = Example(target, feature)
        # comment
        connective = explicitRelation.connective
        conn_name = " ".join([parse_dict[connective.DocID]["sentences"][connective.sent_index]["words"][word_index][0] \
                              for word_index in connective.token_indices ])
        example.comment = "%s|%s|%s|%s|%s" % \
                          (explicitRelation.ID, conn_name, connective.DocID, str(connective.sent_index), " ".join(map(str, connective.token_indices)))

        example_list.append(example)

    if add_dimension:
        util.write_example_list_to_file(example_list, "%s_%d" % (to_file, dimension))
    else:
        util.write_example_list_to_file(example_list, to_file)