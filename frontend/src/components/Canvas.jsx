import { useCallback, useMemo, useState } from 'react';
import ReactFlow, {
    addEdge,
    Background,
    Controls,
    useEdgesState,
    useNodesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

import BaseNode from './nodes/BaseNode';
import { NODE_DEFINITIONS } from './nodes/nodeDefinitions';
import { PipelineSerializer } from '../services/pipelineSerializer';
import { PipelineClient } from '../services/pipelineClient';

const NODE_TYPES = Object.keys(NODE_DEFINITIONS).reduce((acc, type) => {
    acc[type] = BaseNode;
    return acc;
}, {});

let nodeIdCounter = 0;
function nextNodeId() {
    nodeIdCounter += 1;
    return `node_${nodeIdCounter}`;
}

export default function Canvas() {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [runResult, setRunResult] = useState(null);
    const [isRunning, setIsRunning] = useState(false);

    const onConnect = useCallback(
        (connection) => setEdges((current) => addEdge(connection, current)),
        [setEdges],
    );

    const handleFieldChange = useCallback(
        (nodeId, key, value) => {
            setNodes((current) =>
                current.map((node) =>
                    node.id === nodeId
                        ? { ...node, data: { ...node.data, values: { ...node.data.values, [key]: value } } }
                        : node,
                ),
            );
        },
        [setNodes],
    );

    const addNode = useCallback(
        (type) => {
            const definition = NODE_DEFINITIONS[type];
            const id = nextNodeId();
            const position = { x: 100 + nodes.length * 220, y: 100 };

            setNodes((current) => [
                ...current,
                {
                    id,
                    type,
                    position,
                    data: {
                        label: definition.label,
                        fields: definition.fields,
                        values: definition.defaultValues(),
                        hasInput: definition.hasInput,
                        hasOutput: definition.hasOutput,
                        onFieldChange: (key, value) => handleFieldChange(id, key, value),
                    },
                },
            ]);
        },
        [nodes.length, setNodes, handleFieldChange],
    );

    const client = useMemo(() => new PipelineClient(), []);

    const runPipeline = useCallback(async () => {
        const config = PipelineSerializer.serialize({
            pipelineId: 'pipeline_1',
            name: 'My Pipeline',
            nodes,
            edges,
        });

        setIsRunning(true);
        try {
            const result = await client.run(config);
            setRunResult(result);
        } catch (error) {
            setRunResult({ error: error.message });
        } finally {
            setIsRunning(false);
        }
    }, [nodes, edges, client]);

    return (
        <div className="canvas-layout">
            <aside className="canvas-sidebar">
                {Object.values(NODE_DEFINITIONS).map((definition) => (
                    <button key={definition.type} onClick={() => addNode(definition.type)}>
                        + {definition.label}
                    </button>
                ))}
                <button onClick={runPipeline} disabled={isRunning}>
                    {isRunning ? 'Running...' : 'Run Pipeline'}
                </button>
            </aside>

            <div className="canvas-flow">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    nodeTypes={NODE_TYPES}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                >
                    <Background />
                    <Controls />
                </ReactFlow>
            </div>

            {runResult && <pre className="canvas-result">{JSON.stringify(runResult, null, 2)}</pre>}
        </div>
    );
}