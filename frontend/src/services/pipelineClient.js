import axios from 'axios';

export class PipelineClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.http = axios.create({ baseURL });
    }

    async run(pipelineConfig) {
        try {
            const response = await this.http.post('/pipelines/run', pipelineConfig);
            return response.data;
        } catch (error) {
            throw PipelineClient.toClientError(error);
        }
    }

    static toClientError(error) {
        if (error.response) {
            const detail = error.response.data?.detail ?? error.response.statusText;
            return new Error(`Pipeline run failed (${error.response.status}): ${detail}`);
        }
        if (error.request) {
            return new Error('No response from backend — is the FastAPI server running?');
        }
        return new Error(error.message);
    }
}