import { Handle, Position } from 'reactflow';

function FieldInput({ field, value, onChange }) {
    const handleChange = (event) => {
        const raw = event.target.value;
        const parsed = field.type === 'number' ? Number(raw) : raw;
        onChange(field.key, parsed);
    };

    if (field.type === 'select') {
        return (
            <select value={value ?? ''} onChange={handleChange}>
                {field.options.map((option) => (
                    <option key={option} value={option}>{option}</option>
                ))}
            </select>
        );
    }

    return (
        <input
            type={field.type === 'number' ? 'number' : 'text'}
            value={value ?? ''}
            onChange={handleChange}
            step={field.type === 'number' ? 'any' : undefined}
        />
    );
}

export default function BaseNode({ data }) {
    const { label, fields, values, onFieldChange, hasInput = true, hasOutput = true } = data;

    return (
        <div className="pipeline-node">
            {hasInput && <Handle type="target" position={Position.Top} />}

            <div className="pipeline-node__header">{label}</div>

            <div className="pipeline-node__body">
                {fields.map((field) => (
                    <label key={field.key} className="pipeline-node__field">
                        <span>{field.label}</span>
                        <FieldInput
                            field={field}
                            value={values[field.key]}
                            onChange={onFieldChange}
                        />
                    </label>
                ))}
            </div>

            {hasOutput && <Handle type="source" position={Position.Bottom} />}
        </div>
    );
}