import pyprind
import util
from example import Example


def Make_feature_file(parse_dict, connectives, feature_function_list, to_file, add_dimension=False):
    example_list = []
    dimension = 0

    process_bar = pyprind.ProgPercent(len(connectives))
    for connective in connectives:
        process_bar.update()

        features = [feature_function(parse_dict, connective.DocID, connective.sent_index,connective.token_indices) for feature_function in feature_function_list]
        #合并特征
        feature = util.mergeFeatures(features)
        dimension = feature.dimension
        #特征target
        target = connective.label
        if target is None:
            target = "-1"
        #example
        example = Example(target, feature)
        # comment
        conn_name = " ".join([parse_dict[connective.DocID]["sentences"][connective.sent_index]["words"][word_index][0] \
                              for word_index in connective.token_indices ])
        example.comment = "%s|%s|%s|%s" % \
                          (conn_name, connective.DocID, str(connective.sent_index), " ".join(map(str, connective.token_indices)))

        example_list.append(example)

    if add_dimension:
        util.write_example_list_to_file(example_list, "%s_%d" % (to_file, dimension))
    else:
        util.write_example_list_to_file(example_list, to_file)