import pyprind
import util
from example import Example


def Make_feature_file(parse_dict, clauseArguments, feature_function_list, to_file, add_dimension=False):
    example_list = []
    dimension = 0

    process_bar = pyprind.ProgPercent(len(clauseArguments))
    for clauseArgument in clauseArguments:
        process_bar.update()

        for clause_index,clause in enumerate(clauseArgument.clauses):

            features = [feature_function(clause, clause_index, parse_dict) for feature_function in feature_function_list]
            #合并特征
            feature = util.mergeFeatures(features)
            dimension = feature.dimension
            #特征target
            target = clause.label
            if target is None:
                target = "-1"
            #example
            example = Example(target, feature)
            # comment
            example.comment = "%s|%s|%d|%s" % (clauseArgument.relationID, clauseArgument.DocID, clauseArgument.sent_index, " ".join(map(str, clause.clause_indices)))

            example_list.append(example)

    if add_dimension:
        util.write_example_list_to_file(example_list, "%s_%d" % (to_file, dimension))
    else:
        util.write_example_list_to_file(example_list, to_file)