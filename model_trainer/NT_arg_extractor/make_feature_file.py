import pyprind
import util
from example import Example

def Make_feature_file(parse_dict, constituentArguments, feature_function_list, to_file, add_dimension=False):
    example_list = []
    dimension = 0

    process_bar = pyprind.ProgPercent(len(constituentArguments))
    for constituentArgument in constituentArguments:
        process_bar.update()

        for constituent in constituentArgument.constituents:

            features = [feature_function(parse_dict, constituent,i,constituentArgument.constituents) for i,feature_function in enumerate(feature_function_list)]
            #合并特征
            feature = util.mergeFeatures(features)
            dimension = feature.dimension
            #特征target
            target = constituent.label
            if target is None:
                target = "-1"
            #example
            example = Example(target, feature)
            # comment
            example.comment = "%s|%s|%s|%s" % \
                              (constituentArgument.relationID,
                               constituentArgument.DocID,
                               constituentArgument.sent_index,
                               " ".join(map(str, constituent.indices))
            )

            example_list.append(example)

    if add_dimension:
        util.write_example_list_to_file(example_list, "%s_%d" % (to_file, dimension))
    else:
        util.write_example_list_to_file(example_list, to_file)