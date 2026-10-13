export class NodeDefinition {
    constructor({ type, label, fields, hasInput = true, hasOutput = true }) {
        this.type = type;
        this.label = label;
        this.fields = fields;
        this.hasInput = hasInput;
        this.hasOutput = hasOutput;
    }

    defaultValues() {
        return this.fields.reduce((values, field) => {
            values[field.key] = field.default ?? (field.type === 'number' ? 0 : '');
            return values;
        }, {});
    }
}

const DATASET = new NodeDefinition({
    type: 'dataset',
    label: 'Dataset',
    hasInput: false,
    fields: [
        { key: 'source_path', label: 'Source Path', type: 'text' },
        { key: 'target_column', label: 'Target Column', type: 'text' },
        { key: 'test_size', label: 'Test Size', type: 'number', default: 0.2 },
    ],
});

const VALIDATION = new NodeDefinition({
    type: 'validation',
    label: 'Validation',
    fields: [
        { key: 'required_columns', label: 'Required Columns (comma-separated)', type: 'text' },
        { key: 'null_threshold', label: 'Null Threshold', type: 'number', default: 0.05 },
    ],
});

const TRAINING = new NodeDefinition({
    type: 'training',
    label: 'Training',
    fields: [
        {
            key: 'algorithm',
            label: 'Algorithm',
            type: 'select',
            options: [
                'random_forest_classifier',
                'random_forest_regressor',
                'logistic_regression',
                'linear_regression',
            ],
        },
    ],
});

const EVALUATION = new NodeDefinition({
    type: 'evaluation',
    label: 'Evaluation',
    fields: [
        {
            key: 'metric',
            label: 'Metric',
            type: 'select',
            options: ['accuracy', 'f1', 'precision', 'recall', 'r2', 'mse', 'mae'],
        },
        { key: 'threshold', label: 'Threshold', type: 'number' },
    ],
});

const REGISTRY = new NodeDefinition({
    type: 'registry',
    label: 'Registry',
    hasOutput: false,
    fields: [
        { key: 'model_name', label: 'Model Name', type: 'text' },
        { key: 'stage', label: 'Stage', type: 'select', options: ['Staging', 'Production'], default: 'Staging' },
    ],
});

export const NODE_DEFINITIONS = {
    dataset: DATASET,
    validation: VALIDATION,
    training: TRAINING,
    evaluation: EVALUATION,
    registry: REGISTRY,
};