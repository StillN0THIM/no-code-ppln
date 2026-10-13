import Canvas from '../components/Canvas';

export default function PipelineBuilderPage() {
    return (
        <div className="pipeline-builder-page">
            <header className="pipeline-builder-page__header">
                <h1>No-Code MLOps Platform</h1>
            </header>

            <main className="pipeline-builder-page__main">
                <Canvas />
            </main>
        </div>
    );
}