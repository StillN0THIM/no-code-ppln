class FieldTransformers {
    static passthrough(values) {
        return { ...values };
    }

    static validation(values) {
        return {
            ...values,
            required_columns: values.required_columns
                ? values.required_columns.split(',').map((s) => s.trim()).filter(Boolean)
                : [],
        };
    }
}

const TRANSFORMERS = {
    dataset: FieldTransformers.passthrough,
    validation: FieldTransformers.validation,
    training: FieldTransformers.passthrough,
    evaluation: FieldTransformers.passthrough,
    registry: FieldTransformers.passthrough,
};

export class PipelineSerializer {
    static serialize({ pipelineId, name, nodes, edges }) {
        return {
            pipeline_id: pipelineId,
            name,
            nodes: nodes.map((node) => PipelineSerializer.serializeNode(node)),
            edges: edges.map((edge) => ({ source: edge.source, target: edge.target })),
        };
    }

    static serializeNode(node) {
        const transform = TRANSFORMERS[node.type] ?? FieldTransformers.passthrough;

        return {
            id: node.id,
            type: node.type,
            name: node.data.label,
            position: [node.position.x, node.position.y],
            ...transform(node.data.values),
        };
    }
}